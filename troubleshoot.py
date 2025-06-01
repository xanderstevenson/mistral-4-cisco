import os
import yaml
import argparse
import glob
from datetime import datetime
from mistral_auth import get_mistral_client
import time  # For handling streaming

def create_troubleshooting_agent(client):
    try:
        agent = client.beta.agents.create(
            model="pixtral-12b-2409",
            description="An expert network troubleshooting assistant for Cisco devices.",
            name="Network Troubleshooter",
            instructions=(
                "You are an expert network troubleshooting assistant. "
                "You analyze network device outputs and provide specific, actionable troubleshooting steps. "
                "Focus on providing practical guidance that a network engineer can implement."
            ),
            completion_args={
                "temperature": 0.3,
                "top_p": 0.95,
            }
        )
        print(f"✅ Created agent with ID: {agent.id}")
        return agent.id
    except Exception as e:
        print(f"Error creating agent: {e}")
        return None

def get_most_recent_yaml_files(device_type, n=3):
    output_dir = os.path.join("output", device_type)
    if not os.path.exists(output_dir):
        print(f"❌ Error: Output directory '{output_dir}' not found.")
        return []

    files = glob.glob(os.path.join(output_dir, "*.yaml"))
    files.sort(key=os.path.getmtime, reverse=True)
    return files[:n]

def choose_yaml_file(device_type):
    files = get_most_recent_yaml_files(device_type)

    if not files:
        print(f"No YAML files found in output/{device_type}")
        return None

    print(f"\n📂 Most Recent Output Files in output/{device_type}:")
    for i, filepath in enumerate(files):
        filename = os.path.basename(filepath)
        print(f"{i + 1}: {filename}")

    while True:
        try:
            choice = int(input("Select a file number: ")) - 1
            if 0 <= choice < len(files):
                return files[choice]
            else:
                print("Invalid choice. Please try again.")
        except ValueError:
            print("Invalid input. Please enter a number.")

def troubleshoot_with_mistral(mistral_client, agent_id, yaml_path, user_question):
    try:
        with open(yaml_path, "r") as f:
            data = yaml.safe_load(f)

        if data is None:
            print(f"❌ Error: Could not load YAML data from {yaml_path}")
            return

        device_type = data.get("device_type", "unknown")
        outputs = data.get("outputs", {})
        summary = data.get("summary", "No summary available")

        # Format and truncate raw output to avoid prompt overflow
        outputs_str = yaml.dump(outputs, default_flow_style=False)
        max_output_chars = 3000
        if len(outputs_str) > max_output_chars:
            outputs_str = outputs_str[:max_output_chars] + "\n... [truncated due to token limit]"

        prompt = f"""You are an expert network troubleshooting assistant. A network engineer has provided you with the following data from devices of type '{device_type}', along with an initial AI-generated summary.


Initial AI Summary:
{summary}

Raw Device Outputs:
{outputs_str}

The engineer has the following question:
{user_question}

Provide specific, actionable troubleshooting steps to address the engineer's question, referencing the raw device outputs as needed."""

        response = mistral_client.chat.complete(
            model="mistral-small",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=2000
        )

        troubleshooting_guidance = response.choices[0].message.content.strip()

        print("\n✅ Troubleshooting Guidance:\n")
        print(troubleshooting_guidance)

    except FileNotFoundError:
        print(f"❌ Error: File '{yaml_path}' not found")
    except yaml.YAMLError as e:
        print(f"❌ Error: Could not parse YAML file: {e}")
    except Exception as e:
        print(f"❌ Error during Mistral analysis: {e}")

if __name__ == "__main__":
    mistral_client = get_mistral_client()

    agent_id = create_troubleshooting_agent(mistral_client)
    if agent_id:
        device_type = input("Enter the device type (e.g., nxos, iosxe): ")
        yaml_path = choose_yaml_file(device_type)

        if yaml_path:
            user_question = input("What would you like help troubleshooting? ")
            troubleshoot_with_mistral(mistral_client, agent_id, yaml_path, user_question)
        else:
            print("❌ No YAML file selected. Exiting.")
    else:
        print("❌ Failed to create troubleshooting agent. Exiting.")
