import json
from typing import Dict, List, Tuple, cast

from safa.data.file_change import FileChange

SUMMARIZE_INSTRUCTIONS = """
You are a AI agent working on a software project to help users document their development practices.

The first message will contain a project overview documenting its original vision.
However, their software is undergoing some changes and they have not had time to update the documentation.
Our job is detect what is changing and describe the system after the changes.

The subsequent message will contain a change they have made across all files.
Your job is the make sense of these changes and describe the new system behavior.
Each of these messages will contain the file before the change, the file specification, and the diff of the changes.

Create a JSON object that:
- summarizes each diff to describe how the code is changing
- uses the diff summaries to describe how the system functionality is changing
- uses the changing system functionality to describe what is being introduced
"""

SUMMARIZE_FORMAT = {
    "diffs": ["diff summary 1", "diff summary 2"],
    "changes": ["change 1", "change 2"],
    "title": "commit title"
}

EMPTY_PROJECT_SUMMARY = "Project summary has not been generated yet."


def summarize_commit_changes(llm_manager, file_changes: List[FileChange], project_summary: str) -> Tuple[str, List[str]]:
    """
    Generates summary for list of changes.
    :param llm_manager: LLM manager used to summarize file changes.
    :param file_changes: File changes to summarize into one commit.
    :param project_summary: The project summary to include in system description.
    :return: Title and changes across files.
    """
    prompt = create_change_prompt(file_changes)
    system_prompt = "\n\n".join([SUMMARIZE_INSTRUCTIONS, get_format_prompt(SUMMARIZE_FORMAT)])
    messages = [
        ("system", system_prompt),
        ("human", project_summary if project_summary else EMPTY_PROJECT_SUMMARY),
        ("human", prompt)
    ]
    print("...generating...")

    response = cast(str, llm_manager.invoke(messages).content)
    response_json = parse_json(response)
    diff_summaries = response_json["changes"]
    title = response_json["title"]
    return title, diff_summaries


def create_change_prompt(changes: List[FileChange], delimiter="\n\n") -> str:
    """
    Creates prompts detailing the file summary, file before commit, and file changes.
    :param changes: List of file changes.
    :param delimiter: The delimiter to use between sections.
    :return: Prompt containing all file changes.
    """
    prompts = []

    for change in changes:
        change_prompts = [f"# File: {change.file}"]
        if change.summary:
            change_prompts.append(f"## Original Specification\n{change.summary}")
        if change.content_before:
            change_prompts.append(f"## File Before Change\n{change.content_before}")
        change_prompts.append(f"## Changes\n{change.diff}")
        change_prompt = delimiter.join(change_prompts)
        prompts.append(change_prompt)

    return cast(str, delimiter.join(prompts))


def parse_json(response: str) -> Dict:
    """
    Attempts to find the JSON block in response and parse it into an object.
    :param response: String response from LLM.
    :return: Parsed JSON.
    """
    start_index = response.find("```json")
    end_index = response.find("```", start_index + 1)
    json_str = response[start_index + 7:end_index]
    try:
        return cast(Dict, json.loads(json_str))
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
