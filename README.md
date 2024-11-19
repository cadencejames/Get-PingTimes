# **Cisco Ping Time Monitoring Script**
![Build Status](https://img.shields.io/github/workflow/status/cadencejames/Get-PingTimes/CI?label=build&logo=github&style=flat-square)
![Python Version](https://img.shields.io/badge/python-3.6%2B-blue)
![Netmiko](https://img.shields.io/badge/library-netmiko-blue)
![License](https://img.shields.io/github/license/cadencejames/Get-PingTimes)
![Stars](https://img.shields.io/github/stars/cadencejames/Get-PingTimes)
![Forks](https://img.shields.io/github/forks/cadencejames/Get-PingTImes)
![Last Commit](https://img.shields.io/github/last-commit/cadencejames/Get-PingTimes)
![Contributors](https://img.shields.io/github/contributors/cadencejames/Get-PingTImes)
[![Frontend Tool](https://img.shields.io/badge/frontend-tool-green)](https://github.com/cadencejames/PingTimeStatusReport)

This Python script connects to Cisco devices via SSH, gathers ping times for a list of IP addresses, and processes the results to update multiple output files. The processed data can be used for network performance monitoring and reporting.

---

## **Features**
- Establishes secure SSH connections to multiple Cisco devices (SITE_A and SITE_B).
- Executes ping commands for a list of IPs and parses the results.
- Outputs the results in a structured CSV file (`results.csv`).
- Updates an aggregated data file (`alldata.csv`) with the latest ping results and calculated averages.
- Generates a `.js` file (`csvdata.js`) containing the last 35 days of data, ready for use in frontend applications such as [PingTimeStatusReport](https://github.com/cadencejames/PingTimeStatusReport).

---

## **Workflow**
1. **Connect to Devices**  
   - Establish SSH connections to SITE_A and SITE_B using the provided credentials.
   
2. **Ping Execution**  
   - Send ICMP ping commands to each target IP using SITE_A and SITE_B as sources.  
   - Parse the success rates and average round-trip times from the device responses.
   
3. **Output Results**  
   - Save the ping results to `results.csv`, including site metadata (e.g., site name, code, tier).
   
4. **Update Aggregated Data**  
   - Add the new results to `alldata.csv`.  
   - Compute averages for each site and append the data with new columns for the current date.
   
5. **Generate Frontend Data**  
   - Create a `.js` file (`csvdata.js`) containing the last 35 days of data, formatted as a string for frontend integration.

---

## **Requirements**
- **Python Version:** Python 3.6+
- **Libraries:**  
  - `netmiko`: For SSH connections. Install via pip: `pip install netmiko`
  - `csv`: Standard library for working with CSV files.
  
- **Input Files:**  
  - `sites.csv`: Contains metadata and IPs to be pinged. (Example file provided)  
  - `alldata.csv`: Aggregated historical data for ping times. (Example file provided)  

- **Output Files:**  
  - `results.csv`: Stores the current run's ping results.  
  - `csvdata.js`: Contains the last 35 days of data for frontend use.

---

## **Usage**
1. Clone the repository and navigate to the script directory.
2. Install the required dependencies if not already installed:
   ```bash
   pip install netmiko
   ```
3. Run the script:
   ```bash
   python .\Get-PingTimes.py
   ```
4. Enter the SSH username and password when prompted
