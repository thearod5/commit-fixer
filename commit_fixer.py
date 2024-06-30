import json
import os

import git
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain_community.llms import OpenAI

ALLOWED_MANAGERS = {
    "anthropic": lambda k: ChatAnthropic(anthropic_api_key=k, model_name='claude-3-sonnet-20240229'),
    "openai": lambda k: OpenAI(openai_api_key=k)
}
INSTRUCTIONS_PROMPT = (
    "Produce the JSON output to summarize the given commit changes. "
    "Each diff should be converted to natural language. "
    "Each change should group the diffs into a behavioral change."
    "The title should describe what the changes ultimately accomplish."
)
FORMAT_PROMPT = (
    "Output only valid json like so:\n\n"
    "```json\n"
    "{\n"
    "\t\"diffs\": [\"diff desc 1\", \"diff desc 2\"],\n"
    "\t\"changes\": [\"change desc 1\", \"change desc 2\"],\n"
    "\t\"title\": \"commit title\""
    "\n}"
    "\n```"
)


def runner(repo_path: str = "."):
    # Get commits to be pushed
    repo = git.Repo(repo_path)
    commits = get_commits_to_push(repo)

    for commit in commits:
        title, content = split_commit_message(commit.message)
        print_commit("Commit", title, content)

        user_choice = input("Choose an option: (1) Keep as is, (2) Generate summary: ")

        if user_choice == '1':
            continue
        elif user_choice == '2':
            redo_commit(commit, repo)


def redo_commit(commit, repo):
    commit_diff = get_commit_diff(repo, commit)
    title, content = generate_summary(commit_diff)
    print_commit("Generated", title, content)
    title = input("Final title:")
    confirmation = input("Do you want to update this commit? (y/n): ")
    if confirmation.lower() == 'y':
        new_message = f"{title}\n\n{content}"

        # Amend the commit message
        repo.git.commit('--amend', '-m', new_message, '--no-edit', '--author', commit.author)


def get_llm_manager():
    llm_manager_type = os.environ["LLM_MANAGER"]
    assert llm_manager_type in ALLOWED_MANAGERS, f"Unrecognized manager `{llm_manager_type}`"
    llm_key = os.environ["LLM_KEY"]

    # Initialize the LLM providers
    llm_manager = ALLOWED_MANAGERS[llm_manager_type](llm_key)
    return llm_manager


# Function to get diff of a commit
def get_commit_diff(repo, commit):
    diffs = commit.parents[0].diff(commit, create_patch=True) if commit.parents else commit.diff(None, create_patch=True)
    diff_text = '\n'.join(d.diff.decode('utf-8') for d in diffs)
    return diff_text


def generate_summary(commit_message):
    system_prompt = "\n\n".join([INSTRUCTIONS_PROMPT, FORMAT_PROMPT])
    llm_manager = get_llm_manager()
    response = llm_manager.invoke([
        ("system", system_prompt),
        ("human", commit_message)
    ]).content
    start_index = response.find("```json")
    end_index = response.find("```", start_index + 1)
    json_str = response[start_index + 7:end_index]
    try:
        json_dict = json.loads(json_str)
    except Exception as e:
        print(response)
        raise e
    title = json_dict["title"]
    content = "\n".join(["- " + c for c in json_dict["changes"]]).strip()
    return title, content


def get_commits_to_push(repo, branch_name='main'):
    # Fetch the latest changes from the remote
    repo.remotes.origin.fetch()

    # Get the local branch and the corresponding remote branch
    local_branch = repo.branches[branch_name]
    remote_branch = repo.remotes.origin.refs[branch_name]

    # Compare the local branch with the remote branch to find new commits
    commit_filter = f'{remote_branch.commit.hexsha}..{local_branch.commit.hexsha}'
    commits_to_push = list(repo.iter_commits(commit_filter))

    return commits_to_push


def split_commit_message(commit_message):
    title, *content = commit_message.split("\n\n")
    content = "\n\n".join(content)
    return title, content


def print_commit(id_name: str, title: str, content: str):
    print("-" * 25, id_name, "-" * 25)
    print("Title:", title)
    print(content)
    print("-" * 50)


if __name__ == "__main__":
    load_dotenv()
    runner()
