
import platform
import subprocess
import sys
from pathlib import Path

arc = None


def print_status(message):
    print(f" • \033[38;5;196m->\033[37m {message}")


def check_updates():
    print_status("CHECKING FOR UPDATES")

    try:
        result = subprocess.run(
            ["git", "pull", "--quiet"],
            capture_output=True,
            text=True,
            timeout=30,
            check=False
        )

        if result.returncode == 0:
            print_status("UPDATE CHECK COMPLETED")
        else:
            print_status("UPDATE FAILED OR GIT REPOSITORY NOT CONFIGURED")

    except FileNotFoundError:
        print_status("GIT IS NOT INSTALLED")
    except subprocess.TimeoutExpired:
        print_status("UPDATE CHECK TIMED OUT")


def main():
    global arc

    architecture = platform.architecture()[0]

    if architecture == "32bit":
        arc = "32BIT"
        print_status("32BIT NOT SUPPORTED")
        sys.exit(1)

    elif architecture == "64bit":
        arc = "64BIT"
        print_status("64BIT DETECTED")
        print_status("STARTING AVINAV")

        try:
            import data.Avinav
        except ModuleNotFoundError as error:
            print_status(f"MODULE NOT FOUND: {error}")
            sys.exit(1)
        except Exception as error:
            print_status(f"APPLICATION ERROR: {error}")
            sys.exit(1)

    else:
        arc = "INVALID"
        print_status("UNKNOWN DEVICE TYPE")
        sys.exit(1)


if __name__ == "__main__":
    check_updates()
    main()
    
