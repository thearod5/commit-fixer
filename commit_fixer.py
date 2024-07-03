import json
import os
import sys
from typing import List

from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain_community.llms import OpenAI
from safa.safa_client import Safa
from safa.safa_store import SafaStore

ALLOWED_MANAGERS = {
    "anthropic": lambda k: ChatAnthropic(anthropic_api_key=k, model_name='claude-3-sonnet-20240229'),
    "openai": lambda k: OpenAI(openai_api_key=k)
}
INSTRUCTIONS_PROMPT = (
    "Produce the JSON output to summarize the given commit changes. "
    "Each diff should be converted to natural language. "
    "Each change should group the diffs into a behavioral change."
)

SUMMARIZE_FORMAT_JSON = {
    "diffs": ["diff desc 1", "diff desc 2"]
}

SYNTHESIZE_FORMAT_JSON = {
    "changes": ["change desc 1", "change desc 2"],
    "title": "commit title"
}


def run_menu(state: Dict, menu: Dict[str, Callable]):
    commit = state["commit"]
    title, changes = split_commit_message(commit.message)
    print_commit("Commit", title, changes=changes)
    selected_key = get_menu_option(menu.keys())
    menu_action = menu[selected_key]
    menu_action(state)


def get_format_prompt() -> str:
    """
    Generates prompt displaying the expected format of the json response.
    :return: Format prompt as string.
    """
    example_json_str = json.dumps(EXAMPLE_JSON, indent=4)
    return f"Output valid json like so:\n```json\n{example_json_str}\n```"


def generate_commit_summary(state: Dict):
    repo = state["repo"]
    commit = state["commit"]
    safa_client = state["safa_client"]

    commit_diff = get_commit_diff(repo, commit)
    title, changes = generate_summary(commit_diff)
    print_commit("Generated", title, changes=changes)
    # Next
    run_menu(state, MAIN_MENU)


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
        edit_change = get_yn(change, title="\nEdit/Delete this change?")

        if edit_change:
            new_change_desc = input("New Change (empty for remove):")
            if new_change_desc == "":
                print("Removed.")
                continue
            changes_kept.append(new_change_desc)
        else:
            changes_kept.append(change)
            print("Keeping as is.")
    # Next
    state["message"] = combine_commit_message(title, changes_kept)
    op_amend(state)
    run_menu(state, MAIN_MENU)
    print("Changes have been saved.\n\n")


def get_yn(p: str, title: str = None):
    if title:
        print(title, "\n")

    print(p)
    answer = input("\n(y/n) >")
    valid_answers = {"y", "n"}
    if answer not in valid_answers:
        return get_yn(p, title=title)
    return answer == "y"


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
        ("human", commit_diff)
    ]).content
    start_index = response.find("```json")
    end_index = response.find("```", start_index + 1)
    json_str = response[start_index + 7:end_index]
    try:
        json_dict = json.loads(json_str)
        change_summaries = json_dict["changes"]
        return change_to_message(change_summaries)
    except Exception as e:
        print(response)
        raise e


def get_llm_manager():
    """
    Reads LLM manager from env variables.
    :return:
    """
    llm_manager_type = os.environ["LLM_MANAGER"]
    assert llm_manager_type in ALLOWED_MANAGERS, f"Unrecognized manager `{llm_manager_type}`"
    llm_key = os.environ["LLM_KEY"]

    # Initialize the LLM providers
    llm_manager = ALLOWED_MANAGERS[llm_manager_type](llm_key)
    return llm_manager


def change_to_message(change_messages: List[str]):
    """
    Formats list of changes as a Markdown list.
    :param change_messages: List of diff summaries.
    :return: String delimited changes as a Markdown list.
    """
    content = '\n'.join(["- " + c for c in change_messages])
    return content


def get_staged_diffs(repo):
    """
    Get the staged diffs using Git.
    """
    staged_files = [item.a_path for item in repo.index.diff("HEAD")]

    diffs = []
    for file in staged_files:
        diff = repo.git.diff('HEAD', file)
        diffs.append(diff)

    return diffs


if __name__ == "__main__":
    MAIN_MENU = {
        "Generate": generate_commit_summary,
        "Edit Title": edit_title,
        "Edit Changes": edit_changes,
        "Keep as is": lambda s: None
    }
    repo_path: str = "."
    load_dotenv()

    email = os.environ["SAFA_EMAIL"]
    password = os.environ["SAFA_PASSWORD"]
    version_id = os.environ["SAFA_VERSION_ID"]

    CACHE_FILE_PATH = os.path.expanduser("~/projects/commit-fixer/local.cache")
    client_store = SafaStore(CACHE_FILE_PATH)
    client = Safa(client_store)
    client.login(email, password)
    project_data = client.get_project_data(version_id)

    r = git.Repo(repo_path)
    diffs = get_staged_diffs(r)

    commit_state = {
        "repo": r,
        "commit": c,
        "message": c.message,
        "safa_client": client,
        "version_id": version_id
    }
    run_menu(commit_state, MAIN_MENU)
