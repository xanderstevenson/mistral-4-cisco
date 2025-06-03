# **Mistral AI-Powered Network Analysis for Cisco Devices**

<div style="text-align:center">
  <img src="https://github.com/xanderstevenson/mistral-4-cisco/blob/main/images/mistral-ai.jpg" width="400">
</div>


## **🔍 Objective**

This project automates the **collection**, **analysis**, and **collaborative troubleshooting** of data from Cisco network devices using SSH and **Mistral AI**, combining real-time intelligence with persistent memory.

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


## **Prerequisites**

Before you begin, ensure you have the following:

*   *Cisco Network Devices*: Access to Cisco network devices (e.g., Nexus switches, IOS-XE routers) with SSH enabled.
*   *Mistral AI Account and API Key*: A Mistral AI account and a valid API key. You can sign up at [Mistral AI](https://mistral.ai/).
*   *Python Environment*: A Python 3.9+ environment with the necessary libraries installed.
*   *SSH Credentials*: Valid SSH credentials (username and password) for accessing the Cisco devices.
*   *Source of Truth YAML File*: A YAML file (e.g., `source_of_truth/devices.yaml`) containing a list of devices with their connection details and device types.

## **Set Up**

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



### **Step 4: Place the Mistral API key in the environment**

A. Create a `.env` file in the root directory of your project to store your Mistral AI API key in a persistent manner:

```bash
touch .env
```

....placing the key inside like so:

```bash
MISTRAL_API_KEY=your_mistral_api_key_here
````

* This method may require some additional steps in IDEs like VS Code, such as adding an entry in .vscode/settings.json as well as the settings.json in the VS Code Settings.


B. To save the API key non-persistently, you can:

```bash
MISTRAL_API_KEY=your_mistral_api_key_here
```


### **Step 5: Create the `source_of_truth/devices.yaml` File**

``bash
mkdir source_of_truth
touch source_of_truth/devices.yaml

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

## **Run It**

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
5.  Save the raw outputs and the AI-generated summaries to a timestamped YAML file in the `output/<device_type>` directory.
6.  Display analysis for each device and for the device group in the terminal.


<img src="https://github.com/xanderstevenson/mistral-4-cisco/blob/main/images/Mistral-Output.png" width="800" style="display: block; margin-left: auto; margin-right: auto;">


### **Review the Output**


The script will create a directory named `output` (if it doesn't already exist) and subdirectories for each device type (e.g., `output/nxos`, `output/iosxe`). Each subdirectory will contain timestamped YAML files with the raw device outputs and the AI-generated summaries.

The YAML files will contain:

*   The `device_type`.
*   A timestamp.
*   **If there is only one device of that type:** The raw outputs from that device and a detailed AI-generated summary of that device.
*   **If there are multiple devices of that type:**
    *   The raw outputs from each device.
    *   AI-generated summaries for each individual device.
    *   A combined AI-generated summary that identifies common configurations, deviations, and potential vulnerabilities across all devices of that type.
