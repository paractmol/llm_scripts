from gpt4all import GPT4All # type: ignore
import subprocess
import os
import atexit

def restore_staged_files():
    os.system('git restore --staged .')
    print("Staged changes have been restored.")

atexit.register(restore_staged_files)

SYSTEM_PROMPT = """
  As a software developer, your task is to generate a concise and compliant git commit
  message for the changes you can see in the prompt.
  The message should be short, descriptive, and follow best practices for writing commit messages, and it
  can include emojis to convey the message effectively.
  You are about to commit your changes to the project's repository. Generate a short git commit message
  based on the file changes you can see in the prompt.
"""

MODEL = GPT4All("Meta-Llama-3-8B-Instruct.Q4_0.gguf")

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

  with MODEL.chat_session(SYSTEM_PROMPT) as llm:
    message = (llm.generate(instructions(custom_instructions), max_tokens=512, temp=0.5))

  try:
    return message.split('"')[1]
  except IndexError:
    print("Error: Failed to generate a valid commit message.")
    return None

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

if __name__ == "__main__":
    main()
