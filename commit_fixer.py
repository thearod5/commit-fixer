import git
from langchain.llms import Anthropic, OpenAI
from langchain.prompts import ChatPrompt

# Initialize the LLM providers
openai = OpenAI(api_key='your_openai_api_key')
anthropic = Anthropic(api_key='your_anthropic_api_key')

# Choose your LLM provider
llm = anthropic  # or anthropic

# Initialize the repository
repo = git.Repo('.')


def generate_summary(commit_message):
    prompt = ChatPrompt(
        llm=llm,
        prompt=f"Summarize the following commit message:\n\n{commit_message}"
    )
    response = prompt.execute()
    return response['text'].strip()


def get_user_input(prompt_text):
    return input(prompt_text)


def main():
    # Get commits to be pushed
    commits = list(repo.iter_commits('origin/main..HEAD'))

    for commit in commits:
        original_message = commit.message

        print(f"Commit: {original_message}")
        user_choice = get_user_input("Choose an option: (1) Keep as is, (2) Generate summary: ")

        if user_choice == '1':
            continue
        elif user_choice == '2':
            summary = generate_summary(original_message)
            print(f"Generated Summary: {summary}")

            final_title = get_user_input("Enter the final title: ")
            final_content = get_user_input("Enter the final content: ")

            confirmation = get_user_input("Do you want to update this commit? (yes/no): ")
            if confirmation.lower() == 'yes':
                new_message = f"{final_title}\n\n{final_content}"

                # Amend the commit message
                repo.git.commit('--amend', '-m', new_message, '--no-edit', '--author', commit.author)


if __name__ == "__main__":
    main()
