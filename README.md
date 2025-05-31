# **Mistral AI-Powered Network Analysis for Cisco Devices**

## **Objective**

This project automates the collection and analysis of data from Cisco network devices using SSH and the Mistral AI API. The goal is to provide network engineers with intelligent summaries and insights into device configurations, operational status, and potential issues. The script connects to devices, collects output from various `show` commands, and then sends the collected data to Mistral AI for analysis. The results are then saved in organized, timestamped YAML files. This version supports multiple device types (e.g., nxos, iosxe) and groups analysis by device type.

## **Use Case**

*   Proactive Network Monitoring: Regularly collect and analyze device data to identify potential problems before they impact the network.
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

1.  Create a Project Directory:

    ```bash
    mkdir mistral-cisco-analyzer
    cd mistral-cisco-analyzer
    ```

2.  Create a Virtual Environment:

    ```bash
    python3 -m venv venv
    ```

3.  Activate the Virtual Environment:

    ```bash
    source venv/bin/activate
    ```

**Step 3: Install Required Python Libraries**

Install the necessary Python libraries using `pip`:

```bash
pip install -r requirements.txt
```
