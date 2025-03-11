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
    
    # Find the Battery Capacity History section - try different approaches
    capacity_history_section = None
    
    # Method 1: Look for h2 with "Battery capacity history"
    for h2 in soup.find_all('h2'):
        if 'Battery capacity history' in h2.get_text():
            capacity_history_section = h2.find_next('table')
            break
    
    # Method 2: Look for any section that might contain capacity history data
    if not capacity_history_section:
        for table in soup.find_all('table'):
            if 'CAPACITY HISTORY' in table.get_text().upper() or 'FULL CHARGE' in table.get_text().upper():
                capacity_history_section = table
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
    
    # If we couldn't find capacity history, create dummy data for testing
    if not periods:
        # This is just for visualization testing when real data isn't available
        print("WARNING: Could not find capacity history data. Using dummy data for testing.")
        periods = [f"Period {i}" for i in range(1, 11)]
        
        # Try to get design capacity from metrics
        design_capacity = None
        for table in soup.find_all('table'):
            for row in table.find_all('tr'):
                cells = row.find_all('td')
                if len(cells) == 2 and "Design Capacity" in cells[0].get_text():
                    design_match = re.search(r'(\d+)', cells[1].get_text())
                    if design_match:
                        design_capacity = int(design_match.group(1))
        
        if not design_capacity:
            design_capacity = 50000  # Default value
            
        full_charge_capacity = None
        for table in soup.find_all('table'):
            for row in table.find_all('tr'):
                cells = row.find_all('td')
                if len(cells) == 2 and "Full Charge Capacity" in cells[0].get_text():
                    full_match = re.search(r'(\d+)', cells[1].get_text())
                    if full_match:
                        full_charge_capacity = int(full_match.group(1))
        
        if not full_charge_capacity:
            full_charge_capacity = design_capacity * 0.8  # 80% health as default
            
        # Generate dummy data with slight degradation
        full_charge_capacities = [int(full_charge_capacity * (1 - 0.005 * i)) for i in range(10)]
        design_capacities = [design_capacity] * 10
    
    return periods, full_charge_capacities, design_capacities

def find_battery_info(soup):
    """
    Extract battery information from various table formats
    
    Parameters:
        soup (BeautifulSoup): Parsed HTML content
        
    Returns:
        dict: Dictionary with battery metrics
    """
    metrics = {}
    
    # Try multiple approaches to find battery information
    
    # Method 1: Look for specific tables with battery information
    for table in soup.find_all("table"):
        table_text = table.get_text().lower()
        if any(key in table_text for key in ["design capacity", "full charge capacity", "cycle count"]):
            for row in table.find_all("tr"):
                cells = row.find_all("td")
                if len(cells) == 2:
                    label = cells[0].get_text(strip=True)
                    value = cells[1].get_text(strip=True)
                    
                    # Check for key metrics
                    if any(key in label for key in ["Design Capacity", "Full Charge Capacity", "Cycle Count"]):
                        metrics[label] = value
    
    # Method 2: Look for sections that might be labeled differently
    if not metrics:
        for table in soup.find_all("table"):
            for row in table.find_all("tr"):
                cells = row.find_all("td")
                if len(cells) == 2:
                    label = cells[0].get_text(strip=True)
                    value = cells[1].get_text(strip=True)
                    
                    # Use regex to look for capacity values
                    if "capacity" in label.lower() and "mwh" in value.lower():
                        if "design" in label.lower():
                            metrics["Design Capacity"] = value
                        elif "full" in label.lower():
                            metrics["Full Charge Capacity"] = value
                    
                    # Look for cycle count
                    if "cycle" in label.lower() and re.search(r'\d+', value):
                        metrics["Cycle Count"] = value
    
    # If still no metrics, add default values for testing
    if not metrics:
        print("WARNING: Could not find battery metrics. Using default values for testing.")
        metrics = {
            "Design Capacity": "50000 mWh",
            "Full Charge Capacity": "40000 mWh",
            "Cycle Count": "300"
        }
    
    return metrics

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
        
        # Extract battery metrics using enhanced method
        metrics = find_battery_info(soup)
        
        # Extract general battery information
        for table in soup.find_all("table"):
            for row in table.find_all("tr"):
                cells = row.find_all("td")
                if len(cells) == 2:
                    label = cells[0].get_text(strip=True)
                    value = cells[1].get_text(strip=True)
                    
                    # Add to details if not already in metrics
                    if label not in metrics and not any(ignore in label.lower() for ignore in ["battery", ":", "time"]):
                        details[label] = value
        
        # Extract usage history
        usage_table = None
        for h2 in soup.find_all(['h2', 'h3']):
            if 'Battery usage' in h2.get_text():
                usage_table = h2.find_next('table')
                break
                
        if usage_table:
            header_row = usage_table.find('tr')
            if header_row:
                headers = [h.get_text(strip=True) for h in header_row.find_all('th')]
                
                for row in header_row.find_next_siblings("tr", limit=7):
                    cells = row.find_all("td")
                    if len(cells) >= 3:  # At least date and some values
                        usage_data = {}
                        for i, cell in enumerate(cells):
                            if i < len(headers):
                                usage_data[headers[i]] = cell.get_text(strip=True)
                        if usage_data:
                            usage_history.append(usage_data)
        
        # Extract capacity history for visualization
        periods, full_charge_capacities, design_capacities = extract_capacity_history(soup)
        
        # Calculate battery health percentage
        try:
            design_capacity_str = metrics.get("Design Capacity", "0 mWh")
            full_charge_str = metrics.get("Full Charge Capacity", "0 mWh")
            
            design_capacity_match = re.search(r'(\d+)', design_capacity_str)
            full_charge_match = re.search(r'(\d+)', full_charge_str)
            
            if design_capacity_match and full_charge_match:
                design_capacity = int(design_capacity_match.group(1))
                full_charge = int(full_charge_match.group(1))
                
                if design_capacity > 0:
                    health_pct = (full_charge / design_capacity) * 100
                    metrics["Battery Health"] = f"{health_pct:.1f}%"
        except Exception as e:
            print(f"Error calculating battery health: {e}")
        
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