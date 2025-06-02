import os
import yaml
import glob
import requests
from dotenv import load_dotenv
from mistralai import Mistral  # NEW import style

load_dotenv()

MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
AGENT_ID_FILE = "agent_id.txt"
CONVERSATION_ID_FILE = "conversation_id.txt"

def get_mistral_client():
    api_key = os.getenv("MISTRAL_API_KEY")
    if not api_key:
        raise ValueError("MISTRAL_API_KEY environment variable is not set.")
    return Mistral(api_key=api_key)

def save_agent_id(agent_id):
    with open(AGENT_ID_FILE, "w") as f:
        f.write(agent_id)

def load_agent_id():
    if os.path.exists(AGENT_ID_FILE):
        with open(AGENT_ID_FILE, "r") as f:
            return f.read().strip()
    return None

def save_conversation_id(conversation_id):
    with open(CONVERSATION_ID_FILE, "w") as f:
        f.write(conversation_id)

def load_conversation_id():
    if os.path.exists(CONVERSATION_ID_FILE):
        with open(CONVERSATION_ID_FILE, "r") as f:
            return f.read().strip()
    return None

def create_network_architect_agent(client):
    try:
        agent = client.beta.agents.create(
            model="pixtral-12b-2409",
            description="Expert network engineer and security architect agent.",
            name="Network Architect Assistant",
            instructions=(
                "You are a helpful expert network engineering and security architect who can diagnose and troubleshoot network issues extremely well, "
                "including anticipating possible issues in the future. You will be coordinating actions among team members in order to keep the network "
                "up and running in good health at all times. When asked a question, provide a clear, direct answer without adding extra action plans or long explanations unless specifically requested. If you don’t have enough info, ask for clarification instead of assuming. Keep your responses concise and focused."
            ),
            completion_args={
                "temperature": 0.3,
                "top_p": 0.95,
            },
        )
        print(f"✅ Created agent with ID: {agent.id}")
        return agent.id
    except Exception as e:
        print(f"❌ Error creating agent: {e}")
        return None

WEBEX_TOKEN = os.getenv("WEBEX_BOT_TOKEN")
WEBEX_SPACE = os.getenv("WEBEX_SPACE")
ALEXANDER_WEBEX_ID = os.getenv("ALEXANDER_WEBEX_ID")

SEVERITY_KEYWORDS = [
    "CRITICAL", "FAILURE", "OUTAGE", "DOWN", "MAJOR ISSUE",
    "HIGH IMPACT", "DATA LOSS", "UNABLE TO CONNECT", "NOT RESPONSIVE"
]

def get_latest_yaml(device_type):
    output_dir = os.path.join("output", device_type)
    files = glob.glob(os.path.join(output_dir, "*.yaml"))
    files.sort(key=os.path.getmtime, reverse=True)
    return files[0] if files else None

def load_summary_from_yaml(path):
    with open(path, "r") as f:
        data = yaml.safe_load(f)
        return (
            data.get("summary", ""),
            data.get("timestamp", ""),
            data.get("device_type", "unknown"),
        )

def is_critical(summary):
    summary_tail = summary[-2000:].upper()
    return any(keyword in summary_tail for keyword in SEVERITY_KEYWORDS)



def extract_agent_reply(response):
    # Safely extract the agent's reply content from the response object
    agent_reply = None
    if hasattr(response, "outputs") and response.outputs:
        agent_reply = response.outputs[0].content
    return agent_reply


def send_agent_update(client, agent_id, summary, device_type, timestamp):
    try:
        input_text = (
            f"A network scan of Cisco `{device_type}` devices was completed at `{timestamp}`. "
            f"Here is the raw issue summary:\n\n{summary}\n\n"
            "Please identify the most critical issues first, especially unreachable devices, outages, or total failures. "
            "Summarize key points in priority order. Avoid repeating similar issues unless they impact different systems. "
            "Keep the summary focused and high signal."
        )


        conversation_id = load_conversation_id()

        if conversation_id:
            response = client.beta.conversations.append(
                conversation_id=conversation_id,
                inputs=input_text,
                store=True
            )
        else:
            response = client.beta.conversations.start(
                agent_id=agent_id,
                inputs=input_text,
                store=True
            )

        conversation_id = getattr(response, "conversation_id", None)
        if conversation_id:
            save_conversation_id(conversation_id)

        agent_reply = extract_agent_reply(response)

        print(f"🧠 Agent received update for {device_type}.")
        print(f"🤖 Agent reply:\n{agent_reply}")

        return conversation_id

    except Exception as e:
        print(f"⚠️ Failed to update agent: {e}")
        return None




def send_webex_message(recipient, message, is_room=False):
    url = "https://webexapis.com/v1/messages"
    headers = {
        "Authorization": f"Bearer {WEBEX_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {"markdown": message}
    if is_room:
        payload["roomId"] = recipient
    else:
        payload["toPersonId"] = recipient

    response = requests.post(url, headers=headers, json=payload)
    if response.status_code != 200:
        print(f"❌ Failed to send Webex message: {response.status_code} {response.text}")

def interactive_chat(client, agent_id):
    conversation_id = load_conversation_id()
    print("\n💬 Starting interactive chat with the agent. Type 'exit' or 'quit' to stop.\n")

    while True:
        user_input = input("You: ")
        if user_input.strip().lower() in ["exit", "quit"]:
            print("🛑 Chat ended.")
            break

        try:
            if conversation_id:
                response = client.beta.conversations.append(
                    conversation_id=conversation_id,
                    inputs=user_input,
                    store=True
                )
            else:
                response = client.beta.conversations.start(
                    agent_id=agent_id,
                    inputs=user_input,
                    store=True
                )
            conversation_id = getattr(response, "conversation_id", None)
            if conversation_id:
                save_conversation_id(conversation_id)

            agent_reply = extract_agent_reply(response)
            print(f"Agent: {agent_reply}\n")

        except Exception as e:
            print(f"⚠️ Error during chat: {e}")

def main(device_type):
    mistral_client = get_mistral_client()

    agent_id = load_agent_id()
    if not agent_id:
        print("No saved agent ID found. Creating a new network architect agent...")
        agent_id = create_network_architect_agent(mistral_client)
        if agent_id:
            save_agent_id(agent_id)
        else:
            print("❌ Could not create agent; aborting.")
            return

    latest_yaml = get_latest_yaml(device_type)
    if not latest_yaml:
        print(f"❌ No YAML files found for {device_type}")
        return

    yaml_filename = os.path.basename(latest_yaml)
    chat_link = os.getenv("LE_CHAT_URL")
    summary, timestamp, device_type_loaded = load_summary_from_yaml(latest_yaml)

    critical_issue_found = is_critical(summary)

    send_agent_update(mistral_client, agent_id, summary, device_type_loaded, timestamp)

    short_issue = (
        "⚠️ Critical issue detected — Alexander has been notified directly."
        if critical_issue_found else "✅ No major issues detected."
    )

    team_msg = f"""✅ **Network Analysis Completed**  
**Device Type**: `{device_type_loaded}`  
**Timestamp**: `{timestamp}`  
{short_issue}  
📁 **Report**: `output/{device_type_loaded}/{yaml_filename}`  
💬 [Open La Chat]({chat_link})
"""

    send_webex_message(WEBEX_SPACE, team_msg, is_room=True)

    if critical_issue_found:
        summary_tail = summary[-2000:]
        matching_lines = [
            line.strip()
            for line in summary_tail.splitlines()
            if any(keyword in line.upper() for keyword in SEVERITY_KEYWORDS)
        ]
        context_excerpt = (
            "\n".join(matching_lines[:5]) if matching_lines else "Critical indicators found in summary tail."
        )
        critical_msg = f"""🚨 **Critical Network Issue Detected**  
A major issue was found during the analysis of `{device_type_loaded}` devices at `{timestamp}`.  
🔍 **Detected Indicators**:  
{context_excerpt}  
🗂 **Report**: `output/{device_type_loaded}/{yaml_filename}`  
💬 [Discuss in La Chat]({chat_link})
"""
        send_webex_message(ALEXANDER_WEBEX_ID, critical_msg)
        print("📨 Notifications sent.")

    # Start interactive chat session
    interactive_chat(mistral_client, agent_id)

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python analyze_and_collab.py <device_type>")
    else:
        main(sys.argv[1])
