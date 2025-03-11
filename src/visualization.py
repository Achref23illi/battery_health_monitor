import matplotlib.pyplot as plt

def plot_capacity_history(periods, full_charge_capacities, design_capacities):
    """
    Plots the battery capacity history.
    
    Parameters:
        periods (list): A list of strings representing the reporting periods.
        full_charge_capacities (list): A list of full charge capacity values (in mWh) over time.
        design_capacities (list): A list of design capacity values (in mWh) corresponding to each period.
    """
    plt.figure(figsize=(10, 6))
    plt.plot(periods, full_charge_capacities, marker='o', linestyle='-', label='Full Charge Capacity')
    plt.plot(periods, design_capacities, marker='o', linestyle='--', label='Design Capacity')
    
    plt.xlabel("Period")
    plt.ylabel("Capacity (mWh)")
    plt.title("Battery Capacity History")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

# For testing purposes, run a sample plot when executing this file directly.
if __name__ == "__main__":
    # Sample data (replace with real parsed data later)
    sample_periods = ["Period 1", "Period 2", "Period 3"]
    sample_full_charge = [20360, 14694, 21466]
    sample_design = [56999, 56999, 56999]
    plot_capacity_history(sample_periods, sample_full_charge, sample_design)
