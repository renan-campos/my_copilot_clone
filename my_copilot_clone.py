"""
    my_copilot_cli_clone leverages gpt-3.5-turbo to mimic the functionality described here:
        https://githubnext.com/projects/copilot-cli/
    For now, it acts like '??':
    "?? is meant as the general-purpose goto for arbitrary shell commands."
"""

import os
import sys
import openai

MODEL = "gpt-3.5-turbo-0301"

def main():
    setup_openai()
    query = process_args()
    response = command_query(query)
    display_response(response)


def setup_openai():
    api_key = os.environ.get("OPENAI_API_KEY")
    if api_key is None:
        sys.stderr.write("Error: OPENAI_API_KEY environment variable is not set.\n")
        sys.stderr.write("\tI suggest asking Chat GPT how to set that up.\n")
        sys.exit(1)
    openai.api_key = api_key

def process_args():
    args = sys.argv
    if len(args) < 2:
        sys.stderr.write("Error: No command description provided\n")
        sys.exit(1)
    return " ".join(args[1:])


def command_query(query):
        def gpt_call():
            return openai.ChatCompletion.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": "Only show the command and a bulleted breakdown of the parameters to perform the described action on the bash shell.'"},
                    {"role": "user", "name": "command-query", "content": query},
                ],
            )
        gpt_response = handle_gpt_exceptions(gpt_call)
        return gpt_response["choices"][0]["message"]["content"]

def handle_gpt_exceptions(call):
    """
        Makes the chat gpt call, and handles exceptions if it fails.
        For certain exceptions, it will apply exponential backoff and try again.
    """
    num_retries = 10
    wait_time = 3
    for _ in range(num_retries):
        try:
            response = call()
        except openai.error.RateLimitError:
            sys.stderr.write(f"WARNING Rate limit error hit. Sleeping for {wait_time} seconds, then trying again.\n")
            time.sleep(wait_time)
            wait_time *= 2
            continue
        return response
    raise OutOfRetries()

class OutOfRetries(Exception):
    def __init__(self):
        self.message = "Ran out of retries"
    def __str__(self):
        return self.message

def display_response(response):
    # Making the output purple because that's my favorite color.
    PURPLE = '\033[1;95;47m'
    END = '\033[0m'
    print(f"{PURPLE}\n{response}{END}\n")

if __name__ == "__main__":
    main()
