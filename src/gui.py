import tkinter as tk
from tkinter import scrolledtext, ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from src.battery_repport import generate_battery_report, parse_battery_report
from src.visualization import plot_capacity_history

def generate_report_callback():
    """
    Callback to generate the battery report and update the status label.
    """
    try:
        generate_battery_report()
        status_label.config(text="Battery report generated successfully.")
    except Exception as e:
        status_label.config(text=f"Error generating report: {e}")

def show_metrics_callback():
    """
    Callback to parse the battery report and display its key metrics in the text box.
    """
    try:
        metrics, details, usage_history = parse_battery_report()
        display_text = "\n".join([f"{key}: {value}" for key, value in metrics.items()])
        report_box.delete("1.0", tk.END)
        report_box.insert(tk.END, display_text)
        
        details_text = "\n".join([f"{key}: {value}" for key, value in details.items()])
        details_label.config(text=details_text)
        
        # Update usage history table
        for row in usage_history_table.get_children():
            usage_history_table.delete(row)
        for usage in usage_history:
            usage_history_table.insert("", "end", values=(usage["Date"], usage["Active Time"], usage["Energy Drain"], usage["Energy Usage"]))
        
        # Update visualizations
        update_visualizations(metrics)
    except Exception as e:
        report_box.delete("1.0", tk.END)
        report_box.insert(tk.END, f"Error parsing report: {e}")
        details_label.config(text=f"Error parsing report: {e}")

def update_visualizations(metrics):
    """
    Update the visualizations with the parsed battery metrics.
    """
    # Clear previous plots
    for widget in visualizations_frame.winfo_children():
        widget.destroy()
    
    # Create new plots
    fig = Figure(figsize=(8, 4))
    ax = fig.add_subplot(111)
    
    # Sample data for demonstration
    periods = ["Period 1", "Period 2", "Period 3"]
    full_charge_capacities = [20360, 14694, 21466]
    design_capacities = [56999, 56999, 56999]
    
    ax.plot(periods, full_charge_capacities, marker='o', linestyle='-', label='Full Charge Capacity')
    ax.plot(periods, design_capacities, marker='o', linestyle='--', label='Design Capacity')
    ax.set_xlabel("Period")
    ax.set_ylabel("Capacity (mWh)")
    ax.set_title("Battery Capacity History")
    ax.legend()
    ax.grid(True)
    
    canvas = FigureCanvasTkAgg(fig, master=visualizations_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

# Create the main application window
root = tk.Tk()
root.title("Battery Health Monitor")
root.geometry("1000x800")

# Create a frame for the buttons
button_frame = tk.Frame(root)
button_frame.pack(pady=10)

# Button: Generate Battery Report
gen_button = tk.Button(button_frame, text="Generate Battery Report", command=generate_report_callback)
gen_button.grid(row=0, column=0, padx=10)

# Button: Show Parsed Metrics
parse_button = tk.Button(button_frame, text="Show Parsed Metrics", command=show_metrics_callback)
parse_button.grid(row=0, column=1, padx=10)

# Status label for feedback messages
status_label = tk.Label(root, text="Status messages will appear here.", fg="blue")
status_label.pack(pady=5)

# A notebook widget to organize different sections
notebook = ttk.Notebook(root)
notebook.pack(expand=True, fill='both')

# Tab for displaying parsed battery report metrics
metrics_tab = ttk.Frame(notebook)
notebook.add(metrics_tab, text="Battery Metrics")

# A scrolled text box to display the parsed battery report metrics
report_box = scrolledtext.ScrolledText(metrics_tab, wrap=tk.WORD, width=80, height=20)
report_box.pack(pady=10, padx=10, expand=True, fill='both')

# Tab for displaying additional battery details
details_tab = ttk.Frame(notebook)
notebook.add(details_tab, text="Battery Details")

# Add more detailed battery metrics here
details_label = tk.Label(details_tab, text="Additional Battery Details will be displayed here.", wraplength=700, justify="left")
details_label.pack(pady=10, padx=10)

# Tab for displaying usage history
usage_history_tab = ttk.Frame(notebook)
notebook.add(usage_history_tab, text="Usage History")

# Table for displaying usage history
columns = ("Date", "Active Time", "Energy Drain", "Energy Usage")
usage_history_table = ttk.Treeview(usage_history_tab, columns=columns, show="headings")
for col in columns:
    usage_history_table.heading(col, text=col)
    usage_history_table.column(col, width=150)
usage_history_table.pack(pady=10, padx=10, expand=True, fill='both')

# Tab for displaying visualizations
visualizations_tab = ttk.Frame(notebook)
notebook.add(visualizations_tab, text="Visualizations")

# Frame for embedding visualizations
visualizations_frame = tk.Frame(visualizations_tab)
visualizations_frame.pack(pady=10, padx=10, expand=True, fill='both')

# Start the Tkinter event loop
root.mainloop()
