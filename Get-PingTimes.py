"""
This script connects to Cisco devices via SSH to gather ping times for a list of IPs, 
stores the results in a CSV file, and updates additional data files with the results. 

Workflow:
1. Establishes SSH connections to SITE_A and SITE_B.
2. Sends ping commands to the provided IPs and parses the results.
3. Writes results to an output CSV file.
4. Updates an aggregated CSV file (`alldata.csv`) with new results and calculates averages.
5. Creates a `.js` file containing the last 35 days of data for frontend use.

Requirements:
- Python 3.6+
- Netmiko library for SSH connections.
- Input files: `sites.csv`, `alldata.csv`.
- Output files: `results.csv`, `csvdata.js`.

Usage:
Run the script and provide username and password credentials when prompted.
"""
from netmiko import ConnectHandler
from getpass import getpass
from concurrent.futures import ThreadPoolExecutor, as_completed
import csv
import time
from datetime import datetime
# Login Credentials
username = input("Username: ") # Prompt the user for their SSH username
password = getpass("Password: ") # Securely prompt for the password (hidden input)

# Initialize variables
start_time = time.time()
SITE_A_IP = "192.168.1.1"
SITE_B_IP = "192.168.2.1"
sites_csv = "sites.csv"
output_file = "results.csv"
js_file = "csvdata.js"
all_csv = "alldata.csv"
skip_sites = {"SITEC", "SITED"} # Update with the sitenames of any sites that have been decommissioned

# Create an SSH connection using netmiko
device = {
    'device_type': 'cisco_ios', # Specifies the device type for Netmiko
    'host': '0.0.0.0', # Placeholder for dynamic assignment during SSH connection
    'username': username, # Username provided by the user
    'password': password, # Password provided by the user
}

# Gather Ping Time Function
def gather_pings(ip, device):
    """
    Sends ping commands from SITE_A and SITE_B to a given IP address.
    
    Args:
        ip (str): The target IP address to ping.
        device (dict): Netmiko device configuration.

    Returns:
        dict: Contains the IP address and average ping times from SITE_A and SITE_B.
              If ping fails, 'x' is returned for the corresponding site.
    """
    try:
        device['host'] = SITE_A_IP
        connection = ConnectHandler(**device)
        # print(f"Successfully connected to {SITE_A_IP}.")
        # print(f"Pinging {ip} from {SITE_A_IP}...")
        ping_output = connection.send_command(f"ping {ip} source {SITE_A_IP} timeout 1 repeat 2")
        connection.disconnect()
        # print(f"Disconnected from SSH.")
        aping_time = "N/A"
        for line in ping_output.splitlines():
            if "Success rate is 0" in line:
                aping_time = 'x'
            elif "Success rate is" in line:
                aping_time = "N/A"
                try:
                    aping_time = line.split(" ")[9].split("/")[1]
                except IndexError:
                    aping_time = "N/A"
                break
        device['host'] = SITE_B_IP
        connection = ConnectHandler(**device)
        # print(f"Successfully connected to {SITE_B_IP}.")
        # print(f"Pinging {ip} from {SITE_B_IP}...")
        ping_output = connection.send_command(f"ping {ip} source {SITE_B_IP} timeout 1 repeat 2")
        connection.disconnect()
        # print(f"Disconnected from SSH.")
        bping_time = "N/A"
        for line in ping_output.splitlines():
            if "Success rate is 0" in line:
                bping_time = 'x'
            elif "Success rate is" in line:
                bping_time = "N/A"
                try:
                    bping_time = line.split(" ")[9].split("/")[1]
                except IndexError:
                    bping_time = "N/A"
                break
        return {
            'ip': ip,
            'ams': aping_time,
            'bms': bping_time
        }
    except Exception as e:
        print(f"Error pinging: {e}")
        return {
            'ip': ip,
            'ams': 'x',
            'bms': 'x'
        }

# Open CSV files, gather ping times, save results to the output csv file
try:
    # Read IPs from CSV
    print("Gathering ping times...")
    site_file = open(sites_csv)
    site_dict = csv.DictReader(site_file)
    sites = []
    ips_to_ping = []

    for row in site_dict:
        sites.append(row)
        ips_to_ping.append(row['ip'])

    # Perform concurrent ping operations
    ping_results = []
    with ThreadPoolExecutor(max_workers=12) as executor:
        # Submit ping tasks to the thread pool executor
        futures = {executor.submit(gather_pings, ip, device): ip for ip in ips_to_ping}
        for future in as_completed(futures):
            ip = futures[future]
            try:
                result = future.result()
                ping_results.append(result)
            except Exception as e:
                print(f"Error pinging {ip}")
    # Merge ping results with site metadata
    try:
        for site in sites:
            for result in ping_results:
                if result['ip'] == site['ip']:
                    result['tier'] = site['tier']
                    result['sitename'] = site['sitename']
                    result['sitecode'] = site['sitecode']
    except Exception as e:
        print(f"Error: {e}")
        
    # Write results to an output CSV file
    outputFile = open(output_file, 'w', newline='')
    outputDictWriter = csv.DictWriter(outputFile, ['tier', 'sitename', 'sitecode', 'ip', 'arouter', 'brouter'])
    outputDictWriter.writeheader()
    for result in ping_results:
        outputDictWriter.writerow({'tier': result['tier'], 'sitename': result['sitename'], 'sitecode': result['sitecode'], 'ip': result['ip'], 'arouter': result['ams'], 'brouter': result['bms']})
    outputFile.close()
    print(f"Results saved to {output_file}")
except Exception as e:
    print(f"An error occurred while gathering pings: {e}")

# Update all data csv file
try:
    print("Updating the 'alldata.csv' file...")
    today_date = datetime.now().strftime('%d-%b-%y')
    with open(all_csv, 'r') as file:
        csv_reader = csv.reader(file)
        header = next(csv_reader)
        header.append(today_date)
        data = []
        for  row in csv_reader:
            data.append(row)
    site_count = 0
    for result in ping_results:
        for row in data:
            if row[0] == result['sitename']:
                site_count += 1
                if site_count == 1:
                    row.append(result['ams'])
                elif site_count == 2:
                    row.append(result['bms'])
                    # site_count gets reset only after the second count. There will only ever
                    # be two sites. No more, no less.
                    site_count = 0
    for row in data:
        # Parses the row and pulls only the numbers and ignores any non-numbers
        numbers = [float(x) for x in row[4:] if x.replace('.', '', 1).isdigit()]
        if numbers:
            row[2] = round(sum(numbers) / len(numbers))
        else:
            if "site" not in row[0]:
                row[2] = 'x'
        with open(all_csv, 'w', newline='') as outfile:
            csv_writer = csv.writer(outfile)
            csv_writer.writerow(header)
            csv_writer.writerows(data)
except Exception as e:
    print(f"An error occured while updating the all data csv file: {e}")

# Pull the last 35 dates and update the .js csv file with them
try:
    print("Updating the .js file...")
    with open(all_csv, 'r') as file:
        csv_reader = csv.reader(file)
        data = []
        for row in csv_reader:
            temp1 = row[:3]
            temp2 = row[-35:]
            data.append(temp1 + temp2)
    for row in data:
        if row[1] == 'M':
            continue
        # Parses the row and pulls only the numbers and ignores any non-numbers
        numbers = [float(x) for x in row[3:] if x.replace('.', '', 1).isdigit()]
        if numbers:
            row[2] = round(sum(numbers) / len(numbers))
        else:
            if "site" not in row[0]:
                row[2] = 'x'
    js_output = ''
    js_output += "// The raw CSV data as a string\n"
    js_output += "const csvData = `\n"
    for row in data:
        if row[0] in skip_sites:
            continue
        row_str = ",".join(str(value) for value in row)
        js_output += row_str + "\n"
    js_output += "\n`;"
    with open(js_file, 'w') as file:
        file.write(js_output)
except Exception as e:
    print(f"An error occured while updating the .js file: {e}")

elapsed_time = (time.time()) - start_time
print(f"Script ran in {elapsed_time} seconds")
