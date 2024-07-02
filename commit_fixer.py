import json
import os
import sys
from typing import Callable, Dict

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


def change_to_message(changes):
    content = '\n'.join(["- " + c for c in changes])
    return content


def read_file(f_path):
    with open(f_path, 'r') as file:
        diffs = file.read()
        return diffs


if __name__ == "__main__":
    load_dotenv()
    diff_file = sys.argv[1]
    diffs = read_file(diff_file)
    if len(diffs.strip()) == 0:
        sys.exit(0)
    title, changes = generate_summary(diffs)
    change_body = "\n".join([f"- {c}" for c in changes])
    print(change_body)
