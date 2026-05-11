import sys
import os
from pathlib import Path
import subprocess

command_types = {"echo": "builtin", "exit": "builtin", "type": "builtin"}


def find_executable(command):
    found = False
    path_value = os.environ.get("PATH", "") # get returns PATH var or empty string if not found
    if path_value:
        for directory in path_value.split(os.pathsep):
            if not directory:
                continue
            path = Path(directory)
            if not path.is_dir():
                continue
            candidate = path / command # merges path object, example: candidate = Path("/usr/bin/python") (works OS independesnty to merge path strings)
            if candidate.is_file() and os.access(candidate, os.X_OK):
                return [True, command, candidate]
    return [False, command, candidate]

def search_output(command, candidate = ""):
    if candidate != "":
        print(f"{command} is {candidate}")
    else:
        print(f"{command}: not found")
        

def main():
    mainLoop = True
    while mainLoop:
        sys.stdout.write("$ ")

        # Wait for user input
        command = input()

        # No input, new line
        if command:
            commandList = command.split()
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
                    result = find_executable(command[5:])
                    if result[0] == True:
                        search_output(result[1], result[2])
                    else:
                        search_output(result[1])

            # run if executable
            
            elif find_executable(commandList[0])[0] == True:
                result = subprocess.run(
                    commandList,
                    capture_output=True,
                    text=True)
                print("STDOUT:", result.stdout)
                #print("STDERR:", result.stderr)
                #print("CODE:", result.returncode)

            # unknown command
            else:
                print(f"{command}: command not found")


if __name__ == "__main__":
    main()