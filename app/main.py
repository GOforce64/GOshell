import sys


def main():
    mainLoop = True
    while mainLoop:
        sys.stdout.write("$ ")

        # Wait for user input
        command = input()
        if command == "exit":
            mainLoop = False
            break
        
        print(f"{command}: command not found")


if __name__ == "__main__":
    main()
