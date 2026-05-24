import sys
import os
from pathlib import Path
import subprocess
import shlex
from io import StringIO
from contextlib import redirect_stdout, redirect_stderr
try:
    import readline
except ImportError:
    try:
        import pyreadline3 as readline
    except ImportError:
        readline = None  # silently disable if neither available (dependent on OS)

command_types = {"echo": "builtin", "exit": "builtin", "type": "builtin", "pwd": "builtin", "cd": "builtin"}


def find_executable(command):

    # Handle direct/absolute/relative paths
    p = Path(command)
    if p.is_file() and os.access(p, os.X_OK):
        return [True, command, p]

    # Windows executable extensions
    path_value = os.environ.get("PATH", "")
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

# Remove redirect tokens and filenames from the command
def build_actual_command(commandList, redirectIndex, errorIndex, appendIndex, appendErrorIndex):
    skip = set()
    for index in (redirectIndex, errorIndex, appendIndex, appendErrorIndex):
        if index != -1:
            skip.add(index)
            skip.add(index + 1)
    return [token for i, token in enumerate(commandList) if i not in skip]

def split_command(command):
    try:
        return shlex.split(command, posix=True)
    except ValueError:
        return command.split()
    
def strip_quotes(token):
    if len(token) >= 2 and token[0] == token[-1] and token[0] == "'":
        # Single quotes: everything literal, just remove the quotes
        return token[1:-1]
    elif len(token) >= 2 and token[0] == token[-1] and token[0] == '"':
        # Double quotes: process escape sequences inside
        inner = token[1:-1]
        result = []
        i = 0
        while i < len(inner):
            if inner[i] == '\\' and i + 1 < len(inner):
                next_char = inner[i + 1]
                if next_char in ('"', '\\', '$', '`', '\n'):
                    # These are the only chars backslash escapes inside double quotes
                    result.append(next_char)
                    i += 2
                else:
                    # Backslash is literal if followed by anything else
                    result.append('\\')
                    i += 1
            else:
                result.append(inner[i])
                i += 1
        return ''.join(result)
    return token

def get_executables():
    executables = []
    path_value = os.environ.get("PATH", "")
    for directory in path_value.split(os.pathsep):
        p = Path(directory)
        if p.is_dir():
            for f in p.iterdir():
                if f.is_file() and os.access(f, os.X_OK):
                    executables.append(f.name)
    return executables

# Build once at startup
_executables_cache = []

def completer(text, state):
    global _executables_cache
    if not _executables_cache:
        _executables_cache = get_executables()

    builtins = list(command_types.keys())
    options = [cmd for cmd in builtins + _executables_cache if cmd.startswith(text)]
    
    if state < len(options):
        match = options[state]
        # Add trailing space for commands that take arguments
        if match in command_types:
            return match + " "
        return match
    return None

def main():
    if readline:
        readline.set_completer(completer)
        readline.parse_and_bind("Tab: complete")
    mainLoop = True
    while mainLoop:
        sys.stdout.write("$ ")
        sys.stdout.flush()

        # Wait for user input
        command = input()

        # No input, new line
        if command:
            commandList = split_command(command)
            executable = find_executable(commandList[0])

            out_buf = StringIO()
            err_buf = StringIO()
            redirectIndex = -1
            errorIndex = -1
            appendIndex = -1
            appendErrorIndex = -1

            for index, token in enumerate(commandList):
                if token in ("1>", ">"):
                    redirectIndex = index
                elif token == "2>":
                    errorIndex = index
                elif token in ("1>>", ">>"):
                    appendIndex = index
                elif token == "2>>":
                    appendErrorIndex = index

            # exit command
            if commandList[0].lower() == "exit":
                mainLoop = False
                break

            # echo command
            elif commandList[0] == "echo":
                # find the first redirect position (either 1> or 2>)
                cutoff = min(
                    redirectIndex    if redirectIndex    != -1 else len(commandList),
                    errorIndex       if errorIndex       != -1 else len(commandList),
                    appendIndex      if appendIndex      != -1 else len(commandList),
                    appendErrorIndex if appendErrorIndex != -1 else len(commandList),
                )
                content = " ".join(commandList[1:cutoff]) + "\n"

                if redirectIndex != -1:
                    with open(commandList[redirectIndex + 1], "w") as f:
                        f.write(content)
                elif appendIndex != -1:
                    with open(commandList[appendIndex + 1], "a") as f:
                        f.write(content)
                else:
                    print(content, end="")

                if errorIndex != -1:
                    with open(commandList[errorIndex + 1], "w") as f:
                        f.write("")
                elif appendErrorIndex != -1:
                    with open(commandList[appendErrorIndex + 1], "a") as f:
                        f.write("")

            # type command
            elif commandList[0] == "type":
                if commandList[1] in command_types and command_types[commandList[1]] == "builtin":
                    if redirectIndex == -1:
                        print(f"{commandList[1]} is a shell builtin")
                    else:
                        with open(commandList[redirectIndex + 1], "w") as f:
                            f.write(f"{commandList[1]} is a shell builtin\n")
                else:
                    result = find_executable(commandList[1])
                    if result[0] == True:
                        search_output(result[1], result[2], redirectIndex, out_buf, err_buf)
                    else:
                        search_output(result[1], "", redirectIndex, out_buf, err_buf)

            # pwd command
            elif commandList[0] == "pwd":
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
                actualCommand = build_actual_command(commandList, redirectIndex, errorIndex, appendIndex, appendErrorIndex)

                process = subprocess.Popen(
                    actualCommand,
                    executable=str(executable[2]),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True)

                # Handle stdout
                if redirectIndex != -1:
                    with open(commandList[redirectIndex + 1], "w") as f:
                        for line in process.stdout:
                            f.write(line)
                elif appendIndex != -1:
                    with open(commandList[appendIndex + 1], "a") as f:    # "a" = append
                        for line in process.stdout:
                            f.write(line)
                else:
                    for line in process.stdout:
                        print(line, end="")

                # Handle stderr
                if errorIndex != -1:
                    with open(commandList[errorIndex + 1], "w") as f:
                        for line in process.stderr:
                            f.write(line)
                elif appendErrorIndex != -1:
                    with open(commandList[appendErrorIndex + 1], "a") as f:  # "a" = append
                        for line in process.stderr:
                            f.write(line)
                else:
                    for line in process.stderr:
                        print(line, end="")

                process.wait()

            # unknown command
            else:
                print(f"{command}: command not found")


if __name__ == "__main__":
    main()