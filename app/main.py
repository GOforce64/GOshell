import sys


def main():
    mainLoop = True
    while mainLoop:
        sys.stdout.write("$ ")

        # Wait for user input
        command = input()

        # exit command
        if command.lower() == "exit":
            mainLoop = False
            break

        # echo command
        elif command.startswith("echo "):
            print(command[5:])

        # type command
        elif command.startswith("type "):
            if command[5:] == "echo":
                print("echo is a shell builtin")
            elif command[5:] == "exit":
                print("exit is a shell builtin")
            elif command[5:] == "type":
                print("type is a shell builtin")
            else:
                print(f"{command[5:]}: not found")

        # unknown command
        else:
            print(f"{command}: command not found")


if __name__ == "__main__":
    main()
