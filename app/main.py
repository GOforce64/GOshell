import sys


def main():
    mainLoop = True
    while mainLoop:
        sys.stdout.write("$ ")

        # Wait for user input
        command = input()

        if command.lower() == "exit":
            mainLoop = False
            break

        elif command.startswith("echo "):
            print(command[5:])
            
        else:
            print(f"{command}: command not found")


if __name__ == "__main__":
    main()
