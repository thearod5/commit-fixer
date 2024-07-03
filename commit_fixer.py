import json
import os
import sys
from typing import Dict, List, Tuple

import git
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain_community.llms import OpenAI
from safa.safa_client import Safa
from safa.safa_store import SafaStore

ALLOWED_MANAGERS = {
    "anthropic": lambda k: ChatAnthropic(anthropic_api_key=k, model_name='claude-3-sonnet-20240229'),
    "openai": lambda k: OpenAI(openai_api_key=k)
}
TITLE_INSTRUCTIONS = (
    "Create title describing how the code is changing."
)

TITLE_FORMAT = {
    "title": "commit title"
}

SUMMARIZE_INSTRUCTIONS = (
    "The user will present a file from their software project. "
    "This file has been modified and its your job to describe how the system is changing. "
    "Each file changed will also contain a summary of what it used to accomplish in the system and "
    "your job is to describe how it is changing. "
    "Produce JSON describing each file level change followed by a title of the overall set of changes.."
)

SUMMARIZE_FORMAT = {
    "changes": ["change desc 1", "change desc 2"],
    "title": "commit title"
}


def generate_diff_summary(changes):
    prompt = create_change_prompt(changes)
    system_prompt = "\n\n".join([SUMMARIZE_INSTRUCTIONS, get_format_prompt(SUMMARIZE_FORMAT)])
    messages = [
        ("system", system_prompt),
        ("human", prompt)
    ]
    print("...generating...")
    response_json = generate_json(messages)
    diff_summaries = response_json["changes"]
    title = response_json["title"]
    return title, diff_summaries


def create_change_prompt(changes: List[Dict]) -> str:
    prompt = ""

    for change in changes:
        change_prompt = []
        change_prompt.append(f"# File: {change['file']}")
        change_prompt.append(f"## Functionality before change\n{change['summary']}")
        change_prompt.append(f"## Changes\n{change['diff']}")
        prompt += "\n\n".join(change_prompt)

    return prompt


def generate_json(messages: List[Tuple]):
    llm_manager = get_llm_manager()
    response = llm_manager.invoke(messages).content
    start_index = response.find("```json")
    end_index = response.find("```", start_index + 1)
    json_str = response[start_index + 7:end_index]
    try:
        return json.loads(json_str)
    except Exception as e:
        print(response)
        raise e


def get_format_prompt(example_json) -> str:
    """
    Generates prompt displaying the expected format of the json response.
    :return: Format prompt as string.
    """
    example_json_str = json.dumps(example_json, indent=4)
    return f"Output valid json like so:\n```json\n{example_json_str}\n```"


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


def changes_to_message(change_messages: List[str]):
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

    file2diff = {}
    for file in staged_files:
        diff = repo.git.diff('HEAD', file)
        file2diff[file] = diff

    return file2diff


def create_artifact_map(artifacts: List[Dict]):
    artifact_map = {}
    for artifact in artifacts:
        artifact_map[artifact["name"]] = artifact
    return artifact_map


def to_commit_message(title, changes):
    return f"{title}\n\n{changes_to_message(changes)}"


def print_commit_message(title, changes):
    print(to_commit_message(title, changes))


if __name__ == "__main__":

    repo_path: str = "."
    load_dotenv()

    email = os.environ["SAFA_EMAIL"]
    password = os.environ["SAFA_PASSWORD"]
    version_id = os.environ["SAFA_VERSION_ID"]
    cache_file_path = os.environ["CACHE_FILE_PATH"]

    client_store = SafaStore(os.path.expanduser(cache_file_path))
    client = Safa(client_store)
    client.login(email, password)
    project_data = client.get_project_data(version_id)
    artifact_map = create_artifact_map(project_data["artifacts"])

    repo = git.Repo(repo_path)
    file2diff = get_staged_diffs(repo)
    if len(file2diff) == 0:
        print("No changes staged for commit.")
        sys.exit(0)

    changes = []
    for file, diff in file2diff.items():
        file_artifact = artifact_map[file]
        changes.append({
            "file": file,
            "diff": diff,
            "summary": file_artifact["summary"] if file_artifact["summary"] != "" else file_artifact["content"]
        })

    title, changes = generate_diff_summary(changes)

    menu_options = ["Edit title", "Edit changes", "Add change", "Commit"]
    running = True

    while running:
        print_commit_message(title, changes)
        for i, menu_option in enumerate(menu_options):
            print(f"{i + 1})", menu_option)
        option = input(">")
        option_num = int(option)

        if option_num == 1:
            title = input("New Title:")
        elif option_num == 2:
            change_num = int(input("Change Number"))
            changes[change_num - 1] = input("New Change:")
        elif option_num == 3:
            changes.append(input("New Change:"))
        elif option_num == 4:
            repo.index.commit(to_commit_message(title, changes))
            running = False
        else:
            raise Exception("Invalid option")

    print("Done.")
