YOUTUBE LINK:https://youtu.be/PDM8P7mVPco

# LastMile-DDx: Explainable Home and Last-Mile Connectivity Diagnosis

**Project ID:** A3-PS015-TCOS4\
**Event:** AIORI Hackathon 3\

## Overview

LastMile-DDx is a proposed evidence-based approach to diagnosing home
and last-mile internet connectivity problems. Traditional speed tests
primarily report peak bandwidth under idle conditions, which may not
explain issues affecting real-time applications such as voice calls,
video meetings, and online gaming.

LastMile-DDx measures network behaviour under idle and loaded
conditions, evaluates the collected evidence using transparent rules,
and explains the reasoning behind its diagnosis. When the evidence is
insufficient to isolate a cause, it returns an **Inconclusive** result
rather than forcing a guess.

## Problem Statement

A slow internet connection can have several possible causes, including
gateway reachability problems, DNS failures, packet loss, and
congestion. A single download-speed figure may not distinguish between
them. In addition, users may receive diagnoses that do not show the
evidence supporting the conclusion.

LastMile-DDx aims to: - Diagnose slowness rather than only measure
speed. - Use measurements to help localise the likely fault. - Apply
media-aware baselines for different connection types. - Explain the
rules, measurements, thresholds, and next steps behind each verdict. -
Represent uncertainty honestly when evidence cannot identify a cause.

## Key Measurements

-   **Packet loss:** The percentage of probe packets that do not return.
-   **Round-trip time (RTT):** The time for a probe to reach a
    destination and for its reply to return.
-   **Loaded jitter:** Variation in packet delay while the connection is
    carrying traffic.
-   **DNS delay:** The time required to translate a domain name into an
    IP address.

The system compares relevant measurements at the gateway and a public
IP, checks DNS behaviour, and compares idle and loaded network
conditions.

## Supported Access Media

The proposed diagnostic approach considers four types of internet
access:

-   **Fiber:** Typically has low, stable RTT; local equipment, DNS, or
    congestion can still cause problems.
-   **Cellular (4G/5G):** Results may vary with radio signal conditions,
    mobility, and cell load.
-   **Fixed wireless access (FWA):** Line of sight, obstacles, antenna
    alignment, interference, weather, and capacity may affect
    performance.
-   **Satellite (GEO/LEO):** Expected latency depends on the satellite
    system. High GEO latency alone is not treated as proof of a fault.

Thresholds should be interpreted in the context of the access medium
rather than using one universal baseline.

## Proposed Diagnostic Workflow

1.  **Calibrate the host:** Check CPU load, timer accuracy, and loopback
    behaviour to reduce device-side measurement errors.
2.  **Probe the connection:** Measure gateway and public-IP
    reachability, DNS response, packet loss, and RTT under idle and
    loaded conditions.
3.  **Evaluate candidate causes:** Consider gateway failure, DNS fault,
    random packet loss, congestion, local Wi-Fi link issues, and an
    unknown upstream fault.
4.  **Apply explainable rules:** Use the stored measurements and rule
    logic to eliminate hypotheses that do not match the evidence.
5.  **Generate the result:** Present the verdict, evidence, thresholds,
    ruled-out causes, and recommended next steps. If the cause cannot be
    isolated, return **Inconclusive** and prepare an escalation report.

## Decision Rules Described in the Project

  -----------------------------------------------------------------------
  Rule                    Evidence observed       Intended interpretation
  ----------------------- ----------------------- -----------------------
  R1                      Gateway ping has 100%   Gateway unreachable;
                          loss and ARP fails      investigate the router
                                                  or local link.

  R2                      Gateway and public IP   DNS failure on the
                          are reachable, system   local resolver path.
                          DNS fails, and          
                          alternate DNS succeeds  

  R3                      Idle packet loss is     Random packet loss
                          above the applicable    rather than a
                          media threshold while   congestion signature.
                          RTT remains stable      
                          under load              

  R4                      Idle path is clean and  Congestion or a
                          loaded RTT rises above  bufferbloat-like
                          three times the         signature.
                          baseline                

  R5                      Gateway is reachable,   Inconclusive; escalate
                          but public-IP and DNS   with the evidence
                          checks fail             report.
  -----------------------------------------------------------------------

These rules are the decision logic described in the project
presentation. They should be validated through the planned fault-lab
evaluation before being relied on in a live environment.

## Proposed Architecture

The presentation describes the following components:

-   **Desktop agent UI:** Guided wizard built with Python and PySide6.
-   **Orchestrator:** Coordinates calibration and probe scheduling.
-   **Probe modules:** ICMP, DNS, iperf3 load testing, ARP, and Wi-Fi
    link statistics.
-   **Rule engine:** YAML rules and a hypothesis tracker.
-   **Evidence store:** SQLite storage for replayable test runs.
-   **Report generator:** Jinja2-based PDF and HTML reports.
-   **Controlled fault lab:** Network namespaces, `tc netem`, `dnsmasq`,
    `iptables`, and reversible fault scripts.
-   **Optional pilot collector:** FastAPI service for anonymised
    results.

The stated design principle is that the rule engine reads stored
evidence, allowing a diagnosis to be regenerated and audited. The pilot
collector is optional and is described as receiving anonymised results.

## Evaluation Plan

The project presentation proposes testing with known, reversible fault
scenarios:

-   Gateway unreachable.
-   DNS failure.
-   Induced packet loss.
-   Network congestion.
-   Combined faults, where an Inconclusive result may be appropriate.

The planned evaluation includes **30 or more runs per fault scenario**,
a no-fault baseline to assess false positives, a confusion matrix,
precision and recall, and median time to diagnosis.

These are evaluation plans described in the presentation; this README
does not claim that the tests have already been completed or that
performance results have been achieved.

## Deployment Plan

The proposed sequence is:

1.  Build the network-namespace fault lab and establish clean baselines.
2.  Implement ICMP, DNS, and iperf3 probes, calibration, and the SQLite
    evidence store.
3.  Implement YAML rules, hypothesis tracking, and the guided UI.
4.  Evaluate against injected faults and analyse Inconclusive cases.
5.  Deliver the escalation PDF, live demonstration, pseudocode, and
    final report.

## Important Limitations and Guardrails

-   A diagnosis should be based on recorded evidence, not assumptions.
-   High latency may be normal for some access media, particularly GEO
    satellite.
-   The system should not claim cable damage, ISP-internal faults, or
    Wi-Fi interference without supporting telemetry.
-   A single failed DNS lookup should not be treated as proof of a DNS
    fault; IP reachability and an alternate resolver should also be
    checked.
-   If the evidence cannot distinguish between causes, the system should
    report **Inconclusive** and recommend further testing.

## References

The project presentation cites the following standards and publication:

1.  V. Paxson et al., "Framework for IP Performance Metrics," RFC 2330,
    IETF, May 1998.
2.  G. Almes, S. Kalidindi, and M. Zekauskas, "A One-way Delay Metric
    for IPPM," RFC 2679, September 1999.
3.  G. Almes, S. Kalidindi, and M. Zekauskas, "A One-way Packet Loss
    Metric for IPPM," RFC 2680, September 1999.
4.  G. Almes, S. Kalidindi, and M. Zekauskas, "A Round-trip Delay Metric
    for IPPM," RFC 2681, September 1999.
5.  P. Eardley et al., "A Framework for Large-Scale Measurement of
    Broadband Performance (LMAP)," RFC 7594, September 2015.
6.  B. Constantine et al., "Framework for TCP Throughput Testing," RFC
    6349, August 2011.
7.  J. Gettys and K. Nichols, "Bufferbloat: Dark Buffers in the
    Internet," *ACM Queue*, vol. 9, no. 11, 2011.

## Project Team

-   Dr. Gokulapriya R
-   Prisha S
-   Ramya R

------------------------------------------------------------------------

**Project tagline:** *Diagnose with evidence. Escalate with confidence.*

> **Repository note:** This README is based on the project presentation.
> It documents the proposed design and evaluation plan, not a verified
> implementation status. Add installation commands, configuration
> details, actual test results, screenshots, and contribution/licensing
> information when those project files and details are available.
