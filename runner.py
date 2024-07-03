from dotenv import load_dotenv

from src.commit_fixer.config import CommitConfig
from src.commit_fixer.fixer import run

if __name__ == "__main__":
    load_dotenv()
    config = CommitConfig.from_env()
    run(config)

    print("Done.")
