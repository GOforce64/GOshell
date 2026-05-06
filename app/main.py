import sys


def main():
    mainLoop = True
    while mainLoop:
        sys.stdout.write("$ ")

        # Wait for user input
        command = input()
        sys.stdout.write(f"{command}: command not found\n")


if __name__ == "__main__":
    main()
