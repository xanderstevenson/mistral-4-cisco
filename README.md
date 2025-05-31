# **Mistral AI-Powered Network Analysis for Cisco Devices**

## **Objective**

This project automates the collection and analysis of data from Cisco network devices using SSH and the Mistral AI API. The goal is to provide network engineers with intelligent summaries and insights into device configurations, operational status, and potential issues. The script connects to devices, collects output from various `show` commands, and then sends the collected data to Mistral AI for analysis. The results are then displayed in the terminal and saved in organized, timestamped YAML files. This version supports multiple device types (e.g., nxos, iosxe) and groups analysis by device type.

## **Use Case**

*   *Proactive Network Monitoring*: Regularly collect and analyze device data to identify potential problems before they impact the network.
*   Configuration Auditing: Ensure that devices are configured according to organizational standards and security best practices.
*   Troubleshooting: Quickly gather and analyze relevant data from multiple devices to diagnose network issues.
*   Security Analysis: Identify potential security vulnerabilities or misconfigurations.
*   Inventory and Documentation: Automatically generate summaries of device configurations for documentation purposes.

## **Prerequisites**

Before you begin, ensure you have the following:

*   Cisco Network Devices: Access to Cisco network devices (e.g., Nexus switches, IOS-XE routers) with SSH enabled.
*   Mistral AI Account and API Key: A Mistral AI account and a valid API key. You can sign up at [Mistral AI](https://mistral.ai/).
*   Python Environment: A Python 3.9+ environment with the necessary libraries installed.
*   SSH Credentials: Valid SSH credentials (username and password) for accessing the Cisco devices.
*   Source of Truth YAML File: A YAML file (e.g., `source_of_truth/devices.yaml`) containing a list of devices with their connection details and device types.

## **Set Up**

**Step 1: Obtain a Mistral AI API Key**

1.  Create a Mistral AI Account: Go to [Mistral AI](https://mistral.ai/) and sign up for an account. Set up Multi-Factor Authentication (MFA) for enhanced security.
2.  Generate an API Key: Navigate to the Mistral Console. Go to API Keys and click "Create New Key". Copy the generated API key.


**Step 2: Create a Python Virtual Environment**

It is highly recommended to use a virtual environment to manage project dependencies.


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


**Step 3: Install Required Python Libraries**

Install the necessary Python libraries using `pip`:

```bash
pip install -r requirements.txt
```



**Step 4: Create a `.env` File**

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


**Step 5: Edit the `source_of_truth/devices.yaml` File**

```bash
devices:
  - name: Open NX-OS Programmability AlwaysOn
    device_type: nxos
    ip: sbx-nxos-mgmt.cisco.com
    username: admin
    password: Admin_1234!
```

The devices should be accurately labelled by device_type so they scriot can loop though those families, aggregate the family info, and send to Mistral for analysis on individual devices, as well as on the family of devices.

## **Run It**

From the `mistral_4_cisco` directory, run:

```bash
python mistral.py
```

***The script will:***

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


**Review the Output**


The script will create a directory named `output` (if it doesn't already exist) and subdirectories for each device type (e.g., `output/nxos`, `output/iosxe`). Each subdirectory will contain timestamped YAML files with the raw device outputs and the AI-generated summaries.

The YAML files will contain:

*   The `device_type`.
*   A timestamp.
*   **If there is only one device of that type:** The raw outputs from that device and a detailed AI-generated summary of that device.
*   **If there are multiple devices of that type:**
    *   The raw outputs from each device.
    *   AI-generated summaries for each individual device.
    *   A combined AI-generated summary that identifies common configurations, deviations, and potential vulnerabilities across all devices of that type.






