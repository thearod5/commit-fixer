from safa_cmd.config import FixerConfig


def run(config: FixerConfig = None):
    if config is None:
        config = FixerConfig.from_env()
