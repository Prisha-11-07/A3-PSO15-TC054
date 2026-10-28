
"""
PS-015: Controlled Network Fault Scenarios

These are simulations for safely testing diagnostic rules.
They do not change the computer's real network settings.
"""

from dataclasses import dataclass


@dataclass
class NetworkEvidence:
    scenario: str
    gateway_reachable: bool
    dns_resolved: bool
    packet_loss_percent: float
    average_latency_ms: float
    simulated: bool = True


def run_scenario(scenario_name):
    """Return controlled evidence for a selected lab scenario."""

    scenarios = {
        "normal": NetworkEvidence(
            scenario="Normal network",
            gateway_reachable=True,
            dns_resolved=True,
            packet_loss_percent=0.0,
            average_latency_ms=15.0,
        ),
        "gateway_unreachable": NetworkEvidence(
            scenario="Gateway unreachable",
            gateway_reachable=False,
            dns_resolved=False,
            packet_loss_percent=100.0,
            average_latency_ms=0.0,
        ),
        "dns_failure": NetworkEvidence(
            scenario="DNS failure",
            gateway_reachable=True,
            dns_resolved=False,
            packet_loss_percent=0.0,
            average_latency_ms=18.0,
        ),
        "packet_loss": NetworkEvidence(
            scenario="Induced packet loss",
            gateway_reachable=True,
            dns_resolved=True,
            packet_loss_percent=40.0,
            average_latency_ms=35.0,
        ),
        "congestion": NetworkEvidence(
            scenario="Simulated network congestion",
            gateway_reachable=True,
            dns_resolved=True,
            packet_loss_percent=5.0,
            average_latency_ms=250.0,
        ),
    }

    if scenario_name not in scenarios:
        available = ", ".join(scenarios.keys())
        raise ValueError(
            f"Unknown scenario: {scenario_name}. "
            f"Available scenarios: {available}"
        )

    return scenarios[scenario_name]


def explain_evidence(evidence):
    """Apply transparent rules to simulated measurements."""

    if not evidence.gateway_reachable:
        diagnosis = (
            "Gateway reachability failure: the gateway did not respond "
            "in this simulated test. The underlying cause is not established."
        )

    elif not evidence.dns_resolved:
        diagnosis = (
            "DNS resolution failure: the gateway is reachable, "
            "but the simulated DNS lookup failed."
        )

    elif evidence.packet_loss_percent >= 20:
        diagnosis = (
            "High packet loss observed in the simulation. "
            "The cause cannot be isolated from these measurements alone."
        )

    elif evidence.average_latency_ms >= 200:
        diagnosis = (
            "High latency observed in the simulation. "
            "Congestion is one possible explanation, not a confirmed cause."
        )

    elif evidence.packet_loss_percent > 0:
        diagnosis = (
            "Some packet loss observed in the simulation. "
            "Further tests are needed to isolate the cause."
        )

    else:
        diagnosis = (
            "No simulated fault detected by these basic diagnostic rules."
        )

    return diagnosis


def main():
    scenarios = [
        "normal",
        "gateway_unreachable",
        "dns_failure",
        "packet_loss",
        "congestion",
    ]

    print("=" * 60)
    print("PS-015 NETWORK FAULT SIMULATOR")
    print("SIMULATED EVIDENCE — NOT LIVE NETWORK MEASUREMENTS")
    print("=" * 60)

    for scenario_name in scenarios:
        evidence = run_scenario(scenario_name)
        diagnosis = explain_evidence(evidence)

        print(f"\nScenario: {evidence.scenario}")
        print(f"Gateway reachable: {evidence.gateway_reachable}")
        print(f"DNS resolved: {evidence.dns_resolved}")
        print(f"Packet loss: {evidence.packet_loss_percent}%")
        print(f"Average latency: {evidence.average_latency_ms} ms")
        print(f"Diagnosis: {diagnosis}")
        print("-" * 60)


if __name__ == "__main__":
    main()
