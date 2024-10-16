import argparse
import os
import sys
from typing import Dict, List, Optional, OrderedDict, Tuple

import urllib3

from safa.api.safa_client import SafaClient
from safa.tools.configure import configure

SRC_PATH = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(SRC_PATH)

from safa.api.client_factory import create_safa_client
from safa.constants import safa_banner
from safa.tool_registrar import TOOL_FUNCTIONS, TOOL_GROUPS, TOOL_NAMES, TOOL_PERMISSIONS
from safa.utils.fs import clean_path
from safa.utils.menus.printers import print_title

from safa.config.safa_config import SafaConfig
from safa.utils.menus.inputs import input_option

OneOrMany = Dict[str, str] | Dict[str, List[str]]


def main() -> None:
    """
    Allows users to run tools.
    :return: None
    """
    setup_main()
    repo_path, env_file_path, tool = parse_args()
    print("\n", safa_banner.strip(), "\n\n")

    config = SafaConfig.from_repo(repo_path, root_env_file_path=env_file_path)
    if not config.is_configured():
        configure(config)

    client = create_safa_client(config)

    print_title("Configuration")
    print(config)

    run_tool_loop(config, client, tool=tool)


def run_tool_loop(config: SafaConfig, client: SafaClient, tool: Optional[str] = None):
    running = True
    while running:
        tools, tool2name, group2tools = filter_tools_by_permissions(TOOL_NAMES,
                                                                    TOOL_GROUPS,
                                                                    TOOL_PERMISSIONS,
                                                                    config)
        tools.append("exit")
        tool2name["exit"] = "Exit"
        group2tools["---"] = ["exit"]
        if not tool:
            option_selected = input_option(tools,
                                           item2name=tool2name,
                                           title="Command",
                                           group2items=group2tools,
                                           page_items=len(tools))
            if option_selected == "exit":
                print("Good Bye :)")
                return
        else:
            option_selected = tool

        tool_func = TOOL_FUNCTIONS[option_selected]
        tool_func(config, client)

        if tool:
            sys.exit("All Done :)")


def filter_tools_by_permissions(tool_options: Dict, tool_groups: OneOrMany, tool_permissions: Dict,
                                config: SafaConfig) -> Tuple[List[str], Dict, Dict]:
    """
    Filters for tools that meet permission levels.
    :param tool_options: Set of available tools.
    :param tool_groups: Set of available permissions.
    :param tool_permissions: Map of tool to permissions required to run that tool.
    :param config: SafaConfig to extract permissions from.
    :return: Map of tool name to func for available tools.
    """
    configured_entities = config.get_configured_entities()

    available_tools: List[str] = [k for k, v in tool_permissions.items() if
                                  all([v_item in configured_entities for v_item in v]) or "*" in v]
    available_groups: Dict = _filter_groups(tool_groups, available_tools)
    tool2name: Dict = {k: v for k, v in tool_options.items() if k in available_tools}
    return available_tools, tool2name, available_groups


def _filter_groups(groups: OneOrMany, valid_items: List[str]) -> Dict:
    items: List[Tuple[str, List[str]]] = [
        (k, [v_item for v_item in v
             if v_item in valid_items] if isinstance(v, list) else _filter_groups(v, valid_items))  # type: ignore
        for k, v in groups.items()
    ]
    new_groups = OrderedDict[str, List[str]](items)
    filtered_groups = {k: v for k, v in new_groups.items() if len(v) > 0}
    return filtered_groups


def parse_args():
    parser = argparse.ArgumentParser(description="A tool for processing repositories.")
    parser.add_argument('--tool', '-t', type=str, help="Specify the tool to use")
    parser.add_argument('--repo_path', '-r', type=str, help="Path to the repository directory")
    parser.add_argument('--env', '-e', type=str, help="Path to the environment file")

    args = parser.parse_args()

    repo_path = clean_path(args.repo_path) if args.repo_path else os.path.abspath("")
    env_file_path = clean_path(args.env) if args.env else None

    return repo_path, env_file_path, args.tool


def setup_main():
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    os.environ["TOKENIZERS_PARALLELISM"] = "false"


if __name__ == "__main__":
    main()
