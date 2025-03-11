import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os
import threading
import webbrowser
import sys
from datetime import datetime

# Import our modules - adjust paths if needed
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from battery_repport import generate_battery_report, parse_battery_report
from visualization import create_battery_health_gauge, plot_capacity_history

class BatteryReportApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Battery Health Analyzer")
        self.root.geometry("900x700")
        self.root.minsize(800, 600)
        
        # Set application icon if available
        try:
            self.root.iconbitmap("battery_icon.ico")
        except:
            pass
            
        # Variables
        self.report_path = None
        self.html_content = None
        self.loading = False
        
        # Create the main frame
        self.main_frame = ttk.Frame(self.root, padding=10)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create tabs
        self.dashboard_tab = ttk.Frame(self.notebook)
        self.details_tab = ttk.Frame(self.notebook)
        self.raw_data_tab = ttk.Frame(self.notebook)
        
        self.notebook.add(self.dashboard_tab, text="Dashboard")
        self.notebook.add(self.details_tab, text="Details")
        self.notebook.add(self.raw_data_tab, text="Raw Report")
        
        # Setup the UI
        self.setup_dashboard()
        self.setup_details_tab()
        self.setup_raw_data_tab()
        
        # Control frame at the bottom
        self.control_frame = ttk.Frame(self.main_frame)
        self.control_frame.pack(fill=tk.X, pady=10)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready. Click 'Generate Report' to start.")
        self.status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Buttons
        self.progress = ttk.Progressbar(self.control_frame, mode="indeterminate")
        self.progress.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        self.generate_btn = ttk.Button(self.control_frame, text="Generate Report", command=self.generate_report)
        self.generate_btn.pack(side=tk.LEFT, padx=5)
        
        self.load_btn = ttk.Button(self.control_frame, text="Load Existing Report", command=self.load_report)
        self.load_btn.pack(side=tk.LEFT, padx=5)
        
        self.export_btn = ttk.Button(self.control_frame, text="Export Data", command=self.export_data, state=tk.DISABLED)
        self.export_btn.pack(side=tk.LEFT, padx=5)
        
        # Initial setup
        self.progress.pack_forget()  # Hide progress initially

    def setup_dashboard(self):
        # Top frame for metrics
        top_frame = ttk.Frame(self.dashboard_tab)
        top_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Health gauge frame
        self.gauge_frame = ttk.LabelFrame(top_frame, text="Battery Health")
        self.gauge_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # Key metrics frame
        metrics_frame = ttk.LabelFrame(top_frame, text="Key Metrics")
        metrics_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # Placeholder for metrics
        self.metrics = {}
        for i, label in enumerate(["Design Capacity", "Full Charge Capacity", "Cycle Count", "Battery Health"]):
            lbl = ttk.Label(metrics_frame, text=f"{label}:", font=("", 10, "bold"))
            lbl.grid(row=i, column=0, sticky=tk.W, padx=10, pady=5)
            
            val = ttk.Label(metrics_frame, text="N/A")
            val.grid(row=i, column=1, sticky=tk.W, padx=10, pady=5)
            self.metrics[label] = val
        
        # Bottom frame for chart
        bottom_frame = ttk.LabelFrame(self.dashboard_tab, text="Capacity History")
        bottom_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Placeholder for gauge
        self.gauge_placeholder = ttk.Label(self.gauge_frame, text="Generate a report to see battery health")
        self.gauge_placeholder.pack(padx=20, pady=30)
        self.gauge_canvas = None
        
        # Placeholder for chart
        self.chart_placeholder = ttk.Label(bottom_frame, text="Generate a report to see capacity history")
        self.chart_placeholder.pack(padx=20, pady=50)
        self.chart_canvas = None

    def setup_details_tab(self):
        # Create a frame for the details
        self.details_frame = ttk.Frame(self.details_tab)
        self.details_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Add two sections: Battery Details and Usage History
        details_pane = ttk.PanedWindow(self.details_frame, orient=tk.HORIZONTAL)
        details_pane.pack(fill=tk.BOTH, expand=True)
        
        # Battery details section
        self.battery_details_frame = ttk.LabelFrame(details_pane, text="Battery Details")
        details_pane.add(self.battery_details_frame, weight=50)
        
        # Scrollable frame for battery details
        details_canvas = tk.Canvas(self.battery_details_frame)
        details_scrollbar = ttk.Scrollbar(self.battery_details_frame, orient="vertical", command=details_canvas.yview)
        details_canvas.configure(yscrollcommand=details_scrollbar.set)
        
        details_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        details_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.details_content_frame = ttk.Frame(details_canvas)
        details_canvas.create_window((0, 0), window=self.details_content_frame, anchor=tk.NW)
        
        self.details_content_frame.bind("<Configure>", lambda e: details_canvas.configure(scrollregion=details_canvas.bbox("all")))
        
        # Usage history section
        self.usage_history_frame = ttk.LabelFrame(details_pane, text="Battery Usage History")
        details_pane.add(self.usage_history_frame, weight=50)
        
        # Treeview for usage history
        self.usage_tree = ttk.Treeview(self.usage_history_frame)
        usage_scrollbar = ttk.Scrollbar(self.usage_history_frame, orient="vertical", command=self.usage_tree.yview)
        self.usage_tree.configure(yscrollcommand=usage_scrollbar.set)
        
        usage_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.usage_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Add placeholder text
        ttk.Label(self.details_content_frame, text="Generate a report to see battery details").pack(pady=20, padx=20)
        
        # Add placeholder columns to treeview
        self.usage_tree["columns"] = ("date", "duration", "energy")
        self.usage_tree.column("#0", width=0, stretch=tk.NO)
        self.usage_tree.column("date", anchor=tk.W, width=120)
        self.usage_tree.column("duration", anchor=tk.W, width=120)
        self.usage_tree.column("energy", anchor=tk.W, width=120)
        
        self.usage_tree.heading("#0", text="", anchor=tk.W)
        self.usage_tree.heading("date", text="Date", anchor=tk.W)
        self.usage_tree.heading("duration", text="Duration", anchor=tk.W)
        self.usage_tree.heading("energy", text="Energy Used", anchor=tk.W)

    def setup_raw_data_tab(self):
        # Create a frame for the raw HTML view
        raw_frame = ttk.Frame(self.raw_data_tab)
        raw_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Add controls at the top
        controls_frame = ttk.Frame(raw_frame)
        controls_frame.pack(fill=tk.X)
        
        ttk.Label(controls_frame, text="Report Location:").pack(side=tk.LEFT, padx=(0, 5))
        
        self.report_location_var = tk.StringVar(value="No report generated yet")
        location_label = ttk.Label(controls_frame, textvariable=self.report_location_var, foreground="blue", cursor="hand2")
        location_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        location_label.bind("<Button-1>", self.open_report_location)
        
        open_btn = ttk.Button(controls_frame, text="Open in Browser", command=self.open_in_browser)
        open_btn.pack(side=tk.LEFT, padx=5)
        
        refresh_btn = ttk.Button(controls_frame, text="Refresh", command=self.refresh_raw_data)
        refresh_btn.pack(side=tk.LEFT, padx=5)
        
        # Add text area with scrollbars
        text_frame = ttk.Frame(raw_frame)
        text_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.raw_text = tk.Text(text_frame, wrap=tk.NONE)
        y_scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.raw_text.yview)
        x_scrollbar = ttk.Scrollbar(text_frame, orient=tk.HORIZONTAL, command=self.raw_text.xview)
        
        self.raw_text.configure(yscrollcommand=y_scrollbar.set, xscrollcommand=x_scrollbar.set)
        
        y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        x_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.raw_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Make text read-only
        self.raw_text.configure(state=tk.DISABLED)
        
        # Add placeholder text
        self.set_raw_text_content("Generate a report to see raw HTML data")

    def set_raw_text_content(self, content):
        self.raw_text.configure(state=tk.NORMAL)
        self.raw_text.delete(1.0, tk.END)
        self.raw_text.insert(tk.END, content)
        self.raw_text.configure(state=tk.DISABLED)

    def open_report_location(self, event=None):
        if self.report_path and os.path.exists(self.report_path):
            # Open the folder containing the report
            folder_path = os.path.dirname(os.path.abspath(self.report_path))
            if sys.platform == 'win32':
                os.startfile(folder_path)
            elif sys.platform == 'darwin':  # macOS
                os.system(f'open "{folder_path}"')
            else:  # Linux
                os.system(f'xdg-open "{folder_path}"')

    def open_in_browser(self):
        if self.report_path and os.path.exists(self.report_path):
            webbrowser.open(f"file://{os.path.abspath(self.report_path)}")
        else:
            messagebox.showinfo("No Report", "No battery report has been generated yet.")

    def refresh_raw_data(self):
        if self.report_path and os.path.exists(self.report_path):
            try:
                with open(self.report_path, "r", encoding="utf-8") as f:
                    html_content = f.read()
                self.set_raw_text_content(html_content)
                self.html_content = html_content
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load report: {e}")

    def generate_report(self):
        if self.loading:
            return
            
        self.loading = True
        self.progress.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.progress.start()
        self.status_var.set("Generating battery report...")
        self.generate_btn.configure(state=tk.DISABLED)
        self.load_btn.configure(state=tk.DISABLED)
        
        def process():
            try:
                # Generate the report
                timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
                output_path = os.path.join(os.path.expanduser("~"), f"battery-report-{timestamp}.html")
                
                self.report_path = generate_battery_report(output_path)
                self.report_location_var.set(self.report_path)
                
                # Parse the report
                metrics, details, usage_history, capacity_data, html_content = parse_battery_report(self.report_path)
                self.html_content = html_content
                
                # Update the UI with the results
                self.root.after(0, lambda: self.update_ui(metrics, details, usage_history, capacity_data))
                
                # Set status message
                self.root.after(0, lambda: self.status_var.set("Report generated successfully."))
                
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", f"Error generating report: {e}"))
                self.root.after(0, lambda: self.status_var.set(f"Error: {str(e)}"))
            finally:
                # Re-enable buttons and stop progress
                self.root.after(0, lambda: self.progress.stop())
                self.root.after(0, lambda: self.progress.pack_forget())
                self.root.after(0, lambda: self.generate_btn.configure(state=tk.NORMAL))
                self.root.after(0, lambda: self.load_btn.configure(state=tk.NORMAL))
                self.root.after(0, lambda: self.export_btn.configure(state=tk.NORMAL))
                self.loading = False
        
        # Run the process in a separate thread
        thread = threading.Thread(target=process)
        thread.daemon = True
        thread.start()

    def load_report(self):
        file_path = filedialog.askopenfilename(
            title="Select Battery Report",
            filetypes=[("HTML files", "*.html"), ("All files", "*.*")]
        )
        
        if file_path:
            self.loading = True
            self.progress.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
            self.progress.start()
            self.status_var.set("Loading battery report...")
            self.generate_btn.configure(state=tk.DISABLED)
            self.load_btn.configure(state=tk.DISABLED)
            
            def process():
                try:
                    self.report_path = file_path
                    self.report_location_var.set(file_path)
                    
                    # Parse the existing report
                    metrics, details, usage_history, capacity_data, html_content = parse_battery_report(file_path)
                    self.html_content = html_content
                    
                    # Update the UI
                    self.root.after(0, lambda: self.update_ui(metrics, details, usage_history, capacity_data))
                    
                    # Set status message
                    self.root.after(0, lambda: self.status_var.set("Report loaded successfully."))
                    
                except Exception as e:
                    self.root.after(0, lambda: messagebox.showerror("Error", f"Error loading report: {e}"))
                    self.root.after(0, lambda: self.status_var.set(f"Error: {str(e)}"))
                finally:
                    # Re-enable buttons and stop progress
                    self.root.after(0, lambda: self.progress.stop())
                    self.root.after(0, lambda: self.progress.pack_forget())
                    self.root.after(0, lambda: self.generate_btn.configure(state=tk.NORMAL))
                    self.root.after(0, lambda: self.load_btn.configure(state=tk.NORMAL))
                    self.root.after(0, lambda: self.export_btn.configure(state=tk.NORMAL))
                    self.loading = False
            
            # Run the process in a separate thread
            thread = threading.Thread(target=process)
            thread.daemon = True
            thread.start()

    def update_ui(self, metrics, details, usage_history, capacity_data):
        # Update metrics display
        for key, label in self.metrics.items():
            value = metrics.get(key, "N/A")
            label.configure(text=value)
        
        # Update gauge
        self.update_gauge(metrics)
        
        # Update capacity history
        self.update_capacity_chart(capacity_data)
        
        # Update details tab
        self.update_details(details)
        
        # Update usage history
        self.update_usage_history(usage_history)
        
        # Update raw data tab
        self.set_raw_text_content(self.html_content if self.html_content else "No data available")
    
    def update_gauge(self, metrics):
        # Extract values for the gauge
        design_capacity = metrics.get("Design Capacity", "0 mWh")
        full_charge = metrics.get("Full Charge Capacity", "0 mWh")
        
        # Clear the current gauge if exists
        if self.gauge_canvas:
            self.gauge_canvas.get_tk_widget().destroy()
            self.gauge_canvas = None
        
        if self.gauge_placeholder:
            self.gauge_placeholder.pack_forget()
            self.gauge_placeholder = None
        
        # Create the gauge figure
        fig = create_battery_health_gauge(full_charge, design_capacity)
        
        # Add the figure to the frame
        self.gauge_canvas = FigureCanvasTkAgg(fig, master=self.gauge_frame)
        self.gauge_canvas.draw()
        self.gauge_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def update_capacity_chart(self, capacity_data):
        periods, full_charges, design_capacities = capacity_data
        
        # Clear the current chart if exists
        if self.chart_canvas:
            self.chart_canvas.get_tk_widget().destroy()
            self.chart_canvas = None
        
        if self.chart_placeholder:
            self.chart_placeholder.pack_forget()
            self.chart_placeholder = None
        
        # Create the capacity history chart
        fig = plot_capacity_history(periods, full_charges, design_capacities)
        
        # Get the parent widget (the Capacity History LabelFrame)
        parent = self.dashboard_tab.winfo_children()[1]
        
        # Add the figure to the frame
        self.chart_canvas = FigureCanvasTkAgg(fig, master=parent)
        self.chart_canvas.draw()
        self.chart_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def update_details(self, details):
        # Clear existing details
        for widget in self.details_content_frame.winfo_children():
            widget.destroy()
        
        # Add details to the frame
        row = 0
        for key, value in details.items():
            key_label = ttk.Label(self.details_content_frame, text=f"{key}:", font=("", 10, "bold"))
            key_label.grid(row=row, column=0, sticky=tk.W, padx=10, pady=5)
            
            value_label = ttk.Label(self.details_content_frame, text=value)
            value_label.grid(row=row, column=1, sticky=tk.W, padx=10, pady=5)
            
            row += 1
    
    def update_usage_history(self, usage_history):
        # Clear existing items
        for item in self.usage_tree.get_children():
            self.usage_tree.delete(item)
        
        # Configure columns based on actual data
        if usage_history and len(usage_history) > 0:
            # Get the keys from the first history item
            columns = list(usage_history[0].keys())
            
            # Configure columns
            self.usage_tree["columns"] = columns
            
            # Remove old column headings
            for col in self.usage_tree["columns"]:
                self.usage_tree.heading(col, text="")
                self.usage_tree.column(col, width=0)
            
            # Add new column headings
            for col in columns:
                display_name = col.replace("_", " ").title()
                self.usage_tree.heading(col, text=display_name, anchor=tk.W)
                self.usage_tree.column(col, anchor=tk.W, width=100)
            
            # Add data
            for i, usage in enumerate(usage_history):
                values = [usage.get(col, "") for col in columns]
                self.usage_tree.insert("", tk.END, text=f"Item {i+1}", values=values)

    def export_data(self):
        if not self.report_path:
            messagebox.showinfo("No Data", "No battery report has been generated or loaded yet.")
            return
        
        # Ask for file location
        file_path = filedialog.asksaveasfilename(
            title="Export Battery Report Data",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if not file_path:
            return
        
        try:
            # Parse the report again to get fresh data
            metrics, details, usage_history, capacity_data, _ = parse_battery_report(self.report_path)
            
            # Write to CSV
            with open(file_path, "w", encoding="utf-8") as f:
                f.write("Battery Report Data Export\n")
                f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                # Write metrics
                f.write("Battery Metrics\n")
                for key, value in metrics.items():
                    f.write(f"{key},{value}\n")
                f.write("\n")
                
                # Write details
                f.write("Battery Details\n")
                for key, value in details.items():
                    f.write(f"{key},{value}\n")
                f.write("\n")
                
                # Write usage history
                f.write("Battery Usage History\n")
                if usage_history and len(usage_history) > 0:
                    # Write header
                    headers = list(usage_history[0].keys())
                    f.write(",".join(headers) + "\n")
                    
                    # Write data
                    for usage in usage_history:
                        values = [str(usage.get(header, "")) for header in headers]
                        f.write(",".join(values) + "\n")
                f.write("\n")
                
                # Write capacity history
                f.write("Battery Capacity History\n")
                periods, full_charges, design_capacities = capacity_data
                f.write("Period,Full Charge Capacity (mWh),Design Capacity (mWh)\n")
                for i in range(len(periods)):
                    f.write(f"{periods[i]},{full_charges[i]},{design_capacities[i]}\n")
            
            messagebox.showinfo("Export Successful", f"Data exported successfully to {file_path}")
            
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export data: {e}")

def main():
    root = tk.Tk()
    app = BatteryReportApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()