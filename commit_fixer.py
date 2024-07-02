import json
import os
import sys
from typing import List

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
)

EXAMPLE_JSON = {
    "diffs": ["diff desc 1", "diff desc 2"],
    "changes": ["change desc 1", "change desc 2"]
}


def get_format_prompt() -> str:
    """
    Generates prompt displaying the expected format of the json response.
    :return: Format prompt as string.
    """
    example_json_str = json.dumps(EXAMPLE_JSON, indent=4)
    return f"Output valid json like so:\n```json\n{example_json_str}\n```"


def generate_summary(commit_diff: str):
    """
    Summarizes the changes present in the commit diff.
    :param commit_diff: String containing all the diffs of commit.
    :return: Summary of commit diffs.
    """
    format_prompt = get_format_prompt()
    system_prompt = "\n\n".join([INSTRUCTIONS_PROMPT, format_prompt])
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


def read_file(f_path):
    """
    Reads file at given path.
    :param f_path: Path to the file to read.
    :return: Content of the file.
    """
    with open(f_path, 'r') as file:
        f_content = file.read()
        return f_content


if __name__ == "__main__":
    load_dotenv()
    diff_file = sys.argv[1]
    diffs = read_file(diff_file)
    if len(diffs.strip()) == 0:
        sys.exit(0)
    diff_summary = generate_summary(diffs)
    print(diff_summary)
