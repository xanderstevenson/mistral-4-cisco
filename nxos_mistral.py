import os
import yaml
import paramiko
from datetime import datetime
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
    combined_input = "You are an expert network, automation, platform engineering, and security engineer. Analyze the following outputs from a Cisco Nexus switch and provide a summary of the device state, configurations, logs, and any potential issues.\n\n"
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

# --- Save Results to Timestamped YAML ---
def save_output(device_name, outputs, summary):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    device_dir = os.path.join("nxos", "output", device_name)
    os.makedirs(device_dir, exist_ok=True)
    
    output_path = os.path.join(device_dir, f"{timestamp}.yaml")
    with open(output_path, "w") as f:
        yaml.dump({"device": device_name, "timestamp": timestamp, "outputs": outputs, "summary": summary}, f, default_flow_style=False)
    
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
