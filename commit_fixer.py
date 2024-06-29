import os

import git
from dotenv import load_dotenv
from langchain.llms import Anthropic, OpenAI
from langchain.prompts import ChatPromptTemplate

ALLOWED_MANAGERS = {"anthropic": lambda k: Anthropic(anthropic_api_key=k), "openai": lambda k: OpenAI(openai_api_key=k)}


def get_llm_manager():
    llm_manager_type = os.environ["LLM_MANAGER"]
    assert llm_manager_type in ALLOWED_MANAGERS, f"Unrecognized manager `{llm_manager_type}`"
    llm_key = os.environ["LLM_KEY"]

    # Initialize the LLM providers
    llm_manager = ALLOWED_MANAGERS[llm_manager_type](llm_key)
    return llm_manager


# Function to get diff of a commit
def get_commit_diff(repo, commit):
    diffs = commit.diff(commit.parents[0], create_patch=True) if commit.parents else commit.diff(None, create_patch=True)
    diff_text = '\n'.join(d.diff.decode('utf-8') for d in diffs)
    return diff_text


def generate_summary(commit_message):
    llm_manager = get_llm_manager()
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", f"Summarize the following set of changes into a commit description."),
            ("human", f"{commit_message}")]

    )
    response = prompt.execute()
    return response['text'].strip()


def get_user_input(prompt_text):
    return input(prompt_text)


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


def runner(repo_path: str = "."):
    # Get commits to be pushed
    repo = git.Repo(repo_path)
    commits = get_commits_to_push(repo)

    for commit in commits:
        original_message = commit.message

        print(f"Commit: {original_message}")
        user_choice = get_user_input("Choose an option: (1) Keep as is, (2) Generate summary: ")

        if user_choice == '1':
            continue
        elif user_choice == '2':
            commit_diff = get_commit_diff(repo, commit)
            summary = generate_summary(commit_diff)
            print(f"Generated Summary: {summary}")

            final_title = get_user_input("Enter the final title: ")
            final_content = get_user_input("Enter the final content: ")

            confirmation = get_user_input("Do you want to update this commit? (yes/no): ")
            if confirmation.lower() == 'yes':
                new_message = f"{final_title}\n\n{final_content}"

                # Amend the commit message
                repo.git.commit('--amend', '-m', new_message, '--no-edit', '--author', commit.author)


if __name__ == "__main__":
    load_dotenv()
    runner()
