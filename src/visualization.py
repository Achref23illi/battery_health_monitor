import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import numpy as np
import re

def plot_capacity_history(periods, full_charge_capacities, design_capacities):
    """
    Plots the battery capacity history.
    
    Parameters:
        periods (list): A list of strings representing the reporting periods.
        full_charge_capacities (list): A list of full charge capacity values (in mWh) over time.
        design_capacities (list): A list of design capacity values (in mWh) corresponding to each period.
        
    Returns:
        Figure: Matplotlib figure containing the plot
    """
    fig = Figure(figsize=(10, 6))
    ax = fig.add_subplot(111)
    
    # Only plot if we have data
    if periods and full_charge_capacities and design_capacities:
        # Ensure we have data to plot
        if len(periods) > 10:
            # If there are too many periods, just show the latest 10
            periods = periods[-10:]
            full_charge_capacities = full_charge_capacities[-10:]
            design_capacities = design_capacities[-10:]
        
        # Create x-positions for the bars
        x = np.arange(len(periods))
        width = 0.35
        
        # Plot bars
        bar1 = ax.bar(x - width/2, full_charge_capacities, width, label='Full Charge Capacity', color='#4a86e8')
        bar2 = ax.bar(x + width/2, design_capacities, width, label='Design Capacity', color='#ff9900', alpha=0.7)
        
        # Calculate health percentage
        health_percentages = [(fc / dc * 100) if dc > 0 else 0 
                             for fc, dc in zip(full_charge_capacities, design_capacities)]
        
        # Add health percentage text above bars
        for i, (fc, hp) in enumerate(zip(full_charge_capacities, health_percentages)):
            ax.text(i - width/2, fc + max(full_charge_capacities) * 0.05, f"{hp:.1f}%", 
                   ha='center', va='bottom', fontsize=9, fontweight='bold', color='#333333')
            
        # Set labels and title
        ax.set_xlabel("Period", fontsize=11, fontweight='bold')
        ax.set_ylabel("Capacity (mWh)", fontsize=11, fontweight='bold')
        ax.set_title("Battery Capacity History and Health Percentage", fontsize=13, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(periods, rotation=45, ha='right')
        ax.legend(loc='upper right')
        ax.grid(True, alpha=0.3)
        
        # Set y-limit with some padding
        max_capacity = max(max(full_charge_capacities), max(design_capacities))
        ax.set_ylim(0, max_capacity * 1.15)
    else:
        ax.text(0.5, 0.5, "No capacity history data available", 
                ha='center', va='center', transform=ax.transAxes, fontsize=12)
    
    fig.tight_layout()
    return fig

def create_battery_health_gauge(full_charge, design_capacity):
    """
    Creates a gauge chart showing current battery health as a percentage of design capacity.
    
    Parameters:
        full_charge (int or str): Current full charge capacity in mWh
        design_capacity (int or str): Original design capacity in mWh
        
    Returns:
        Figure: Matplotlib figure containing the gauge chart
    """
    fig = Figure(figsize=(6, 4))
    ax = fig.add_subplot(111, polar=True)
    
    # Process input values to ensure we have integers
    try:
        # Handle string values with units (e.g., "45000 mWh")
        if isinstance(full_charge, str):
            match = re.search(r'(\d+)', full_charge)
            if match:
                full_charge = int(match.group(1))
            else:
                full_charge = 0
        
        if isinstance(design_capacity, str):
            match = re.search(r'(\d+)', design_capacity)
            if match:
                design_capacity = int(match.group(1))
            else:
                design_capacity = 1  # Avoid division by zero
        
        # Ensure we have positive values
        full_charge = max(0, full_charge)
        design_capacity = max(1, design_capacity)  # Avoid division by zero
        
        # Calculate health percentage
        health_pct = min(100, (full_charge / design_capacity) * 100)
    except (ValueError, TypeError, ZeroDivisionError) as e:
        print(f"Error calculating battery health: {e}")
        health_pct = 0
    
    # Gauge settings
    theta = np.linspace(np.pi/2, 3*np.pi/2, 100)
    radii = np.ones_like(theta)
    
    # Map health percentage to color (green->yellow->red)
    if health_pct > 80:
        color = '#4CAF50'  # Green
    elif health_pct > 60:
        color = '#8BC34A'  # Light green
    elif health_pct > 40:
        color = '#FFC107'  # Amber
    elif health_pct > 20:
        color = '#FF9800'  # Orange
    else:
        color = '#F44336'  # Red
    
    # Background gauge (grey)
    ax.bar(theta, radii, width=np.pi, bottom=0.0, color='#E0E0E0', alpha=0.5)
    
    # Health percentage gauge
    if health_pct > 0:  # Only draw if we have a non-zero health percentage
        health_theta = np.linspace(np.pi/2, np.pi/2 + np.pi * health_pct/100, 100)
        health_radii = np.ones_like(health_theta)
        ax.bar(health_theta, health_radii, width=np.pi * health_pct/100, bottom=0.0, color=color, alpha=0.8)
    
    # Remove spines and ticks
    ax.set_yticks([])
    ax.spines['polar'].set_visible(False)
    
    # Set custom labels
    labels = ['100%', '75%', '50%', '25%', '0%']
    positions = [np.pi/2, np.pi/2 + np.pi/4, np.pi, np.pi + np.pi/4, 3*np.pi/2]
    ax.set_xticks(positions)
    ax.set_xticklabels(labels, fontsize=10, fontweight='bold')
    
    # Add text in the center
    ax.text(0, 0, f"{health_pct:.1f}%", ha='center', va='center', 
           fontsize=24, fontweight='bold', color='#333333')
    
    fig.tight_layout()
    return fig

# For testing purposes
if __name__ == "__main__":
    # Sample data
    sample_periods = ["Jan 2023", "Feb 2023", "Mar 2023"]
    sample_full_charge = [42000, 40000, 39000]
    sample_design = [45000, 45000, 45000]
    
    fig = plot_capacity_history(sample_periods, sample_full_charge, sample_design)
    plt.figure(fig.number)
    plt.show()
    
    gauge_fig = create_battery_health_gauge(39000, 45000)
    plt.figure(gauge_fig.number)
    plt.show()