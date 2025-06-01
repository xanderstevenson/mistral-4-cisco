import os
import yaml
import glob
import requests
from dotenv import load_dotenv

load_dotenv()

# Load from .env
WEBEX_TOKEN = os.getenv("WEBEX_BOT_TOKEN")
WEBEX_SPACE = os.getenv("WEBEX_SPACE")
ALEXANDER_WEBEX_ID = os.getenv("ALEXANDER_WEBEX_ID")

# --- Severity Keywords ---
SEVERITY_KEYWORDS = [
    "CRITICAL",
    "FAILURE",
    "OUTAGE",
    "DOWN",
    "MAJOR ISSUE",
    "HIGH IMPACT",
    "DATA LOSS",
    "Unable to connect"
]


# --- Get Most Recent YAML ---
def get_latest_yaml(device_type):
    output_dir = os.path.join("output", device_type)
    files = glob.glob(os.path.join(output_dir, "*.yaml"))
    files.sort(key=os.path.getmtime, reverse=True)
    return files[0] if files else None


# --- Load Summary from YAML ---
def load_summary_from_yaml(path):
    with open(path, "r") as f:
        data = yaml.safe_load(f)
        return (
            data.get("summary", ""),
            data.get("timestamp", ""),
            data.get("device_type", "unknown"),
        )


# --- Check for Critical Severity ---
# def is_critical(summary):
#     upper_summary = summary.upper()
#     return any(keyword in upper_summary for keyword in SEVERITY_KEYWORDS)
# --- Check for Critical Severity in the Summary ---
def is_critical(summary):
    summary_tail = summary[-2000:].upper()  # Look at only the last part (trimmed to avoid noise)
    return any(keyword in summary_tail for keyword in SEVERITY_KEYWORDS)



# --- Send Webex Message ---
def send_webex_message(recipient, message, is_room=False):
    url = "https://webexapis.com/v1/messages"
    headers = {
        "Authorization": f"Bearer {WEBEX_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "markdown": message
    }

    if is_room:
        payload["roomId"] = recipient
    else:
        payload["toPersonId"] = recipient

    response = requests.post(url, headers=headers, json=payload)
    if response.status_code != 200:
        print(f"❌ Failed to send Webex message: {response.status_code} {response.text}")



# --- Main Logic ---
def main(device_type):
    latest_yaml = get_latest_yaml(device_type)
    if not latest_yaml:
        print(f"❌ No YAML files found for {device_type}")
        return
    yaml_filename = os.path.basename(latest_yaml)
    chat_link = os.getenv("LE_CHAT_URL")
    summary, timestamp, device_type_loaded = load_summary_from_yaml(latest_yaml)

    # Check critical first
    critical_issue_found = is_critical(summary)

    # Prepare short issue summary for team message
    short_issue = (
        "⚠️ Critical issue detected — Alexander has been notified directly."
        if critical_issue_found else "✅ No major issues detected."
    )

    # Team message includes alert status and link
    team_msg = f"""✅ **Network Analysis Completed**
                **Device Type**: `{device_type_loaded}`  
                **Timestamp**: `{timestamp}`  
                {short_issue}  
                📁 **Report**: `output/{device_type_loaded}/{yaml_filename}`  
                💬 [Open La Chat]({chat_link})
                """

    send_webex_message(WEBEX_SPACE, team_msg, is_room=True)

    # Send direct alert if critical
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



if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: python analyze_and_collab.py <device_type>")
    else:
        main(sys.argv[1])
