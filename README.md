# **AI-Powered Network Analysis for Cisco Devices Using Mistral's AI API and Agent Architecture**

[![published](https://static.production.devnetcloud.com/codeexchange/assets/images/devnet-published.svg)](https://developer.cisco.com/codeexchange/github/repo/xanderstevenson/mistral-4-cisco)

<div style="text-align:center">
  <img src="https://github.com/xanderstevenson/mistral-4-cisco/blob/main/images/mistral-ai.jpg" width="400">
</div>


## **⚠️ Data Privacy Disclaimer** 

Although Mistral complies with the EU's more stringent data sovereignty guidelines, any non-personally identifiable information you share with them may be retained. I believe that for their agents, data is stored for 30 days, while for the AI API, the information you send is retained until you delete your account. Take care to wisely choose what you send to Mistral or any other AI provider. 


## **🔍 Objective**

This project automates the **collection**, **analysis**, and **collaborative troubleshooting** of data from Cisco network devices using SSH/Paramiko and **Mistral AI**, combining real-time intelligence with persistent memory. It utlizes both the Mistral AI API and Mistral AI Agents. Everything you need to run this is free: a free Mistral Account, free API plan, and free models.

### Key Goals:
- Summarize device health and configurations.
- Detect network issues and anomalies.
- Enable persistent, AI-assisted team collaboration.

---

## **📦 Project Overview**

| Script | Purpose |
|--------|---------|
| `mistral.py` | Collects device output and sends it to Mistral AI for analysis. Saves YAML summaries. |
| `troubleshoot.py` | Launches a **stateless AI chat** for ad hoc troubleshooting of Cisco devices. |
| `analyze_and_collab.py` | Creates a **persistent Mistral AI Agent** with stored context and collaborative memory. Sends analysis reports to Webex, notifies team members, and enables an interactive session. |

---

## **🚀 Use Cases**

- **Proactive Network Monitoring**: Run daily/weekly to detect risks and degradations.
- **Configuration Auditing**: Validate against known-good standards.
- **Incident Response & Troubleshooting**: Use agent memory to track ongoing issues.
- **Compliance & Documentation**: Generate structured YAML summaries.
- **Security Auditing**: Spot misconfigurations, default credentials, and exposed ports.

---

## **🧰 Prerequisites**

Before you begin, ensure you have the following:

- ✅ Cisco Devices (e.g. Nexus, IOS-XE) with SSH access.
- ✅ Mistral AI API Key (from [Mistral AI](https://mistral.ai/)).
- ✅ Python 3.9+ environment.
- ✅ Webex Bot Token (optional, for messaging features).
- ✅ `.env` file with required keys and IDs.
- ✅ `source_of_truth/devices.yaml` file with devices grouped by type.

---

## **⚙️ Set Up Instructions**

### Step 1: Obtain a Mistral AI API Key

1.  *Create a Mistral AI Account*: Go to [Mistral AI](https://mistral.ai/) and sign up for an account. Set up Multi-Factor Authentication (MFA) for enhanced security.
2.  *Generate an API Key*: Navigate to the Mistral Console. Go to API Keys and click "Create New Key". Copy the generated API key.


### **Step 2: Create a Python Virtual Environment**

It is **highly recommended** to use a virtual environment to manage project dependencies.


1.  Create a Virtual Environment:

    ```bash
    python3 -m venv venv
    ```

2.  Activate the Virtual Environment:

    ```bash
    source venv/bin/activate
    ```

3.  Clone this Repo:

    ```bash
    git clone https://github.com/xanderstevenson/mistral-4-cisco.git
    ```


### **Step 3: Install Required Python Libraries**

Install the necessary Python libraries using `pip`:

```bash
pip install -r requirements.txt
```



### **Step 4: Add Environment Variables**

A. Create a `.env` file in the root directory of your project to store your Mistral AI API key in a persistent manner:

```bash
touch .env
```

....placing the key inside like so:

```bash
MISTRAL_API_KEY=your_mistral_api_key_here
WEBEX_BOT_TOKEN=your_webex_token
WEBEX_SPACE=webex_space_id
ALEXANDER_WEBEX_ID=person_id_for_direct_alerts
LE_CHAT_URL=https://your-collaboration-space-url

````

* This method may require some additional steps in IDEs like VS Code, such as adding an entry in .vscode/settings.json as well as the settings.json in the VS Code Settings.


B. To save the API key non-persistently, you can:

```bash
export MISTRAL_API_KEY=your_mistral_api_key_here
export WEBEX_BOT_TOKEN=your_webex_token
export WEBEX_SPACE=webex_space_id
export ALEXANDER_WEBEX_ID=person_id_for_direct_alerts
export LE_CHAT_URL=https://your-collaboration-space-url
```


### **Step 5: Define Your Devices**

Create your device list in source_of_truth/devices.yaml:

```bash
mkdir source_of_truth
touch source_of_truth/devices.yaml
```

```bash
devices:
  - name: Open NX-OS Programmability AlwaysOn
    device_type: nxos
    ip: sbx-nxos-mgmt.cisco.com
    username: admin
    password: Admin_1234!
```

The devices should be accurately labelled by device_type so they script can loop though those device families, aggregate the family info, and send it to Mistral for analysis on individual devices, as well as on the family of devices. 

**Note** *For the the NX-OS device used in this demonstration, I am connecting to the Open NX-OS Programmability AlwaysOn sandbox from Cisco DevNet: https://devnetsandbox.cisco.com/DevNet/catalog/Open-NX-OS-Programmability_open-nx-os*

---

## **🚀Run It**

From the `mistral_4_cisco` directory, run:

```bash
python mistral.py
```

### ***The script will:***

1.  Load the device information from `source_of_truth/devices.yaml`.
2.  Group the devices by their `device_type`.
3.  Connect to each device via SSH and execute a series of `show` commands.
4.  **Analyze the Device Outputs:**
    *   **If there is only one device of a particular `device_type`:** Send the output from that device to Mistral AI for a detailed individual analysis.
    *   **If there are multiple devices of a particular `device_type`:**
        *   Send the output from each device to Mistral AI for individual analysis.
        *   Send the combined output from all devices of that type to Mistral AI for a combined analysis, including identification of common configurations, deviations, and potential vulnerabilities.
<img src="https://github.com/xanderstevenson/mistral-4-cisco/blob/main/images/device-analysis.png" width="600" style="display: block; margin-left: auto; margin-right: auto;">
5.  Save the raw outputs and the AI-generated summaries to a timestamped YAML file in the `output/<device_type>` directory.
6.  Display analysis for each device and for the device group in the terminal.
7. Invoke `analyze_and_collab.py` to create or continue a persistent AI Agent conversation:

- This script manages a long-lived conversation by storing agent_id and conversation_id in agent_id.txt and conversation_id.txt.

- The Agent keeps context between runs, enabling ongoing collaborative troubleshooting and analysis.

- The conversation remains open, ready for additional inputs in future runs.

<img src="https://github.com/xanderstevenson/mistral-4-cisco/blob/main/images/persistent-chat.png" width="800" style="display: block; margin-left: auto; margin-right: auto;">

- At least one Webex message with summary information is sent to configured spaces.

<img src="https://github.com/xanderstevenson/mistral-4-cisco/blob/main/images/network-analyzer.png" height="400" style="display: block; margin-left: auto; margin-right: auto;">

- If the network state is deemed critical, a second urgent Webex message is sent to alert the team promptly.

<img src="https://github.com/xanderstevenson/mistral-4-cisco/blob/main/images/network-buddy.png" height="400" style="display: block; margin-left: auto; margin-right: auto;">

**Note** - Remember that you will need the following set in .env in order for the Webex messaging to be successful: WEBEX_BOT_TOKEN, WEBEX_SPACE, <Insert-Team-Member>_WEBEX_ID. The bot token can be gained by creating a bot here: https://developer.webex.com/my-apps, which then must be added to the group space you want it to interact with. The bot will send 1:1 messages to the designated individual(s). The id of the Webex space is gathered by clicking on the `settings` gear in the Webex space and selecting 'Copy space link'. Webex ids of individuals can be found, with their email address, using the Webex People API: https://developer.webex.com/admin/docs/api/v1/people/list-people However, you'll find that you need a Bearer Token to get the id and it is found by clicking on your photo in the top right corner of the page.



### **Review the Output**


The script will immediately disply the analysis it recieves back from the Mistral AI API in the terminal. This will include a summary that explains the status and health of each device, along with the combined analysis of all devices. Detailed points include: Potential Issues/Anomalies, Common Configurations and Settings, Significant Deviations/Inconsistencies, Potential Security Vulnerabilities or Misconfigurations, and Suggestions for Improvement. The script will create a directory named `output` (if it doesn't already exist) and subdirectories for each device type (e.g., `output/nxos`, `output/iosxe`). Each subdirectory will contain timestamped YAML files with the raw device outputs and the AI-generated summaries.

The YAML files will contain:

*   The `device_type`.
*   A timestamp.
*   **If there is only one device of that type:** The raw outputs from that device and a detailed AI-generated summary of that device.
*   **If there are multiple devices of that type:**
    *   The raw outputs from each device.
    *   AI-generated summaries for each individual device.
    *   A combined AI-generated summary that identifies common configurations, deviations, and potential vulnerabilities across all devices of that type.

<img src="https://github.com/xanderstevenson/mistral-4-cisco/blob/main/images/Mistral-Output.png" width="800" style="display: block; margin-left: auto; margin-right: auto;">

---

## **👩🏽‍💻Notes on the Workflow**

- The primary use case is `running mistral.py`, which automates the entire workflow and invokes `analyze_and_collab.py` internally.

- `analyze_and_collab.py` manages a persistent AI Agent conversation by saving conversation IDs locally (`agent_id.txt` and `conversation_id.txt`), allowing the Agent to maintain context across multiple script executions.

- This dual-layer approach uses the Mistral AI API for immediate analysis and the Agent for persistent, conversational context—providing redundancy and richer collaboration in case one service is down. For example, if the AI API is not reachable, the device outputs will still be saved locally by `mistral.py' (just without the analysis and summary apppended), allowing `analyze_and_collab.py' to still create a persistent conversation regarding the network state. On the other hand, if the AI API is functioning but the agent creation pipeline is down for some reason, we still at least get the initial analysis and summary from the API. 

- The Agent conversation stays open after each run, enabling continued interaction and incremental updates.

- Webex notifications are automatically sent by `analyze_and_collab.py`:

  - A summary message is always sent to a team Webex space.

  - An additional urgent alert message is sent to a designated individual if the network state is critical, ensuring timely awareness and response.
 
  - The Webex messages can contain a link to a dedicated Mistral AI In-Browser Assistant (Le Chat) if an Agent with a relevant system prompt (instruction) is created using Mistral's La Platforme dashboard. When an agent is created via the dashboard, the URL for the Le Chat chat assistant can be saved in the .env file. From there, the `analyze_and_collab.py` script will place the URL into the Webex messages.
<img src="https://github.com/xanderstevenson/mistral-4-cisco/blob/main/images/Le-Chat.png" width="500" style="display: block; margin-left: auto; margin-right: auto;">

- For ad hoc, non-persistent troubleshooting, users can run `troubleshoot.py` directly to engage with the AI Agent without persisting context.

---

## **Helpful Links**

- **Mistral Docs, including Quickstart and Models:** https://docs.mistral.ai/

- **Mistral AI API, including OpenAPI specification:** https://docs.mistral.ai/api/

- **Le Chat:** https://chat.mistral.ai/chat

- **La Platforme:** https://console.mistral.ai/

- **Blog: Build AI agents with the Mistral Agents API:** https://mistral.ai/news/agents-api


