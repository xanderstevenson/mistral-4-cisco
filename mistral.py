import os
import yaml
import paramiko
from datetime import datetime
from mistral_auth import get_mistral_client


# --- SSH Command Execution ---
def ssh_connect_and_run_command(device_ip, username, password, command, timeout=3):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(
            device_ip,
            username=username,
            password=password,
            timeout=timeout,
            banner_timeout=timeout,
            auth_timeout=timeout
        )
        stdin, stdout, stderr = client.exec_command(command, timeout=timeout)
        output = stdout.read().decode()
        return output
    except Exception as e:
        return f"Error: {str(e)}"
    finally:
        client.close()


# --- Load Devices ---
def load_devices(filename="source_of_truth/devices.yaml"):
    try:
        with open(filename, "r") as f:
            return yaml.safe_load(f)["devices"]
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found")
        return []


def test_ssh_connection(device_ip, username, password, timeout=3):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(
            device_ip,
            username=username,
            password=password,
            timeout=timeout,
            banner_timeout=timeout,
            auth_timeout=timeout
        )
        return True
    except Exception:
        return False
    finally:
        client.close()


# --- Collect Device Info ---
def collect_device_info(device):
    commands = [
        "show vrf",
        "show vlan",
        "show memory",
        "show version",
        "show interface",
        "show logging",
    ]

    outputs = {}
    print(f"\n🔌 Collecting device information for {device['name']} ({device['ip']})...")
    
    
    # 🔍 Test connection first
    if not test_ssh_connection(device["ip"], device["username"], device["password"]):
        print(f"❌ Unable to connect to {device['name']} ({device['ip']})")
        return {cmd: "Unable to connect" for cmd in commands}
    
    for command in commands:
        print(f"🔌 Running command: {command}")
        outputs[command] = ssh_connect_and_run_command(
            device["ip"], device["username"], device["password"], command
        )
    return outputs


# --- Aggregate Output ---
def aggregate_device_info(output_dict, device_type):
    num_devices = len(output_dict)

    if num_devices == 1:
        prompt = f"""You are an expert network, automation, platform engineering, and security engineer. Analyze the following outputs from a single device of type '{device_type}'.

        Provide a detailed analysis of this device, including its:

        *   Operational state
        *   Key configurations
        *   Relevant logs
        *   Any potential issues or anomalies.

        Focus on providing actionable recommendations based on your analysis."""
    else:
        prompt = f"""You are an expert network, automation, platform engineering, and security engineer. Analyze the following outputs from multiple devices of type '{device_type}'.

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

    combined_input = prompt.format(device_type=device_type)

    for device_name, device_outputs in output_dict.items():
        combined_input += f"\n\n### {device_name} ###\n"
        for command, output in device_outputs.items():
            combined_input += f"\n\n#### {command} ####\n{output}"
    return combined_input


# --- Analyze with Mistral (Updated for SDK v1.x) ---
def analyze_with_mistral(mistral_client, output):
    try:
        messages = [
            {
                "role": "user",
                "content": output
            }
        ]
        response = mistral_client.chat.complete(
            model="pixtral-12b-2409",  # or another available model
            messages=messages,
            max_tokens=2000
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error analyzing with Mistral: {e}")
        return "Error during analysis"


# --- Save Results to Timestamped YAML ---
def save_output(device_type, outputs, summary):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_dir = os.path.join("output", device_type)
    os.makedirs(output_dir, exist_ok=True)

    output_path = os.path.join(output_dir, f"{timestamp}.yaml")
    with open(output_path, "w") as f:
        yaml.dump(
            {
                "device_type": device_type,
                "timestamp": timestamp,
                "outputs": outputs,
                "summary": summary,
            },
            f,
            default_flow_style=False,
        )
    print(f"💾 Output saved to {output_path}")


# --- Main Execution ---
if __name__ == "__main__":
    devices = load_devices()

    devices_by_type = {}
    for device in devices:
        device_type = device.get("device_type", "unknown")
        if device_type not in devices_by_type:
            devices_by_type[device_type] = []
        devices_by_type[device_type].append(device)

    for device_type, device_list in devices_by_type.items():
        print(f"\n--- Processing devices of type: {device_type} ---\n")

        all_outputs = {}
        for device in device_list:
            all_outputs[device["name"]] = collect_device_info(device)

        print("📚 Aggregating device information...")
        aggregated_input = aggregate_device_info(all_outputs, device_type)

        print("🧠 Talking to Mistral...")
        mistral_client = get_mistral_client()
        summary = analyze_with_mistral(mistral_client, aggregated_input)

        print("\n\n✅ Detailed Summary:\n\n")
        print(summary)

        save_output(device_type, all_outputs, summary)

                # --- Call Collaboration Script ---
        os.system(f"python analyze_and_collab.py {device_type}")

    print("\n\n✅ Done processing all devices.")
