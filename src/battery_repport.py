import subprocess
from bs4 import BeautifulSoup

def generate_battery_report(output_path="battery-report.html"):
    """
    Generate a battery report using the Windows 'powercfg' command.
    
    Parameters:
        output_path (str): The file path where the battery report will be saved.
    
    Returns:
        None
    """
    try:
        # Construct and run the command to generate the report.
        command = f'powercfg /batteryreport /output "{output_path}"'
        subprocess.run(command, shell=True, check=True)
        print("Battery report generated successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error generating battery report: {e}")
        raise

def parse_battery_report(file_path="battery-report.html"):
    """
    Parse the battery report HTML and extract key metrics.
    
    Parameters:
        file_path (str): The file path to the battery report HTML.
    
    Returns:
        dict: A dictionary containing key-value pairs of battery metrics.
    """
    metrics = {}
    details = {}
    usage_history = []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            soup = BeautifulSoup(f, "html.parser")
        # Loop through all table rows in the HTML
        for row in soup.find_all("tr"):
            cells = row.find_all("td")
            if len(cells) == 2:
                label = cells[0].get_text(strip=True)
                value = cells[1].get_text(strip=True)
                if "Design Capacity" in label or "Full Charge Capacity" in label or "Cycle Count" in label:
                    metrics[label] = value
                else:
                    details[label] = value
            elif len(cells) == 4 and "Date" in cells[0].get_text(strip=True):
                # Extract usage history for the last 7 days
                for usage_row in row.find_next_siblings("tr", limit=7):
                    usage_cells = usage_row.find_all("td")
                    if len(usage_cells) == 4:
                        date = usage_cells[0].get_text(strip=True)
                        active_time = usage_cells[1].get_text(strip=True)
                        energy_drain = usage_cells[2].get_text(strip=True)
                        energy_usage = usage_cells[3].get_text(strip=True)
                        usage_history.append({
                            "Date": date,
                            "Active Time": active_time,
                            "Energy Drain": energy_drain,
                            "Energy Usage": energy_usage
                        })
    except Exception as e:
        print(f"Error parsing battery report: {e}")
        raise

    return metrics, details, usage_history

if __name__ == "__main__":
    # For testing purposes, generate and then parse the report.
    generate_battery_report()
    battery_metrics, battery_details, battery_usage_history = parse_battery_report()
    print("Parsed Battery Metrics:")
    for key, value in battery_metrics.items():
        print(f"{key}: {value}")
    print("\nParsed Battery Details:")
    for key, value in battery_details.items():
        print(f"{key}: {value}")
    print("\nBattery Usage History (Last 7 Days):")
    for usage in battery_usage_history:
        print(usage)
