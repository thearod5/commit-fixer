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

- [ ] Move store to config so that it can be accessed everywhere
- [ ] Be able to configure defaults
    - [x] Account
    - [x] Project
    - [x] Cache File
    - [ ] LLM Settings
- [ ] Chat with your project
- [ ] Task manager (e.g. embedding change impact analysis, llm lookie look, and change recommendation)
- [ ] What does this line do? (feat; AST Summarization)
- [x] Be able to re-summarize the artifacts that got changed in commit.
- [x] Be able to search only artifacts of specific type.
- [x] MVP:
    - Create new project / select existing
    - Import project
    - Summarize project
    - Search Project
    - Commit Project
