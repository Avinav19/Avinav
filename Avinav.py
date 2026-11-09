import os
import sys
import time
import json
import socket
import shutil
import platform
import subprocess
import urllib.request
import re
from pathlib import Path
from datetime import datetime

VERSION = "1.0"


# =============== COLORS ===============

RED = "\033[1;31m"
GREEN = "\033[1;32m"
CYAN = "\033[1;36m"
YELLOW = "\033[1;33m"
RESET = "\033[0m"


def clear():
    os.system("clear")


def banner():
    print(RED + "=" * 46)
    print("                 A V I N A V")
    print("          ADVANCED SYSTEM TOOLKIT")
    print("                 VERSION " + VERSION)
    print("=" * 46 + RESET)


def pause():
    input("\nPress Enter to continue...")


def run_command(args, timeout=8):
    try:
        result = subprocess.run(
            args,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        return result.stdout.strip()
    except Exception:
        return ""


def format_bytes(value):
    value = float(value)

    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if value < 1024:
            return f"{value:.2f} {unit}"
        value /= 1024

    return f"{value:.2f} PB"


# =============== DEVICE INFORMATION ===============

def basic_info():
    clear()
    banner()

    print(CYAN + "\nBASIC SYSTEM INFORMATION" + RESET)
    print("-" * 46)

    print("Device       :", platform.node())
    print("OS           :", platform.system())
    print("Release      :", platform.release())
    print("Architecture :", platform.machine())
    print("Python       :", platform.python_version())

    print("\nANDROID DETAILS")

    for label, prop in [
        ("Manufacturer", "ro.product.manufacturer"),
        ("Brand", "ro.product.brand"),
        ("Model", "ro.product.model"),
        ("Android", "ro.build.version.release"),
        ("SDK", "ro.build.version.sdk"),
    ]:
        value = run_command(["getprop", prop])
        print(f"{label:16}: {value or 'Unavailable'}")

    pause()


def device_info():
    clear()
    banner()

    print(CYAN + "\nDEVICE INFORMATION" + RESET)
    print("-" * 46)

    properties = [
        ("Manufacturer", "ro.product.manufacturer"),
        ("Brand", "ro.product.brand"),
        ("Model", "ro.product.model"),
        ("Device", "ro.product.device"),
        ("Android Version", "ro.build.version.release"),
        ("SDK Version", "ro.build.version.sdk"),
        ("Build ID", "ro.build.id"),
        ("CPU ABI", "ro.product.cpu.abi"),
    ]

    for label, prop in properties:
        value = run_command(["getprop", prop])
        print(f"{label:20}: {value or 'Unavailable'}")

    print("\nSCREEN")
    print(run_command(["wm", "size"]) or "Unavailable")

    print("\nARCHITECTURE")
    print("Machine:", platform.machine())
    print("Processor:", platform.processor() or "Unavailable")

    pause()


# =============== MEMORY AND CPU ===============

def cpu_times():
    try:
        with open("/proc/stat") as file:
            values = list(map(int, file.readline().split()[1:]))

        idle = values[3] + (values[4] if len(values) > 4 else 0)

        return sum(values), idle
    except Exception:
        return None


def memory_info():
    try:
        data = {}

        with open("/proc/meminfo") as file:
            for line in file:
                parts = line.split()
                if len(parts) >= 2:
                    data[parts[0].rstrip(":")] = int(parts[1]) * 1024

        total = data["MemTotal"]
        available = data.get("MemAvailable", data.get("MemFree", 0))
        used = total - available

        return total, used, available

    except Exception:
        return None


def live_monitor():
    previous = cpu_times()

    try:
        while True:
            clear()
            banner()

            print(CYAN + "\nLIVE SYSTEM MONITOR" + RESET)
            print("-" * 46)

            current = cpu_times()

            if previous and current:
                total_diff = current[0] - previous[0]
                idle_diff = current[1] - previous[1]

                if total_diff > 0:
                    cpu = 100 * (1 - idle_diff / total_diff)
                    print(f"CPU Usage      : {cpu:.1f}%")
                else:
                    print("CPU Usage      : Unavailable")
            else:
                print("CPU Usage      : Unavailable")

            previous = current

            memory = memory_info()

            if memory:
                total, used, available = memory

                print("RAM Total      :", format_bytes(total))
                print("RAM Used       :", format_bytes(used))
                print("RAM Available  :", format_bytes(available))
                print("RAM Usage      :", f"{used / total * 100:.1f}%")
            else:
                print("RAM            : Unavailable")

            try:
                uptime = float(
                    Path("/proc/uptime").read_text().split()[0]
                )
                print(
                    "System Uptime  :",
                    f"{uptime / 3600:.1f} hours"
                )
            except Exception:
                print("System Uptime  : Unavailable")

            print("-" * 46)
            print("Refreshing every 2 seconds")
            print("Press CTRL+C to return")

            time.sleep(2)

    except KeyboardInterrupt:
        pass


# =============== BATTERY ===============

def battery_info():
    clear()
    banner()

    print(CYAN + "\nBATTERY INFORMATION" + RESET)
    print("-" * 46)

    result = run_command(["termux-battery-status"])

    try:
        battery = json.loads(result)

        for key, value in battery.items():
            print(f"{key.replace('_', ' ').title():20}: {value}")

    except Exception:
        print(YELLOW + "Battery information unavailable." + RESET)
        print("Install the Termux:API Android app.")
        print("Also run: pkg install termux-api")

    pause()


# =============== STORAGE ===============

def storage_analyzer():
    clear()
    banner()

    print(CYAN + "\nSTORAGE ANALYZER" + RESET)
    print("-" * 46)

    paths = [
        ("Termux Home", str(Path.home())),
        ("Root Filesystem", "/"),
    ]

    for name, path in paths:
        try:
            total, used, free = shutil.disk_usage(path)

            print(f"\n{name}")
            print("Total :", format_bytes(total))
            print("Used  :", format_bytes(used))
            print("Free  :", format_bytes(free))
            print("Usage :", f"{used / total * 100:.1f}%")

        except OSError:
            print(name, ": Unavailable")

    pause()


# =============== NETWORK SPEED ===============

def network_speed():
    clear()
    banner()

    print(CYAN + "\nNETWORK SPEED TEST" + RESET)
    print("-" * 46)
    print("Maximum download test: 10 MB")
    print("Testing...\n")

    url = "https://speed.cloudflare.com/__down?bytes=10000000"

    try:
        request = urllib.request.Request(
            url,
            headers={"User-Agent": "AVINAV"}
        )

        start = time.time()
        downloaded = 0

        with urllib.request.urlopen(request, timeout=30) as response:
            while True:
                chunk = response.read(65536)

                if not chunk:
                    break

                downloaded += len(chunk)

        elapsed = time.time() - start

        if downloaded and elapsed > 0:
            speed = downloaded * 8 / elapsed / 1000000

            print("Downloaded :", format_bytes(downloaded))
            print("Time       :", f"{elapsed:.2f} seconds")
            print("Speed      :", f"{speed:.2f} Mbps")
        else:
            print("Test failed.")

    except Exception as error:
        print("Network test failed:", error)

    pause()


# =============== PROCESS MONITOR ===============

def process_monitor():
    clear()
    banner()

    print(CYAN + "\nRUNNING PROCESSES" + RESET)
    print("-" * 72)
    print(f"{'PID':>8} {'MEMORY':>12}  PROCESS")
    print("-" * 72)

    processes = []

    try:
        for entry in Path("/proc").iterdir():
            if not entry.name.isdigit():
                continue

            try:
                name = (entry / "comm").read_text().strip()
                rss = 0

                for line in (entry / "status").read_text().splitlines():
                    if line.startswith("VmRSS:"):
                        rss = int(line.split()[1]) * 1024
                        break

                processes.append((int(entry.name), rss, name))

            except (OSError, ValueError):
                continue

        processes.sort(key=lambda item: item[1], reverse=True)

        for pid, memory, name in processes[:40]:
            print(f"{pid:8} {format_bytes(memory):>12}  {name[:35]}")

        print("\nShowing up to 40 accessible processes.")
        print("Android may restrict process visibility.")

    except Exception as error:
        print("Process monitor error:", error)

    pause()


# =============== LARGE FILE FINDER ===============

def large_file_finder():
    clear()
    banner()

    print(CYAN + "\nLARGE FILE FINDER" + RESET)
    print("-" * 46)

    try:
        minimum = input("Minimum size in MB (default 100): ")
        minimum = float(minimum) if minimum else 100

        if minimum <= 0:
            raise ValueError

    except ValueError:
        print("Invalid file size.")
        pause()
        return

    threshold = minimum * 1024 * 1024

    roots = [Path.home()]
    shared = Path.home() / "storage" / "shared"

    if shared.exists():
        roots.append(shared)

    found = []

    print("\nScanning accessible folders...")

    for root in roots:
        for current, dirs, files in os.walk(root):
            dirs[:] = [
                directory for directory in dirs
                if directory not in [".git", "__pycache__"]
            ]

            for filename in files:
                path = Path(current) / filename

                try:
                    size = path.stat().st_size

                    if size >= threshold:
                        found.append((size, path))

                except OSError:
                    continue

    found.sort(reverse=True, key=lambda item: item[0])

    if not found:
        print("No large files found.")

    for size, path in found[:50]:
        print(f"{format_bytes(size):>12}  {path}")

    print(f"\nTotal matching files: {len(found)}")

    pause()


# =============== CPU TEMPERATURE ===============

def cpu_temperature():
    clear()
    banner()

    print(CYAN + "\nCPU TEMPERATURE / THERMAL SENSORS" + RESET)
    print("-" * 46)

    found = False

    try:
        for zone in Path("/sys/class/thermal").glob("thermal_zone*"):
            try:
                temp = float((zone / "temp").read_text().strip())

                if temp > 1000:
                    temp /= 1000

                if not 0 <= temp <= 120:
                    continue

                try:
                    name = (zone / "type").read_text().strip()
                except OSError:
                    name = zone.name

                print(f"{name:25}: {temp:.1f} °C")
                found = True

            except (OSError, ValueError):
                continue

    except OSError:
        pass

    if not found:
        print("Thermal sensors unavailable.")
        print("Android may restrict sensor access.")

    pause()


# =============== DIAGNOSTICS ===============

def diagnostics():
    clear()
    banner()

    print(CYAN + "\nSYSTEM DIAGNOSTICS REPORT" + RESET)
    print("-" * 46)

    report = []

    def add(label, value):
        line = f"{label:24}: {value}"
        print(line)
        report.append(line)

    add("AVINAV Version", VERSION)
    add("Python Version", platform.python_version())
    add("Platform", platform.platform())
    add("Device", run_command(["getprop", "ro.product.model"]) or "Unavailable")

    memory = memory_info()

    if memory:
        add("Total RAM", format_bytes(memory[0]))
        add("Available RAM", format_bytes(memory[2]))

    try:
        total, used, free = shutil.disk_usage(Path.home())
        add("Storage Free", format_bytes(free))
    except OSError:
        add("Storage", "Unavailable")

    try:
        connection = socket.create_connection(
            ("1.1.1.1", 443), timeout=3
        )
        connection.close()
        add("Internet", "Connected")
    except OSError:
        add("Internet", "Disconnected")

    add(
        "Termux API",
        "Installed" if shutil.which("termux-battery-status") else "Not found"
    )

    add("Date", datetime.now().isoformat(timespec="seconds"))

    filename = Path.cwd() / "AVINAV_Diagnostics.txt"

    try:
        filename.write_text(
            "AVINAV DIAGNOSTICS REPORT\n"
            + "=" * 46 + "\n"
            + "\n".join(report) + "\n"
        )

        print("\nReport saved:", filename)

    except OSError as error:
        print("Could not save report:", error)

    pause()


# =============== PYTHON PACKAGE MANAGER ===============

def package_manager():
    pip = [sys.executable, "-m", "pip"]

    while True:
        clear()
        banner()

        print(CYAN + "\nPYTHON PACKAGE MANAGER" + RESET)
        print("[1] List packages")
        print("[2] Install package")
        print("[3] Uninstall package")
        print("[0] Back")

        choice = input("\nSelect: ")

        if choice == "1":
            subprocess.run(pip + ["list"])
            pause()

        elif choice in ("2", "3"):
            name = input("Package name: ").strip()

            pattern = (
                r"[A-Za-z0-9_.-]+"
                if choice == "3"
                else r"[A-Za-z0-9_.-]+(?:==[A-Za-z0-9_.+-]+)?"
            )

            if not re.fullmatch(pattern, name):
                print("Invalid package name.")
                pause()
                continue

            action = "install" if choice == "2" else "uninstall"

            if input(f"Confirm {action} {name}? (y/n): ").lower() == "y":
                args = ["install", name] if choice == "2" else [
                    "uninstall", "-y", name
                ]

                subprocess.run(
                    pip + args,
                    timeout=180
                )

            pause()

        elif choice == "0":
            break


# =============== INTERNET LATENCY ===============

def latency_tester():
    clear()
    banner()

    print(CYAN + "\nINTERNET LATENCY TESTER" + RESET)
    print("-" * 46)

    for name, host, port in [
        ("Cloudflare", "1.1.1.1", 443),
        ("Google", "8.8.8.8", 443),
    ]:
        print(f"\n{name} ({host})")

        times = []

        for attempt in range(4):
            try:
                start = time.perf_counter()

                connection = socket.create_connection(
                    (host, port), timeout=4
                )

                elapsed = (time.perf_counter() - start) * 1000
                connection.close()

                times.append(elapsed)

                print(f"Attempt {attempt + 1}: {elapsed:.2f} ms")

            except OSError:
                print(f"Attempt {attempt + 1}: Failed")

        if times:
            print("Average:", f"{sum(times) / len(times):.2f} ms")
        else:
            print("Connection unavailable.")

    print("\nThis measures TCP connection latency.")

    pause()


# =============== INTERNET CHECKER ===============

def internet_checker():
    clear()
    banner()

    print(CYAN + "\nINTERNET CHECKER" + RESET)
    print("-" * 46)

    try:
        connection = socket.create_connection(
            ("1.1.1.1", 443), timeout=5
        )
        connection.close()
        print("Internet :", GREEN + "Connected" + RESET)

    except OSError:
        print("Internet :", RED + "Disconnected" + RESET)

    try:
        print("DNS      :", socket.gethostbyname("google.com"))
    except OSError:
        print("DNS      : Unavailable")

    try:
        print("Hostname :", socket.gethostname())
        print("Local IP :", socket.gethostbyname(socket.gethostname()))
    except OSError:
        print("Local IP : Unavailable")

    pause()


# =============== PYTHON INFORMATION ===============

def python_info():
    clear()
    banner()

    print(CYAN + "\nPYTHON INFORMATION" + RESET)
    print("-" * 46)

    print("Version        :", sys.version)
    print("Executable     :", sys.executable)
    print("Platform       :", sys.platform)
    print("Implementation :", platform.python_implementation())

    pause()


# =============== SYSTEM INFORMATION MENU ===============

def system_info():
    actions = {
        "1": basic_info,
        "2": live_monitor,
        "3": battery_info,
        "4": storage_analyzer,
        "5": network_speed,
        "6": process_monitor,
        "7": large_file_finder,
        "8": cpu_temperature,
        "9": device_info,
        "10": diagnostics,
        "11": package_manager,
        "12": latency_tester,
    }

    while True:
        clear()
        banner()

        print(CYAN + "\nSYSTEM INFORMATION" + RESET)
        print("-" * 46)

        options = [
            "Basic System Information",
            "Live System Monitor",
            "Battery Information",
            "Storage Analyzer",
            "Network Speed Test",
            "Running Process Monitor",
            "Large File Finder",
            "CPU Temperature",
            "Device Information",
            "System Diagnostics Report",
            "Python Package Manager",
            "Internet Latency Tester",
        ]

        for number, label in enumerate(options, 1):
            print(f"[{number}] {label}")

        print("[0] Back")

        choice = input("\nSelect option: ")

        if choice == "0":
            return

        action = actions.get(choice)

        if action:
            action()
        else:
            print("Invalid option!")
            time.sleep(1)


# =============== MAIN MENU ===============

def main():
    while True:
        clear()
        banner()

        print(CYAN + "\nMAIN MENU" + RESET)
        print("-" * 46)
        print("[1] System Information")
        print("[2] Internet Checker")
        print("[3] Python Information")
        print("[0] Exit")

        choice = input("\nSelect option: ")

        if choice == "1":
            system_info()

        elif choice == "2":
            internet_checker()

        elif choice == "3":
            python_info()

        elif choice == "0":
            print("\nThank you for using AVINAV!")
            break

        else:
            print("Invalid option!")
            time.sleep(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nAVINAV closed.")
  
