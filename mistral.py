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
def load_devices(filename="source_of_truth/devices.yaml"):  # Changed default filename
    try:
        with open(filename, "r") as f:
            return yaml.safe_load(f)["devices"]
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found")
        return []

# --- Collect Device Info ---
def collect_device_info(device):
    commands = [
        "show vrf",
        "show vlan",
        "show memory",
        "show version",
        "show interface",
        "show logging"
    ]

    outputs = {}
    print(f"🔌 Collecting device information for {device['name']} ({device['ip']})...") # Added device info
    for command in commands:
        print(f"🔌 Running command: {command}")
        try:
            outputs[command] = ssh_connect_and_run_command(device["ip"], device["username"], device["password"], command)
        except Exception as e:
            outputs[command] = f"Error: {str(e)}"
    return outputs

# --- Aggregate Output ---
def aggregate_device_info(output_dict, device_type): # Added device_type
    prompt = f"""You are an expert network, automation, platform engineering, and security engineer. Analyze the following outputs from devices of type '{device_type}'.

    For each individual device, provide a concise summary of its:

    *   Operational state
    *   Key configurations
    *   Relevant logs
    *   Any potential issues or anomalies specific to that device

    After summarizing each device individually, provide a combined analysis that identifies:

    *   Common configurations and settings across all devices of type '{device_type}'.
    *   Any significant deviations from the norm or inconsistencies between devices.
    *   Potential security vulnerabilities or misconfigurations that are present in some devices but not others.
    *   Suggestions for improving consistency, security, and overall operational efficiency across the '{device_type}' device family.

    Focus on providing actionable recommendations based on your analysis."""

    combined_input = prompt # Assign the prompt to combined_input

    for device_name, device_outputs in output_dict.items(): # Iterate through device names and their outputs
        combined_input += f"\n\n### {device_name} ###\n" # Add device name to the aggregated input
        for command, output in device_outputs.items():
            combined_input += f"\n\n#### {command} ####\n{output}"
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
def save_output(device_type, outputs, summary): # Changed to device_type
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_dir = os.path.join("output", device_type) # Changed to device_type
    os.makedirs(output_dir, exist_ok=True)

    output_path = os.path.join(output_dir, f"{timestamp}.yaml")
    with open(output_path, "w") as f:
        yaml.dump({"device_type": device_type, "timestamp": timestamp, "outputs": outputs, "summary": summary}, f, default_flow_style=False) # Changed to device_type

    print(f"💾 Output saved to {output_path}")

# --- Main Pipeline ---
if __name__ == "__main__":
    devices = load_devices()

    # Group devices by device_type
    devices_by_type = {}
    for device in devices:
        device_type = device.get("device_type", "unknown")  # Get device_type, default to "unknown"
        if device_type not in devices_by_type:
            devices_by_type[device_type] = []
        devices_by_type[device_type].append(device)

    # Process each device type
    for device_type, device_list in devices_by_type.items():
        print(f"\n--- Processing devices of type: {device_type} ---\n\n")

        # Collect device information for all devices of this type
        all_outputs = {}
        for device in device_list:
            all_outputs[device["name"]] = collect_device_info(device) # Use device name as key

        # Aggregate the device information
        print("📚 Aggregating device information...")
        aggregated_input = aggregate_device_info(all_outputs, device_type) # Pass device_type

        # Analyze with Mistral
        print("🧠 Talking to Mistral...")
        mistral_client = get_mistral_client()
        summary = analyze_with_mistral(mistral_client, aggregated_input)

        # Print the summary
        print("\n\n✅ Detailed Summary:\n\n")
        print(summary)

        # Save the output
        save_output(device_type, all_outputs, summary) # Pass device_type

    print("\n\n✅ Done processing all devices.")