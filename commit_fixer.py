import json
import os
from typing import Callable, Dict, List, Tuple, Union

import git
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain_community.llms import OpenAI

LINE_LENGTH = 90
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


def run_menu(state: Dict, menu: Dict[str, Callable]):
    commit = state["commit"]
    title, changes = split_commit_message(commit.message)
    print_commit("Commit", title, changes=changes)
    selected_key = get_menu_option(menu.keys())
    menu_action = menu[selected_key]
    menu_action(state)


def get_menu_option(menu_keys):
    index2item = {i: k for i, k in enumerate(menu_keys)}
    display_message = "\n".join([f"{i + 1}) {k}" for i, k in index2item.items()])
    print(display_message)
    user_index = int(input("User >")) - 1

    if user_index not in index2item:
        print(f"{user_index} not in {index2item}")
        return get_menu_option(menu_keys)

    return index2item[user_index]


"""
Actions
---
- Edit title
- Edit changes
- Generated


"""


def generate_commit_summary(state: Dict):
    repo = state["repo"]
    commit = state["commit"]
    commit_diff = get_commit_diff(repo, commit)
    title, changes = generate_summary(commit_diff)
    print_commit("Generated", title, changes=changes)
    # Next
    state["message"] = combine_commit_message(title, changes)
    run_menu(state, {**MAIN_MENU, "save": lambda s: op_amend(s)})


def edit_title(state: Dict):
    commit_message = state["message"]
    title, changes = split_commit_message(commit_message)
    new_title = input("New Title > ")
    if new_title == "":
        print("Skipped")
        return None
    # Next
    state["message"] = combine_commit_message(new_title, changes)
    op_amend(state)
    run_menu(state, MAIN_MENU)


def edit_changes(state: Dict):
    commit_message = state["message"]
    title, changes = split_commit_message(commit_message)
    changes_kept = []
    for change in changes:
        print("-" * LINE_LENGTH)
        commit_action = get_user_option(change, {"continue": "c", "edit": "e", "delete": "d"})

        if commit_action == "e":
            new_change_desc = input("New Change:")
            changes_kept.append(new_change_desc)
            print("Updated.")
        elif commit_action == "d":
            print("Removed.")
            continue
        elif commit_action == "c":
            changes_kept.append(change)
            print("Keeping as is.")
        else:
            raise ValueError("Option not recognized.")
    # Next
    state["message"] = combine_commit_message(title, changes_kept)
    op_amend(state)
    run_menu(state, MAIN_MENU)
    print("Changes have been saved.\n\n")


def get_user_option(p: str, answers: Union[Dict, List], title: str = None):
    if answers is None:
        answers = ["y", "n"]

    print(p)
    if isinstance(answers, list):
        options_display = f"({'/'.join(answers)})"
    elif isinstance(answers, dict):
        options_display1 = f"{'/'.join(answers.keys())}"
        options_display2 = f"({'/'.join(answers.values())})"
        options_display = f"{options_display1} {options_display2}"
        answers = [v for k, v in answers.items()]
    else:
        raise Exception("Expected list or dict but got: {}".format(answers))
    answer = input(f"\n({options_display} >")
    if answer not in answers:
        return get_user_option(p, answers, title=title)
    return answer


def split_commit_message(commit_message: str) -> Tuple[str, List[str]]:
    commit_title, *commit_changes = commit_message.split("\n\n")
    if len(commit_changes) > 0:
        commit_changes = [c.replace("- ", "") for c in commit_changes[0].split("\n") if len(c) > 0]
    return commit_title, commit_changes


def combine_commit_message(title: str, changes: List[str]) -> str:
    content = change_to_message(changes)
    if content == "":
        return title
    return f"{title}\n\n{content}"


"""
Operations
- Amend
- Continue
---
"""


def op_amend(state):
    if "message" not in state:
        return
    repo = state["repo"]
    commit = state["commit"]
    commit_message = state["message"]
    repo.git.commit('--amend', '-m', commit_message, '--no-edit', '--author', commit.author)


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
    return title, json_dict["changes"]


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


def print_commit(id_name: str, title: str, content: str = None, changes: List[str] = None):
    if changes:
        content = change_to_message(changes)
    bar_length = ((LINE_LENGTH - len(id_name)) // 2) - 1  # 2 spaces
    print("-" * bar_length, id_name, "-" * bar_length)
    print("Title:", title)
    print(content)
    print("-" * LINE_LENGTH)


def change_to_message(changes):
    content = '\n'.join(["- " + c for c in changes])
    return content


def edit_commit_message(commit):
    print(f"\nCurrent commit message:\n{commit.message}")
    new_message = input("Enter new commit message (leave empty to keep current): ").strip()
    return new_message if new_message else commit.message


def rebase_commits(repo, commits):
    # Temporarily checkout each commit, amend the message, and move HEAD
    head = repo.head.commit
    index = repo.index

    for commit in commits:
        print(f"Rebasing commit {commit.hexsha}")
        new_message = edit_commit_message(commit)

        # Create a new commit with the same tree and parent but new message
        new_commit = repo.Commit.create_from_tree(
            repo,
            tree=commit.tree,
            message=new_message,
            parent_commits=commit.parents,
            author=commit.author,
            committer=commit.committer
        )

        # Move the branch pointer to the new commit
        repo.git.rebase('--onto', new_commit.hexsha, commit.hexsha, 'HEAD')

        # Update HEAD to point to the new commit
        repo.head.reference = new_commit
        index.write()

    # Reset HEAD to original commit
    repo.head.reference = head
    index.write()
    print("Rebase completed.")


def llm_rename(commits):
    for c in commits:
        commit_state = {
            "repo": r,
            "commit": c,
            "message": c.message
        }
        run_menu(commit_state, MAIN_MENU)


if __name__ == "__main__":
    MAIN_MENU = {
        "Generate": generate_commit_summary,
        "Edit Title": edit_title,
        "Edit Changes": edit_changes,
        "Keep as is": lambda s: None
    }
    repo_path: str = "."
    load_dotenv()
    r = git.Repo(repo_path)
    r_commits = get_commits_to_push(r)
    rebase_commits(r, r_commits)
    # llm_rename(r_commits)
