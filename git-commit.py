from gpt4all import GPT4All # type: ignore
import subprocess
import os

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

def system_prompt():
  prompt =  """Generate a short git commit message based on the file changes in the prompt.
    The commit message should be:
    - Analyze the changes in the prompt and generate a commit message based on the changes.
    - In the present tense.
    - Concise and to the point.
    - Descriptive of what has changed without going into too much detail.
    - It can include emojis to convey the message.
  """
  return prompt

def commit_message():
  os.system('git add --intent-to-add .')

  with model().chat_session(system_prompt()) as llm:
    message = (llm.generate(diff_output(), max_tokens=512, temp=0.5))

  return message.split('"')[1]

def are_you_sure(message):
  if not message:
    print("No commit message generated.")
  else:
    print(f"Commit message: {message}")

    user_input = input("Do you like the commit message? ([y]es/[n]o/[r]etry): ")
    if user_input.lower() == "y":
      os.system('git add .')
      os.system(f'git commit -m "{message}"')

      print("Confirmed!")
    elif user_input.lower() == "n":
      print("Cancelled.")
    elif user_input.lower() == "r":
      main()
    else:
      print("Invalid input. Please enter 'y' or 'n' or 'r'.")
      are_you_sure(message)

def main():
  message = commit_message()
  are_you_sure(message)

main()
