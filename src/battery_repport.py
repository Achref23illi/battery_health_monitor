import subprocess
from bs4 import BeautifulSoup
import os
import re

def generate_battery_report(output_path="battery-report.html"):
    """
    Generate a battery report using the Windows 'powercfg' command.
    
    Parameters:
        output_path (str): The file path where the battery report will be saved.
    
    Returns:
        str: Path to the generated report
    """
    try:
        # Get absolute path to ensure proper access
        abs_output_path = os.path.abspath(output_path)
        
        # Construct and run the command to generate the report.
        command = f'powercfg /batteryreport /output "{abs_output_path}"'
        subprocess.run(command, shell=True, check=True)
        print(f"Battery report generated successfully at {abs_output_path}")
        return abs_output_path
    except subprocess.CalledProcessError as e:
        print(f"Error generating battery report: {e}")
        raise

def extract_capacity_history(soup):
    """
    Extract capacity history data from the battery report.
    
    Parameters:
        soup (BeautifulSoup): The parsed HTML
    
    Returns:
        tuple: Lists of periods, full charge capacities, and design capacities
    """
    periods = []
    full_charge_capacities = []
    design_capacities = []
    
    # Find the Battery Capacity History section
    capacity_history_section = None
    for h2 in soup.find_all('h2'):
        if 'Battery capacity history' in h2.get_text():
            capacity_history_section = h2.find_next('table')
            break
    
    if capacity_history_section:
        # Skip the header row
        rows = capacity_history_section.find_all('tr')[1:]
        for row in rows:
            cells = row.find_all('td')
            if len(cells) >= 3:
                periods.append(cells[0].get_text(strip=True))
                
                # Extract numeric values using regex
                full_charge_text = cells[1].get_text(strip=True)
                full_charge_match = re.search(r'(\d+)', full_charge_text)
                if full_charge_match:
                    full_charge_capacities.append(int(full_charge_match.group(1)))
                
                design_text = cells[2].get_text(strip=True)
                design_match = re.search(r'(\d+)', design_text)
                if design_match:
                    design_capacities.append(int(design_match.group(1)))
    
    return periods, full_charge_capacities, design_capacities

def parse_battery_report(file_path="battery-report.html"):
    """
    Parse the battery report HTML and extract key metrics.
    
    Parameters:
        file_path (str): The file path to the battery report HTML.
    
    Returns:
        tuple: A tuple containing metrics, details, usage history, and visualization data
    """
    metrics = {}
    details = {}
    usage_history = []
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            html_content = f.read()
            
        soup = BeautifulSoup(html_content, "html.parser")
        
        # Extract general battery information
        for table in soup.find_all("table"):
            for row in table.find_all("tr"):
                cells = row.find_all("td")
                if len(cells) == 2:
                    label = cells[0].get_text(strip=True)
                    value = cells[1].get_text(strip=True)
                    
                    if any(key in label for key in ["Design Capacity", "Full Charge Capacity", "Cycle Count"]):
                        metrics[label] = value
                    elif not any(ignore in label for ignore in ["BATTERY", ":", "Time"]):
                        details[label] = value
        
        # Extract usage history
        usage_table = None
        for h2 in soup.find_all('h2'):
            if 'Battery usage' in h2.get_text():
                usage_table = h2.find_next('table')
                break
                
        if usage_table:
            header_row = usage_table.find('tr')
            headers = [h.get_text(strip=True) for h in header_row.find_all('th')]
            
            for row in header_row.find_next_siblings("tr", limit=7):
                cells = row.find_all("td")
                if len(cells) >= 4:
                    usage_data = {}
                    for i, cell in enumerate(cells[:4]):
                        if i < len(headers):
                            usage_data[headers[i]] = cell.get_text(strip=True)
                    if usage_data:
                        usage_history.append(usage_data)
        
        # Extract capacity history for visualization
        periods, full_charge_capacities, design_capacities = extract_capacity_history(soup)
        
        return metrics, details, usage_history, (periods, full_charge_capacities, design_capacities), html_content
        
    except Exception as e:
        print(f"Error parsing battery report: {e}")
        raise

if __name__ == "__main__":
    # For testing purposes, generate and then parse the report.
    report_path = generate_battery_report()
    battery_metrics, battery_details, battery_usage_history, capacity_data, _ = parse_battery_report(report_path)
    
    print("Parsed Battery Metrics:")
    for key, value in battery_metrics.items():
        print(f"{key}: {value}")
    
    print("\nParsed Battery Details:")
    for key, value in battery_details.items():
        print(f"{key}: {value}")
    
    print("\nBattery Usage History (Last 7 Days):")
    for usage in battery_usage_history:
        print(usage)
        
    print("\nCapacity History Data:")
    periods, full_charges, design_capacities = capacity_data
    print(f"Periods: {periods}")
    print(f"Full Charge Capacities: {full_charges}")
    print(f"Design Capacities: {design_capacities}")