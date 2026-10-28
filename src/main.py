
import tkinter as tk
from tkinter import ttk
import subprocess
import re
import threading
import csv
import sys
from pathlib import Path
from datetime import datetime


PROJECT_DIR = Path(__file__).resolve().parent.parent
HISTORY_FILE = PROJECT_DIR / "diagnostic_history.csv"
LAB_DIR = Path(__file__).resolve().parent / "lab"


def save_diagnostic_history(result_text):
    """Append diagnostic results to the project CSV history."""
    try:
        file_exists = HISTORY_FILE.exists()
        needs_header = (
            not file_exists or HISTORY_FILE.stat().st_size == 0
        )

        with HISTORY_FILE.open(
            "a", newline="", encoding="utf-8"
        ) as file:
            writer = csv.writer(file)

            if needs_header:
                writer.writerow(["Timestamp", "Diagnostic Result"])

            writer.writerow([
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                result_text
            ])

        return f"\n\nHistory saved: {HISTORY_FILE.name}"

    except OSError as error:
        return f"\n\nHistory could not be saved: {error}"


def get_default_gateway():
    """Find the default IPv4 gateway on Windows."""
    try:
        result = subprocess.run(
            ["route", "print", "-4"],
            capture_output=True,
            text=True,
            timeout=5,
            errors="replace"
        )

        for line in result.stdout.splitlines():
            parts = line.split()

            if (
                len(parts) >= 3
                and parts[0] == "0.0.0.0"
                and parts[1] == "0.0.0.0"
            ):
                return parts[2]

    except (subprocess.TimeoutExpired, OSError):
        pass

    return None


def ping_test(target):
    """Measure reachability, packet loss and average latency."""
    try:
        result = subprocess.run(
            ["ping", "-n", "4", "-w", "1500", target],
            capture_output=True,
            text=True,
            timeout=10,
            errors="replace"
        )

        output = result.stdout

        sent_match = re.search(
            r"Sent\s*=\s*(\d+)", output, re.IGNORECASE
        )
        received_match = re.search(
            r"Received\s*=\s*(\d+)", output, re.IGNORECASE
        )
        average_match = re.search(
            r"Average\s*=\s*(\d+)\s*ms", output, re.IGNORECASE
        )
        loss_match = re.search(
            r"\((\d+)%\s*loss\)", output, re.IGNORECASE
        )

        sent = int(sent_match.group(1)) if sent_match else 4
        received = (
            int(received_match.group(1))
            if received_match else None
        )

        if received is None:
            return {
                "target": target,
                "status": "Inconclusive",
                "sent": sent,
                "received": None,
                "loss": None,
                "latency": None
            }

        loss = (
            int(loss_match.group(1))
            if loss_match
            else round((sent - received) / sent * 100)
        )

        latency = (
            int(average_match.group(1))
            if average_match else None
        )

        if received == 0:
            test_status = "No ping replies"
        elif received < sent:
            test_status = "Partially reachable"
        else:
            test_status = "Reachable"

        return {
            "target": target,
            "status": test_status,
            "sent": sent,
            "received": received,
            "loss": loss,
            "latency": latency
        }

    except (subprocess.TimeoutExpired, OSError):
        return {
            "target": target,
            "status": "Inconclusive",
            "sent": 4,
            "received": None,
            "loss": None,
            "latency": None
        }


def dns_test():
    """Check whether google.com resolves to an IP address."""
    try:
        result = subprocess.run(
            ["nslookup", "google.com"],
            capture_output=True,
            text=True,
            timeout=8,
            errors="replace"
        )

        output = result.stdout + result.stderr

        addresses = re.findall(
            r"Address:\s*(\d{1,3}(?:\.\d{1,3}){3})",
            output,
            re.IGNORECASE
        )

        if re.search(
            r"Non-existent domain|can't find|can't resolve",
            output,
            re.IGNORECASE
        ):
            return {"status": "Resolution failed", "address": None}

        if len(addresses) >= 2:
            return {"status": "Resolved", "address": addresses[-1]}

        return {"status": "Inconclusive", "address": None}

    except (subprocess.TimeoutExpired, OSError):
        return {"status": "Inconclusive", "address": None}


def run_gateway_test():
    gateway = get_default_gateway()

    if not gateway:
        return (
            "GATEWAY TEST\n\n"
            "Result: Inconclusive\n"
            "The default gateway could not be identified."
        )

    data = ping_test(gateway)

    if data["received"] is None:
        return (
            "GATEWAY TEST\n\n"
            f"Gateway: {gateway}\n"
            "Result: Inconclusive\n"
            "Usable ping statistics were unavailable."
        )

    latency = (
        f"{data['latency']} ms"
        if data["latency"] is not None
        else "Unavailable"
    )

    return (
        "GATEWAY TEST\n\n"
        f"Gateway: {gateway}\n"
        f"Result: {data['status']}\n"
        f"Packets received: {data['received']}/{data['sent']}\n"
        f"Packet loss: {data['loss']}%\n"
        f"Average latency: {latency}"
    )


def run_dns_test():
    data = dns_test()

    if data["address"]:
        return (
            "DNS TEST\n\n"
            "Domain: google.com\n"
            "Result: Resolved\n"
            f"IP address: {data['address']}\n\n"
            "DNS resolution succeeded for this lookup."
        )

    return (
        "DNS TEST\n\n"
        "Domain: google.com\n"
        f"Result: {data['status']}\n"
        "A repeat lookup may be needed."
    )


def run_internet_test():
    data = ping_test("1.1.1.1")

    if data["received"] is None:
        return (
            "INTERNET REACHABILITY TEST\n\n"
            "Result: Inconclusive\n"
            "Usable ping statistics were unavailable."
        )

    latency = (
        f"{data['latency']} ms"
        if data["latency"] is not None
        else "Unavailable"
    )

    return (
        "INTERNET REACHABILITY TEST\n\n"
        f"Target: {data['target']}\n"
        f"Result: {data['status']}\n"
        f"Packets received: {data['received']}/{data['sent']}\n"
        f"Packet loss: {data['loss']}%\n"
        f"Average latency: {latency}\n\n"
        "A missing ping reply alone does not prove "
        "internet access is unavailable."
    )


def run_combined_diagnosis():
    """Compare live tests using transparent, cautious rules."""
    gateway = get_default_gateway()

    if not gateway:
        return (
            "COMBINED DIAGNOSIS\n\n"
            "Outcome: Inconclusive\n"
            "Evidence: Default gateway was not identified."
        )

    gateway_data = ping_test(gateway)
    internet_data = ping_test("1.1.1.1")
    dns_data = dns_test()

    gateway_ok = gateway_data["received"] == 4
    internet_ok = (
        internet_data["received"] is not None
        and internet_data["received"] > 0
    )
    dns_ok = dns_data["status"] == "Resolved"

    gateway_loss = (
        f"{gateway_data['loss']}%"
        if gateway_data["loss"] is not None else "Unavailable"
    )
    internet_loss = (
        f"{internet_data['loss']}%"
        if internet_data["loss"] is not None else "Unavailable"
    )

    evidence = (
        "COMBINED DIAGNOSIS — LIVE MEASUREMENTS\n\n"
        f"Gateway ({gateway}): {gateway_data['status']}\n"
        f"Gateway packet loss: {gateway_loss}\n"
        f"Public IP (1.1.1.1): {internet_data['status']}\n"
        f"Public IP packet loss: {internet_loss}\n"
        f"DNS (google.com): {dns_data['status']}\n\n"
    )

    if not gateway_ok:
        conclusion = (
            "Outcome: Inconclusive — investigate local connectivity.\n"
            "Reason: The gateway did not return all four replies. "
            "Ping filtering or intermittent packet loss may explain this."
        )
    elif not dns_ok and internet_ok:
        conclusion = (
            "Outcome: Possible DNS issue.\n"
            "Evidence: The gateway and public IP responded, but "
            "the domain lookup did not return a clear answer.\n"
            "The DNS cause is not confirmed; repeat the lookup."
        )
    elif internet_ok and dns_ok:
        conclusion = (
            "Outcome: Basic connectivity checks passed.\n"
            "Evidence: The gateway and public IP responded, "
            "and the domain resolved.\n"
            "This does not guarantee every service is working."
        )
    else:
        conclusion = (
            "Outcome: Inconclusive — more evidence is required.\n"
            "The current measurements do not isolate a specific cause."
        )

    return evidence + conclusion


def run_lab_simulation():
    """Run the controlled, simulated fault scenarios."""
    simulator_file = LAB_DIR / "fault_scenarios.py"

    if not simulator_file.exists():
        return (
            "LAB SIMULATION ERROR\n\n"
            "The simulator file was not found.\n"
            "Expected location:\n"
            f"{simulator_file}"
        )

    try:
        result = subprocess.run(
            [sys.executable, str(simulator_file)],
            capture_output=True,
            text=True,
            timeout=15,
            cwd=str(PROJECT_DIR),
            errors="replace"
        )

        output = result.stdout.strip()

        if result.returncode != 0:
            details = result.stderr.strip() or "No error details provided."
            return (
                "LAB SIMULATION ERROR\n\n"
                "The simulator did not finish successfully.\n\n"
                f"{details}"
            )

        if not output:
            return (
                "LAB SIMULATION ERROR\n\n"
                "The simulator returned no output."
            )

        return (
            "PS-015 CONTROLLED LAB SIMULATION\n"
            "IMPORTANT: ALL VALUES BELOW ARE SIMULATED.\n"
            "They are not live network measurements.\n\n"
            + output
        )

    except subprocess.TimeoutExpired:
        return (
            "LAB SIMULATION ERROR\n\n"
            "The simulator exceeded the 15-second time limit."
        )
    except OSError as error:
        return (
            "LAB SIMULATION ERROR\n\n"
            f"Could not start the simulator: {error}"
        )


def run_test_in_background(test_function):
    status.config(text="Running diagnostic... Please wait.")
    set_buttons("disabled")

    def worker():
        try:
            result = test_function()
            history_message = save_diagnostic_history(result)
            result += history_message
        except Exception as error:
            result = (
                "TEST ERROR\n\n"
                "The diagnostic did not complete.\n"
                f"Details: {error}"
            )

        root.after(0, lambda: show_result(result))

    threading.Thread(target=worker, daemon=True).start()


def set_buttons(state):
    for button in all_buttons:
        button.config(state=state)


def show_result(result):
    status.config(text=result)
    set_buttons("normal")


def main():
    global root, status, all_buttons

    root = tk.Tk()
    root.title("PS-015: Connectivity Diagnosis")
    root.geometry("800x760")
    root.minsize(650, 600)

    ttk.Label(
        root,
        text="PS-015: Connectivity Diagnosis",
        font=("Segoe UI", 18, "bold")
    ).pack(pady=(18, 5))

    ttk.Label(
        root,
        text="Explainable Home and Last-Mile Connectivity Diagnosis",
        font=("Segoe UI", 10)
    ).pack(pady=5)

    status = ttk.Label(
        root,
        text="Ready to run a network diagnostic.",
        font=("Consolas", 10),
        justify="left",
        anchor="nw",
        wraplength=740
    )
    status.pack(
        fill="both",
        expand=True,
        pady=15,
        padx=20
    )

    gateway_button = ttk.Button(
        root,
        text="Test Default Gateway",
        command=lambda: run_test_in_background(run_gateway_test)
    )
    gateway_button.pack(pady=4)

    dns_button = ttk.Button(
        root,
        text="Test DNS",
        command=lambda: run_test_in_background(run_dns_test)
    )
    dns_button.pack(pady=4)

    internet_button = ttk.Button(
        root,
        text="Test Internet Reachability",
        command=lambda: run_test_in_background(run_internet_test)
    )
    internet_button.pack(pady=4)

    combined_button = ttk.Button(
        root,
        text="Run Combined Diagnosis",
        command=lambda: run_test_in_background(run_combined_diagnosis)
    )
    combined_button.pack(pady=4)

    lab_button = ttk.Button(
        root,
        text="Run Lab Simulation (5 Scenarios)",
        command=lambda: run_test_in_background(run_lab_simulation)
    )
    lab_button.pack(pady=8)

    all_buttons = [
        gateway_button,
        dns_button,
        internet_button,
        combined_button,
        lab_button
    ]

    ttk.Label(
        root,
        text="Prototype | Live measurements and simulated tests are separate",
        font=("Segoe UI", 9)
    ).pack(side="bottom", pady=12)

    root.mainloop()


if __name__ == "__main__":
    main()
