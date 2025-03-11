# Battery Health Monitor

**Battery Health Monitor** is a Python-based desktop application for monitoring the health of your Windows battery. The app generates a detailed battery report using Windows’ built-in `powercfg` command, parses the resulting HTML report to extract key battery metrics, and visualizes the data through an interactive GUI built with Tkinter and matplotlib.

## Table of Contents

- [Features](#features)
- [Project Architecture](#project-architecture)
- [Installation](#installation)
- [Usage](#usage)
- [Development](#development)
- [Testing](#testing)
- [Future Enhancements](#future-enhancements)
- [License](#license)

## Features

- **Battery Report Generation:**  
  Automatically generate a battery report using the command:
  ```
  powercfg /batteryreport /output "battery-report.html"
  ```

- **Data Parsing:**  
  Extract key metrics (e.g., Design Capacity, Full Charge Capacity, Cycle Count) from the generated HTML report using BeautifulSoup.

- **Data Visualization:**  
  Visualize battery capacity history and other data trends with matplotlib.

- **Graphical User Interface (GUI):**  
  A simple, interactive desktop GUI built with Tkinter that allows you to:
  - Generate a new battery report.
  - Display parsed battery metrics.
  - View visualizations of battery performance.

- **Optional Packaging:**  
  Easily package the app as a standalone Windows executable using PyInstaller.

## Project Architecture

The project is structured for clarity and scalability:

```
battery_health_monitor/
├── docs/
│   └── README.md          # Project documentation and overview.
├── src/
│   ├── __init__.py        # Makes src a Python package.
│   ├── main.py            # Main entry point; launches the GUI.
│   ├── battery_report.py  # Module for generating and parsing the battery report.
│   ├── visualization.py   # Module for data visualization using matplotlib.
│   └── gui.py             # Module for the Tkinter-based GUI.
├── tests/
│   └── test_battery_report.py  # Unit tests for battery report parsing.
├── requirements.txt       # Python dependencies (BeautifulSoup, matplotlib).
├── setup.py               # (Optional) Packaging script for distribution.
└── .gitignore             # Files and directories to ignore in version control.
```

## Installation

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/Achref23illi/battery_health_monitor.git
   cd battery_health_monitor
   ```

2. **Create a Virtual Environment (Optional but recommended):**

   ```bash
   python -m venv venv
   source venv/bin/activate      # On Windows use: venv\Scripts\activate
   ```

3. **Install Dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

   The main dependencies include:
   - [beautifulsoup4](https://pypi.org/project/beautifulsoup4/)
   - [matplotlib](https://pypi.org/project/matplotlib/)

4. **(Optional) Install PyInstaller** if you want to package the app later:

   ```bash
   pip install pyinstaller
   ```

## Usage

### Running the Application

From the root of the project, run the main entry point:

```bash
python -m src.main
```

This will launch the Tkinter-based GUI with buttons to:
- **Generate Battery Report:** Runs the command to create `battery-report.html`.
- **Show Parsed Metrics:** Parses and displays key battery metrics from the report.
- **Plot Capacity History:** Displays a sample chart of battery capacity history.

### Testing the Application

A minimal test for parsing functionality is included in the `tests` directory. To run the tests:

```bash
python -m unittest discover tests
```

## Development

### Directory Overview

- **src/battery_report.py:**  
  Contains functions:
  - `generate_battery_report(output_path="battery-report.html")` to run the Windows command.
  - `parse_battery_report(file_path="battery-report.html")` to extract battery metrics using BeautifulSoup.

- **src/visualization.py:**  
  Contains functions to generate charts using matplotlib (e.g., `plot_capacity_history`).

- **src/gui.py:**  
  Contains the Tkinter GUI code that integrates battery report generation, data parsing, and visualization.

- **src/main.py:**  
  The main entry point that launches the GUI.

- **tests/test_battery_report.py:**  
  Contains unit tests to validate the parsing functions.

### Running in Development Mode

While developing, you can run individual modules to test functionality. For example, run `battery_report.py` directly to test report generation and parsing:

```bash
python src/battery_report.py
```

## Future Enhancements

- **Real-Time Monitoring:**  
  Integrate Windows APIs (e.g., WMI) to provide real-time battery data.

- **Enhanced Visualizations:**  
  Develop additional charts for battery drain trends and usage history.

- **UI/UX Improvements:**  
  Consider using more advanced GUI frameworks (such as PyQt) or a web-based UI for a more modern interface.

- **Automated Scheduling:**  
  Add functionality to automatically generate reports at regular intervals.

## License

This project is licensed under the [MIT License](LICENSE).

---

Feel free to contribute, open issues, or suggest improvements. Enjoy monitoring your battery health!

