# **Emergency Broadcast System with FROST and Nostr**

## Introduction

The Emergency Broadcast System is a decentralized, secure messaging solution designed to broadcast critical alerts during emergencies.

Built using the FROST (Flexible Round-Optimized Schnorr Threshold) signature scheme and the Nostr protocol, this system allows a panel of trusted participants (e.g., 6 members) to collaboratively sign and broadcast messages. A message is only broadcasted if it meets a predefined threshold (e.g., 3 out of 6 signatures), ensuring consensus and authenticity. 

Messages are stored with their signatures for later verification, while only the latest approved message is sent to Nostr relays, making it ideal for emergency communication where trust and timeliness are paramount.
This project is perfect for scenarios requiring secure, distributed decision-making, such as disaster response teams or community alert systems. It’s implemented in Python and Rust, leveraging FROST for threshold signatures and Nostr for decentralized broadcasting.

How to Run the Project from Scratch :-
This guide assumes you’re starting with a brand new laptop (Windows-based, based on PowerShell usage in your examples). It covers everything from installing dependencies to running the project step-by-step. If you’re on macOS or Linux, I’ll note adjustments where needed.

## Prerequisite
You’ll need to have an account on nostrudel(https://nostrudel.ninja/#/) with a private key and install the following tools and dependencies:

**Python Installation:**

**Version**: Python 3.12 (used in your project per maturin develop output).

**Steps:**

1.Download the installer from python.org.

2.Run the installer:

* Check "Add Python 3.12 to PATH" during installation.
* Select "Install Now".

**Verify Installation:**
set PYTHONUTF8=1
python --version

Output should be Python 3.12.x.

**Install Rust:**

**Reason**: The FROST logic is implemented in Rust via lib.rs. 

**Steps:**

(a)	Download and install Rust via (https://rustup.rs/). 
On Windows, download rustup-init.exe, run it, and accept the default installation.

(b)	Verify installation
rustc --version

(c)	Output should be something like rustc 1.x.x.

**Install a Code Editor (Optional)**

**Recommendation:** Visual Studio Code (VS Code)

**Steps:**

1.	Download from code.visualstudio.com.
2.	Install with default settings.
3.	(Optional) Install extensions: "Python" and "Rust Analyzer" for better coding support.

# Project Setup

**Create Project Directory:**

Open a terminal (PowerShell on Windows, Terminal on macOS/Linux)

mkdir FROST_NOSTR_PROJECT

cd FROST_NOSTR_PROJECT

**Set Up a Virtual Environment:**

**Reason:** Keeps Python dependencies isolated.

**Steps:**

python -m venv nostr_proj .\nostr_proj\Scripts\activate # Windows 
_source nostr_proj/bin/activate | macOS/Linux_

You’ll see (nostr_proj) in your prompt.

**Install Python Dependencies**

**Required Packages:** 

* maturin: Builds Rust-Python bindings.
* nostr-sdk: Python SDK for Nostr.

**Steps / commands:**

1. pip install maturin
2. pip install nostr-sdk

Open Visual studio code and open the terminal (command prompt insode VS code)

**Build the Rust Module**

**Steps:**
maturin develop

This compiles lib.rs into a Python module (frostpy) and installs it in your virtual environment. 

Expected output ends with something like Finished dev [unoptimized + debuginfo].

**Running the Project:**

Now that everything is set up, here’s how to run the Emergency Broadcast System:
**Generate Keys:** python cli.py generate --n 6 --t 3

What It Does: Generates 6 key shares with a threshold of 3, saving them to: 
* keys/[1-6]/secret_share.txt (individual shares).
* keys/public_key_package.txt (public key package).
* keys/public_key.txt (group public key).
* •	Check the keys in keys folder

**Submit an Emergency Message:** python cli.py submit --message "Evacuate immediately!"
* This adds the message to messages.txt with a new ID (e.g., 1). 
* Check the message generated inside message.txt

**List Pending Messages:** python cli.py list
* This shows all pending messages in messages.txt

**Sign the Message with Shares**

**Commands:**
* python cli.py sign-partial --id 1 --share keys/1/secret_share.txt
* python cli.py sign-partial --id 1 --share keys/2/secret_share.txt
* python cli.py sign-partial --id 1 --share keys/3/secret_share.txt

Each command adds a participant’s signature to message ID 1 in messages.txt

**Broadcast the Message:** python cli.py broadcast --id 1 --threshold 3

* It reads messages.txt to verify 3 signatures
* It uses keys/[1-3]/secret_share.txt and keys/public_key_package.txt to sign
* It appends to keys/signatures.txt and overwrites keys/latest_signature.txt
* And it finally Runs nostr.py to broadcast to Nostr relays
    
On getting the error below, kindly change the encoding of python to UTF-8 using the command mentioned below:
* set PYTHONUTF8=1


**Files Updated:** 
* messages.txt : Status changes to "broadcasted".
* keys/signatures.txt : Adds new signature entry.
* keys/latest_signature.txt : Stores the latest signature/message pair.

**Verify a Message:** python cli.py verify --message "Evacuate immediately!"

This Checks keys/signatures.txt for the message’s signature and verifies it with keys/public_key.txt.

**Repeat for Another Message:**

Submit, sign, and broadcast another message (e.g., "Power outage in sector 5.") to test the system’s ability to handle multiple messages while only broadcasting the latest to Nostr.

# Project Structure:

After running, your directory should look like:

FROST_NOSTR_PROJECT/

![img.png](img.png)

**Troubleshooting:**
* Rust Build Fails: Ensure Rust is installed (rustc --version) and run maturin develop again.
* Python Module Not Found: Verify the virtual environment is active ((nostr_proj) in prompt) and maturin develop ran successfully.
* Nostr Fails: Check internet connection and ensure relay URLs are valid.

**Notes for macOS/Linux:**
* Replace .\nostr_proj\Scripts\activate with source nostr_proj/bin/activate.
* Use forward slashes (/) in file paths (e.g., keys/1/secret_share.txt).
