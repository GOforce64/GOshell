import sys
import os
from pathlib import Path

command_types = {"echo": "builtin", "exit": "builtin", "type": "builtin"}



def find_executable(command):
    found = False
    path_value = os.environ.get("PATH", "")
    if path_value:
        for directory in path_value.split(os.pathsep):
            if not directory:
                continue
            path = Path(directory)
            if not path.is_dir():
                continue
            candidate = path / command # merges path object, example: candidate = Path("/usr/bin/python") (works OS independesnty to merge path strings)
            if candidate.is_file() and os.access(candidate, os.X_OK):
                print(f"{command} is {candidate}")
                found = True
                break
    if not found:
        print(f"{command}: not found")

def main():
    mainLoop = True
    while mainLoop:
        sys.stdout.write("$ ")

        # Wait for user input
        command = input()

        # No input, new line
        if command:
            # exit command
            if command.lower() == "exit":
                mainLoop = False
                break

            # echo command
            elif command.startswith("echo "):
                print(command[5:])

            # type command
            elif command.startswith("type "):
                if command[5:] in command_types and command_types[command[5:]] == "builtin":
                    print(f"{command[5:]} is a shell builtin")
                else:
                    find_executable(command[5:])

            # unknown command
            else:
                print(f"{command}: command not found")


if __name__ == "__main__":
    main()
