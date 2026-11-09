import platform
import subprocess
import sys


def main():
    print(" • -> CHECKING FOR UPDATES")

    try:
        subprocess.run(
            ["git", "pull", "--quiet"],
            timeout=30,
            check=False,
        )
        print(" • -> UPDATE CHECK COMPLETED")
    except Exception:
        print(" • -> UPDATE CHECK SKIPPED")

    if platform.architecture()[0] != "64bit":
        print(" • -> 64BIT REQUIRED")
        sys.exit(1)

    print(" • -> 64BIT DETECTED")
    print(" • -> STARTING AVINAV")

    from data.Avinav import main as start_app
    start_app()


if __name__ == "__main__":
    main()
