# Mistral AI Agent to Interact with Cisco Devices

## Objective
This guide will walk you through setting up the Mistral AI Agent to interact with Cisco Nexus 9000 series switches. We'll use the Mistral API for intelligent analysis of device outputs like show vrf, show vlan, and show logging.

## Prerequisites
Before starting, ensure you have the following:

A Cisco Nexus 9000 series switch for querying device information.

A Mistral AI account and API key to interact with the Mistral model.

A Python environment set up with necessary libraries installed.

## Set Up

Step 1: Set Up Mistral AI Agent
1.1 Create Mistral Account
Go to Mistral AI and sign up for an account.

Set up Multi-Factor Authentication (MFA) and complete the setup.

1.2 Generate an API Key
Navigate to Mistral Console.

Go to API Keys and click Create New Key.

Copy the generated API key. You'll need this to authenticate with Mistral's API.

1.3 Set Up the Environment
You need a virtual environment to store and manage your Python dependencies. You can create a virtual environment using either venv or poetry.

Using venv
bash
Copy
Edit
mkdir mistral
cd mistral
python3 -m venv venv
source venv/bin/activate
Using poetry
bash
Copy
Edit
mkdir mistral
cd mistral
poetry init
poetry add mistralai
poetry install
1.4 Install Mistral Python Client
Install the Mistral AI Python client to interact with the Mistral API.

bash
Copy
Edit
pip install mistralai
1.5 Set Up Authentication
Create a file called mistral_auth.py in the root directory of the project. This file will handle authentication with Mistral.

python
Copy
Edit
import os
import mistralai

def get_mistral_client():
    api_key = os.getenv("MISTRAL_API_KEY")
    if not api_key:
        raise ValueError("MISTRAL_API_KEY is not set.")
    return mistralai.Mistral(api_key=api_key)
Set API Key
In your terminal, export the Mistral API key:

bash
Copy
Edit
export MISTRAL_API_KEY=your_mistral_api_key_here
Verify the environment variable:

bash
Copy
Edit
echo $MISTRAL_API_KEY
Step 2: Install Required Python Libraries
Use pip to install the necessary dependencies for interacting with the Cisco Nexus switch and processing data.

bash
Copy
Edit
pip install paramiko
pip install --upgrade mistralai
pip install langchain openai faiss-cpu beautifulsoup4 langchain-community tiktoken
Step 3: Set Up Device List (nxos_devices.yaml)
Create a YAML file that holds the list of devices you want to interact with.

Example nxos_devices.yaml
yaml
Copy
Edit
devices:
  - name: Nexus9k-101
    ip: 192.168.254.101
    username: cisco
    password: cisco
This file will be used by the main script (nxos_mistral.py) to select devices for querying.

Step 4: Main Script (nxos_mistral.py)
Explanation of the Script
The script nxos_mistral.py connects to Cisco Nexus switches, collects output from various show commands, and then sends the collected data to Mistral for analysis.

Features:
SSH Connection: Connects to devices using SSH to run commands.

Device Selection: Allows the user to select a device from the list in nxos_devices.yaml.

Command Execution: Runs a set of predefined show commands.

Mistral Analysis: Sends the command outputs to Mistral for intelligent analysis.

Results Saving: Saves the results in a directory named after the device, with a timestamped filename.

Code
python
Copy
Edit
import os
import yaml
import paramiko
from mistral_auth import get_mistral_client

# --- SSH Command Execution ---
def ssh_connect_and_run_command(device_ip, username, password, command):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(device_ip, username=username, password=password)
    stdin, stdout, stderr = client.exec_command(command)
    output = stdout.read().decode()
    client.close()
    return output

# --- Load Devices ---
def load_devices(filename="nxos/nxos_devices.yaml"):
    with open(filename, "r") as f:
        return yaml.safe_load(f)["devices"]

# --- Select Device ---
def choose_device(devices):
    print("📟 Available Devices:")
    for idx, dev in enumerate(devices):
        print(f"{idx + 1}: {dev['name']} ({dev['ip']})")
    choice = int(input("Select device number: ")) - 1
    return devices[choice]

# --- Collect Device Info ---
def collect_device_info(device):
    commands = [
        "show vrf",
        "show vlan",
        "show memory",
        "show version",
        "show interface",
        "show logging"  # ✅ Added back now that we’re using Codestral-Mamba
    ]
    
    outputs = {}
    print("🔌 Collecting device information...")
    for command in commands:
        print(f"🔌 Running command: {command}")
        try:
            outputs[command] = ssh_connect_and_run_command(device["ip"], device["username"], device["password"], command)
        except Exception as e:
            outputs[command] = f"Error: {str(e)}"
    return outputs

# --- Aggregate Output ---
def aggregate_device_info(output_dict):
    combined_input = "You are a network engineer. Analyze the following outputs from a Cisco Nexus switch and provide a summary of the device state, configurations, logs, and any potential issues.\n\n"
    for command, output in output_dict.items():
        combined_input += f"\n\n### {command} ###\n{output}"
    return combined_input

# --- Analyze with Mistral (Codestral-Mamba) ---
def analyze_with_mistral(mistral_client, output):
    try:
        response = mistral_client.chat.complete(
            model="pixtral-12b-2409",
            messages=[{"role": "user", "content": output}],
            max_tokens=2000
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error analyzing with Mistral: {e}")
        return "Error during analysis"

# --- Save Results to YAML ---
def save_output(device_name, outputs, summary):
    os.makedirs("output", exist_ok=True)
    output_path = os.path.join("nxos/output", f"{device_name}_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.yaml")
    with open(output_path, "w") as f:
        yaml.dump({"outputs": outputs, "summary": summary}, f, default_flow_style=False)
    print(f"💾 Output saved to {output_path}")

# --- Main Pipeline ---
if __name__ == "__main__":
    devices = load_devices()
    selected_device = choose_device(devices)
    
    outputs = collect_device_info(selected_device)
    print("📚 Aggregating device information...")
    aggregated_input = aggregate_device_info(outputs)

    print("🧠 Talking to Mistral...")
    mistral_client = get_mistral_client()
    summary = analyze_with_mistral(mistral_client, aggregated_input)

    print("\n✅ Detailed Summary:")
    print(summary)

    save_output(selected_device["name"], outputs, summary)
Step 5: Running the Script
Ensure that you have the correct API key set up as an environment variable:

bash
Copy
Edit
export MISTRAL_API_KEY=your_mistral_api_key_here
Run the script using Python:

bash
Copy
Edit
python nxos_mistral.py
The script will:

Prompt you to select a device

Collect outputs from show commands

Send the data to Mistral for analysis

Save the results in nxos/output with a timestamp

Additional Setup
Automation: You can automate this script to run at regular intervals using cron or other task schedulers.

Slack/Email Notifications: Modify the script to send output summaries to Slack or via email if needed.

This is a simple yet powerful tool that integrates Mistral AI with your Cisco Nexus switches. Let me know if you need further enhancements or adjustments!
