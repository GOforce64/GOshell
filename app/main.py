import sys
import os
from pathlib import Path
import subprocess
import shlex
from io import StringIO
from contextlib import redirect_stdout, redirect_stderr

command_types = {"echo": "builtin", "exit": "builtin", "type": "builtin", "pwd": "builtin", "cd": "builtin"}


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

def search_output(command, candidate = "", redirectIndex = -1, out_buf = None, err_buf = None):
    if redirectIndex == -1:
        if candidate != "":
            print(f"{command} is {candidate}")
        else:
            print(f"{command}: not found")
    else:
        redirect_stdout(out_buf)
        redirect_stderr(err_buf)
        with open(commandList[redirectIndex + 1], "w") as f:
            if candidate != "":
                f.write(f"{command} is {candidate}\n")
            else:
                f.write(f"{command}: not found\n")

def main():
    mainLoop = True
    while mainLoop:
        sys.stdout.write("$ ")
        sys.stdout.flush()

        # Wait for user input
        command = input()

        # No input, new line
        if command:
            commandList = shlex.split(command)
            executable = find_executable(commandList[0])
            redirectIndex = -1
            out_buf = StringIO()
            err_buf = StringIO()
            
            for index, command in enumerate(commandList):
                if commandList[index] == "1>" or commandList[index] == ">":
                    redirectIndex = index

            # exit command
            if commandList[0].lower() == "exit":
                mainLoop = False
                break

            # echo command
            elif commandList[0] == "echo":
                if redirectIndex == -1:
                    print(" ".join(commandList[1:]))
                else:
                    redirect_stdout(out_buf)
                    redirect_stderr(err_buf)
                    with open(commandList[redirectIndex + 1], "w") as f:
                        f.write(out_buf.getvalue())

            # type command
            elif commandList[0] == "type":
                if commandList[1] in command_types and command_types[commandList[1]] == "builtin":
                    if redirectIndex == -1:
                        print(f"{command[5:]} is a shell builtin")
                    else:
                        redirect_stdout(out_buf)
                        redirect_stderr(err_buf)
                        with open(commandList[redirectIndex + 1], "w") as f:
                            f.write(out_buf.getvalue())
                else:
                    result = find_executable(commandList[1])
                    if result[0] == True:
                        search_output(result[1], result[2], redirectIndex, out_buf, err_buf)
                    else:
                        search_output(result[1], "", redirectIndex, out_buf, err_buf)

            # pwd command
            elif command == "pwd":
                print(Path.cwd())

            # cd command
            elif commandList[0] == "cd":
                if len(commandList) == 1:
                    os.chdir(Path.home())
                    continue
                elif (commandList[1] == "~"):
                    os.chdir(Path.home())
                    continue
                try:
                    os.chdir(commandList[1])
                except FileNotFoundError:
                    print(f"cd: {commandList[1]}: No such file or directory")
                except NotADirectoryError:
                    print(f"cd: {commandList[1]}: Not a directory")
                except PermissionError:
                    print(f"cd: {commandList[1]}: Permission denied")
                continue

            # run if executable
            elif executable[0]:
                if redirectIndex == -1:
                    subprocess.run(
                    commandList,
                    executable=str(executable[2]))
                else:
                    process = subprocess.Popen(
                    commandList,
                    executable=str(executable[2]),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True)

                    with open(commandList[redirectIndex + 1], "w") as f:
                        for line in process.stdout:
                            f.write(line)
                    process.wait()

            # unknown command
            else:
                print(f"{command}: command not found")


if __name__ == "__main__":
    main()