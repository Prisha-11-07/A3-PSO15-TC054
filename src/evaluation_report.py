
"""
PS-015 Evidence-Based Evaluation Report

Evaluates the project's five controlled simulated scenarios.
All results are simulated and must not be presented as live
network measurements.
"""

import csv
import sys
from datetime import datetime
from pathlib import Path

# Locate the project and simulator.
PROJECT_DIR = Path(__file__).resolve().parent.parent
LAB_DIR = Path(__file__).resolve().parent / "lab"

# Allow importing fault_scenarios.py from the lab folder.
sys.path.insert(0, str(LAB_DIR))

from fault_scenarios import run_scenario, explain_evidence


REPORT_FILE = PROJECT_DIR / "evaluation_report.csv"


SCENARIOS = [
    {
        "name": "normal",
        "expected_text": "No simulated fault",
        "expected_gateway": True,
        "expected_dns": True,
        "expected_loss": 0.0,
        "expected_latency": 15.0,
    },
    {
        "name": "gateway_unreachable",
        "expected_text": "Gateway reachability failure",
        "expected_gateway": False,
        "expected_dns": False,
        "expected_loss": 100.0,
        "expected_latency": 0.0,
    },
    {
        "name": "dns_failure",
        "expected_text": "DNS resolution failure",
        "expected_gateway": True,
        "expected_dns": False,
        "expected_loss": 0.0,
        "expected_latency": 18.0,
    },
    {
        "name": "packet_loss",
        "expected_text": "High packet loss",
        "expected_gateway": True,
        "expected_dns": True,
        "expected_loss": 40.0,
        "expected_latency": 35.0,
    },
    {
        "name": "congestion",
        "expected_text": "High latency",
        "expected_gateway": True,
        "expected_dns": True,
        "expected_loss": 5.0,
        "expected_latency": 250.0,
    },
]


def evaluate_scenario(scenario):
    """Compare simulator output with expected controlled evidence."""

    evidence = run_scenario(scenario["name"])
    diagnosis = explain_evidence(evidence)

    checks = [
        evidence.gateway_reachable == scenario["expected_gateway"],
        evidence.dns_resolved == scenario["expected_dns"],
        evidence.packet_loss_percent == scenario["expected_loss"],
        evidence.average_latency_ms == scenario["expected_latency"],
        scenario["expected_text"].lower() in diagnosis.lower(),
        evidence.simulated is True,
    ]

    passed = all(checks)

    return {
        "scenario": evidence.scenario,
        "evidence_type": "SIMULATED",
        "gateway_reachable": evidence.gateway_reachable,
        "dns_resolved": evidence.dns_resolved,
        "packet_loss_percent": evidence.packet_loss_percent,
        "average_latency_ms": evidence.average_latency_ms,
        "expected_diagnosis": scenario["expected_text"],
        "actual_diagnosis": diagnosis,
        "result": "PASS" if passed else "FAIL",
        "checks_passed": sum(checks),
        "checks_total": len(checks),
        "limitations": (
            "Controlled simulation only; not live network evidence. "
            "Does not establish physical or ISP-internal root cause."
        ),
    }


def main():
    results = []

    print("=" * 72)
    print("PS-015 EVIDENCE-BASED EVALUATION")
    print("SIMULATED SCENARIOS — NOT LIVE NETWORK MEASUREMENTS")
    print("=" * 72)

    for scenario in SCENARIOS:
        result = evaluate_scenario(scenario)
        results.append(result)

        print(f"\nScenario: {result['scenario']}")
        print(f"Evidence type: {result['evidence_type']}")
        print(f"Gateway reachable: {result['gateway_reachable']}")
        print(f"DNS resolved: {result['dns_resolved']}")
        print(f"Packet loss: {result['packet_loss_percent']}%")
        print(f"Average latency: {result['average_latency_ms']} ms")
        print(f"Expected diagnosis: {result['expected_diagnosis']}")
        print(f"Actual diagnosis: {result['actual_diagnosis']}")
        print(
            f"Rule checks: {result['checks_passed']}/"
            f"{result['checks_total']}"
        )
        print(f"Evaluation: {result['result']}")

    fieldnames = [
        "timestamp",
        "scenario",
        "evidence_type",
        "gateway_reachable",
        "dns_resolved",
        "packet_loss_percent",
        "average_latency_ms",
        "expected_diagnosis",
        "actual_diagnosis",
        "result",
        "checks_passed",
        "checks_total",
        "limitations",
    ]

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        with REPORT_FILE.open(
            "w", newline="", encoding="utf-8"
        ) as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()

            for result in results:
                writer.writerow({
                    "timestamp": timestamp,
                    **result,
                })

        passed = sum(r["result"] == "PASS" for r in results)
        failed = len(results) - passed

        print("\n" + "=" * 72)
        print(f"Scenarios evaluated: {len(results)}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print(f"CSV report saved to: {REPORT_FILE}")
        print("=" * 72)

    except OSError as error:
        print(f"\nCould not save the CSV report: {error}")


if __name__ == "__main__":
    main()
