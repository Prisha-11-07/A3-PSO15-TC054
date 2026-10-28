
import unittest

from fault_scenarios import run_scenario, explain_evidence


class TestFaultScenarios(unittest.TestCase):

    def test_normal_network(self):
        evidence = run_scenario("normal")
        diagnosis = explain_evidence(evidence)

        self.assertTrue(evidence.gateway_reachable)
        self.assertTrue(evidence.dns_resolved)
        self.assertIn("No simulated fault", diagnosis)

    def test_gateway_unreachable(self):
        evidence = run_scenario("gateway_unreachable")
        diagnosis = explain_evidence(evidence)

        self.assertFalse(evidence.gateway_reachable)
        self.assertIn("Gateway reachability failure", diagnosis)

    def test_dns_failure(self):
        evidence = run_scenario("dns_failure")
        diagnosis = explain_evidence(evidence)

        self.assertTrue(evidence.gateway_reachable)
        self.assertFalse(evidence.dns_resolved)
        self.assertIn("DNS resolution failure", diagnosis)

    def test_packet_loss(self):
        evidence = run_scenario("packet_loss")
        diagnosis = explain_evidence(evidence)

        self.assertEqual(evidence.packet_loss_percent, 40.0)
        self.assertIn("High packet loss", diagnosis)

    def test_congestion(self):
        evidence = run_scenario("congestion")
        diagnosis = explain_evidence(evidence)

        self.assertEqual(evidence.average_latency_ms, 250.0)
        self.assertIn("High latency", diagnosis)

    def test_unknown_scenario(self):
        with self.assertRaises(ValueError):
            run_scenario("unknown_scenario")


if __name__ == "__main__":
    unittest.main(verbosity=2)
