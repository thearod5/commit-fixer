# Overview

Generates commit summary for currently staged changes. Commits changes if user approves.

# Instructions

1. Create venv with python>=3.10
2. Install requirements.txt
3. Create `.env` file with:
    - SAFA_EMAIL: Email of SAFA account.
    - SAFA_PASSWORD: Password of SAFA account.
    - SAFA_VERSION_ID: Version ID of project to include documentation for.

# TODO:

- Automated way to publish new packages
    - Needs test suite to verify use cases are not broken
- MVP:
    - Create new project
    - Summary project
- Be able to configure defaults