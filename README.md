# pv204_project 
# **Secure Emergency Broadcast System**

## Overview

The Secure Emergency Broadcast System is designed to reliably sign, authenticate, and broadcast critical messages to intended recipients. By leveraging FROST (Flexible Round-Optimized Schnorr Threshold Signatures) and the Nostr Network, this system ensures secure, tamper-proof, and decentralized emergency communications.

## Features

**Threshold Key Generation**: Uses the FROST protocol to distribute cryptographic keys among multiple participants.

**Secure Signing Mechanism**: Requires a minimum threshold of participants to collaboratively sign messages.

**Tamper-Proof Broadcast**: Messages are signed using aggregated Schnorr signatures and distributed via the decentralized Nostr Network.

**Fault-Tolerance**: Can operate even if some participants are unavailable.

**Command-Line Interface (CLI)**: Simple and secure way for authorized users to sign messages and verify authenticity.

