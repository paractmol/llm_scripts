from gpt4all import GPT4All # type: ignore
import subprocess
import os

SYSTEM_PROMPT = """
    Pretend you are a software developer working on a project. You are about to commit your
    changes to the project's repository. Generate a short git commit message based on the file
    changes you can see in the prompt.

    Instructions:
    - Analyze the changes in the prompt.
    - It should be in double quotes.
    - It should be compliant with the best practices for writing commit messages.
    - Concise and to the point.
    - It can include emojis to convey the message.
  """

def model():
  return GPT4All("Meta-Llama-3-8B-Instruct.Q4_0.gguf")

def run_subprocess(command):
  result = subprocess.run(command, stdout=subprocess.PIPE, text=True)
  return result.stdout

def diff_output():
  result = run_subprocess(["git", "diff", "--cached"])
  if not result:
    result = run_subprocess(["git", "diff"])
  return result

def instructions(custom_instructions = None):
  if custom_instructions:
    new_prompt = "The custom instructions from the user:\n"
    new_prompt += custom_instructions + "\n"
    new_prompt += diff_output()

    return new_prompt
  return diff_output()

def commit_message(custom_instructions = None):
  os.system('git add --intent-to-add .')

  print("Generating commit message...")

  with model().chat_session(SYSTEM_PROMPT) as llm:
    message = (llm.generate(instructions(custom_instructions), max_tokens=512, temp=0.5))

  return message.split('"')[1]

def are_you_sure(message):
  if not message:
    print("No commit message generated.")
  else:
    print(f"Commit message: {message}")

    user_input = input(
      "Do you like the commit message? ([y]es/[n]o/[e]dit/[r]etry): "
    ).lower()
    if user_input == "y":
      os.system('git add .')
      os.system(f'git commit -m "{message}"')

      print("Confirmed!")
    elif user_input == "e":
      custom_instructions = input("Enter custom instructions: ")
      message = commit_message(custom_instructions)
      are_you_sure(message)
    elif user_input == "n":
      print("Cancelled.")
    elif user_input == "r":
      main()
    else:
      print("Invalid input. Please enter 'y', 'n', 'e' or 'r'.")
      are_you_sure(message)

def main():
  message = commit_message(None)
  are_you_sure(message)

main()
