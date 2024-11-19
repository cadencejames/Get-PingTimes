This script connects to Cisco devices via SSH to gather ping times for a list of IPs, 
stores the results in a CSV file, and updates additional data files with the results. 

Workflow:
1. Establishes SSH connections to SITE_A and SITE_B.
2. Sends ping commands to the provided IPs and parses the results.
3. Writes results to an output CSV file.
4. Updates an aggregated CSV file (`alldata.csv`) with new results and calculates averages.
5. Creates a `.js` file containing the last 35 days of data for frontend use. (for instance: [This reporting tool](https://github.com/cadencejames/PingTimeStatusReport))

Requirements:
- Python 3.6+
- Netmiko library for SSH connections.
- Input files: `sites.csv`, `alldata.csv`. (Examples provided)
- Output files: `results.csv`, `csvdata.js`.

Usage:
Run the script and provide username and password credentials when prompted.
