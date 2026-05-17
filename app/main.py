import sys
import os
from pathlib import Path
import subprocess

command_types = {"echo": "builtin", "exit": "builtin", "type": "builtin"}


def find_executable(command):
    path_value = os.environ.get("PATH", "") # get returns PATH var or empty string if not found

    # Windows executable extensions
    extensions = os.environ.get("PATHEXT", "").split(os.pathsep)

    # Linux/macOS support
    if not extensions:
        extensions = [""]

    for directory in path_value.split(os.pathsep):
        if not directory:
            continue

        path = Path(directory)

        if not path.is_dir():
            continue

        # Try command directly AND with extensions
        for ext in [""] + extensions:
            candidate = path / (command + ext)

            if candidate.is_file() and os.access(candidate, os.X_OK):
                return [True, command, candidate]

    return [False, command, ""]

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
            executable = find_executable(commandList[0])
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

            # pwd command
            elif command == "pwd":
                print(Path.cwd())

            # run if executable
            elif executable[0]:
                subprocess.run(
                commandList,
                executable=str(executable[2]))

            # unknown command
            else:
                print(f"{command}: command not found")


if __name__ == "__main__":
    main()