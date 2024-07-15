from gpt4all import GPT4All # type: ignore
import subprocess
import os
import pdb

SYSTEM_PROMPT = """
    Generate a short git commit message based on the file changes in the prompt.
    The commit message should be:
    - It should be in double quotes.
    - Analyze the changes in the prompt and generate a commit message based on the changes.
    - It should be compliant with the best practices for writing commit messages.
    - In the present tense.
    - Concise and to the point.
    - Descriptive of what has changed without going into too much detail.
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
  print("custom_instructions", custom_instructions)

  if custom_instructions:
    custom_instructions += "Also include this custom instructions:\n"
    custom_instructions += diff_output()

    pdb.set_trace()

    return custom_instructions
  else:
    return diff_output()

def commit_message(custom_instructions = None):
  os.system('git add --intent-to-add .')

  print("Generating commit message...")

  with model().chat_session(SYSTEM_PROMPT) as llm:
    message = (llm.generate(instructions(custom_instructions), max_tokens=512, temp=0.5))

  pdb.set_trace()

  return message.split('"')[1]

def are_you_sure(message):
  if not message:
    print("No commit message generated.")
  else:
    print(f"Commit message: {message}")

    user_input = input(
      "Do you like the commit message? ([y]es/[n]o/[e]dit/[r]etry): "
    )
    if user_input.lower() == "y":
      os.system('git add .')
      os.system(f'git commit -m "{message}"')

      print("Confirmed!")
    elif user_input.lower() == "e":
      custom_instructions = input("Enter custom instructions: ")
      pdb.set_trace()
      message = commit_message(custom_instructions)
      are_you_sure(message)
    elif user_input.lower() == "n":
      print("Cancelled.")
    elif user_input.lower() == "r":
      main()
    else:
      print("Invalid input. Please enter 'y' or 'n' or 'r'.")
      are_you_sure(message)

def main():
  message = commit_message(None)
  are_you_sure(message)

main()
