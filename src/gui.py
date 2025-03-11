import tkinter as tk
from tkinter import scrolledtext, ttk, messagebox, Frame
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os
import webbrowser
from src.battery_repport import generate_battery_report, parse_battery_report
from src.visualization import plot_capacity_history, create_battery_health_gauge

class BatteryHealthMonitorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Battery Health Monitor")
        self.root.geometry("1100x800")
        self.root.minsize(800, 600)
        
        # Set theme colors
        self.bg_color = "#f5f5f5"
        self.accent_color = "#4a86e8"
        self.header_color = "#2d5bb9"
        self.success_color = "#4CAF50"
        self.warning_color = "#FFC107"
        self.error_color = "#F44336"
        
        # Configure root window
        self.root.configure(bg=self.bg_color)
        
        # Variables
        self.report_path = None
        self.html_content = None
        
        # Create main frame
        self.main_frame = tk.Frame(self.root, bg=self.bg_color)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create header
        self.create_header()
        
        # Create content
        self.create_content()
        
        # Create status bar
        self.create_status_bar()
    
    def create_header(self):
        """Create the header section with app title and buttons"""
        header_frame = tk.Frame(self.main_frame, bg=self.header_color)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        # App title
        title_label = tk.Label(header_frame, text="Battery Health Monitor", 
                               fg="white", bg=self.header_color, font=("Arial", 16, "bold"))
        title_label.pack(side=tk.LEFT, padx=10, pady=10)
        
        # Button frame
        button_frame = tk.Frame(header_frame, bg=self.header_color)
        button_frame.pack(side=tk.RIGHT, padx=10, pady=10)
        
        # Generate Report button
        generate_button_style = {'bg': self.success_color, 'fg': 'white', 
                                'activebackground': '#388E3C', 'activeforeground': 'white',
                                'font': ('Arial', 10, 'bold'), 'bd': 0, 'padx': 15, 'pady': 5}
        self.generate_button = tk.Button(button_frame, text="Generate Report", 
                                        command=self.generate_report, **generate_button_style)
        self.generate_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # View HTML button
        view_button_style = {'bg': self.accent_color, 'fg': 'white', 
                           'activebackground': '#3a6bc2', 'activeforeground': 'white',
                           'font': ('Arial', 10), 'bd': 0, 'padx': 10, 'pady': 5}
        self.view_button = tk.Button(button_frame, text="View Full HTML Report", 
                                   command=self.open_html_report, **view_button_style)
        self.view_button.pack(side=tk.LEFT)
        
    def create_content(self):
        """Create the main content area with tabs"""
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create dashboard tab
        self.dashboard_tab = tk.Frame(self.notebook, bg=self.bg_color)
        self.notebook.add(self.dashboard_tab, text="Dashboard")
        
        # Create details tab
        self.details_tab = tk.Frame(self.notebook, bg=self.bg_color)
        self.notebook.add(self.details_tab, text="Battery Details")
        
        # Create history tab
        self.history_tab = tk.Frame(self.notebook, bg=self.bg_color)
        self.notebook.add(self.history_tab, text="Usage History")
        
        # Create HTML preview tab
        self.html_tab = tk.Frame(self.notebook, bg=self.bg_color)
        self.notebook.add(self.html_tab, text="HTML Preview")
        
        # Setup dashboard tab
        self.setup_dashboard()
        
        # Setup details tab
        self.setup_details_tab()
        
        # Setup history tab
        self.setup_history_tab()
        
        # Setup HTML preview tab
        self.setup_html_preview()
    
    def setup_dashboard(self):
        """Setup the dashboard tab with summary and visualizations"""
        # Create two frames side by side
        left_frame = tk.Frame(self.dashboard_tab, bg=self.bg_color)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        right_frame = tk.Frame(self.dashboard_tab, bg=self.bg_color)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Summary section in left frame
        summary_frame = tk.LabelFrame(left_frame, text="Battery Summary", bg=self.bg_color, 
                                     font=("Arial", 11, "bold"))
        summary_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Summary text widget
        self.summary_text = scrolledtext.ScrolledText(summary_frame, wrap=tk.WORD, 
                                                    bg="white", font=("Arial", 11))
        self.summary_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Battery health gauge in right frame (top)
        self.gauge_frame = tk.LabelFrame(right_frame, text="Battery Health", bg=self.bg_color, 
                                       font=("Arial", 11, "bold"))
        self.gauge_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Capacity history chart in right frame (bottom)
        self.capacity_frame = tk.LabelFrame(right_frame, text="Capacity History", bg=self.bg_color, 
                                          font=("Arial", 11, "bold"))
        self.capacity_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def setup_details_tab(self):
        """Setup the details tab with all battery information"""
        details_frame = tk.Frame(self.details_tab, bg=self.bg_color)
        details_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Metrics and details section
        self.details_text = scrolledtext.ScrolledText(details_frame, wrap=tk.WORD, 
                                                    bg="white", font=("Arial", 11))
        self.details_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def setup_history_tab(self):
        """Setup the history tab with usage history table"""
        history_frame = tk.Frame(self.history_tab, bg=self.bg_color)
        history_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create Treeview for usage history
        columns = ("Date", "Active", "Energy Drain", "Energy Usage")
        self.history_tree = ttk.Treeview(history_frame, columns=columns, show="headings")
        
        # Configure columns
        for col in columns:
            self.history_tree.heading(col, text=col)
            if col == "Date":
                self.history_tree.column(col, width=150, anchor="w")
            else:
                self.history_tree.column(col, width=120, anchor="center")
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(history_frame, orient="vertical", command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack widgets
        self.history_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def setup_html_preview(self):
        """Setup the HTML preview tab"""
        html_frame = tk.Frame(self.html_tab, bg=self.bg_color)
        html_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create text widget with horizontal and vertical scrollbars
        self.html_text = scrolledtext.ScrolledText(html_frame, wrap=tk.NONE, 
                                                 bg="white", font=("Courier New", 10))
        self.html_text.pack(fill=tk.BOTH, expand=True)
        
        # Add horizontal scrollbar
        h_scrollbar = ttk.Scrollbar(html_frame, orient="horizontal", command=self.html_text.xview)
        self.html_text.configure(xscrollcommand=h_scrollbar.set)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def create_status_bar(self):
        """Create status bar at the bottom"""
        self.status_bar = tk.Label(self.root, text="Ready", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def generate_report(self):
        """Generate battery report and update the UI"""
        try:
            self.status_bar.config(text="Generating battery report...")
            self.root.update()
            
            # Generate the report
            self.report_path = generate_battery_report()
            
            # Parse the report
            metrics, details, usage_history, capacity_data, html_content = parse_battery_report(self.report_path)
            self.html_content = html_content
            
            # Update UI
            self.update_dashboard(metrics, details, capacity_data)
            self.update_details(metrics, details)
            self.update_history(usage_history)
            self.update_html_preview(html_content)
            
            # Show success message
            self.status_bar.config(text=f"Report generated successfully at {self.report_path}")
            messagebox.showinfo("Success", "Battery report generated and parsed successfully!")
            
        except Exception as e:
            self.status_bar.config(text=f"Error: {str(e)}")
            messagebox.showerror("Error", f"Failed to generate battery report: {str(e)}")
    
    def update_dashboard(self, metrics, details, capacity_data):
        """Update the dashboard tab with battery data"""
        # Clear existing widgets in visualization frames
        for widget in self.gauge_frame.winfo_children():
            widget.destroy()
        
        for widget in self.capacity_frame.winfo_children():
            widget.destroy()
        
        # Update summary text
        self.summary_text.delete(1.0, tk.END)
        
        # Add header
        self.summary_text.insert(tk.END, "BATTERY SUMMARY\n", "header")
        self.summary_text.tag_configure("header", font=("Arial", 12, "bold"))
        self.summary_text.insert(tk.END, "\n")
        
        # Add metrics
        for key, value in metrics.items():
            self.summary_text.insert(tk.END, f"{key}: ", "label")
            self.summary_text.insert(tk.END, f"{value}\n", "value")
        
        self.summary_text.tag_configure("label", font=("Arial", 11, "bold"))
        self.summary_text.tag_configure("value", font=("Arial", 11))
        
        # Add some selected details
        self.summary_text.insert(tk.END, "\n")
        important_keys = ["Manufacturer", "Serial Number", "Chemistry", "Name"]
        for key, value in details.items():
            if any(important in key for important in important_keys):
                self.summary_text.insert(tk.END, f"{key}: ", "label")
                self.summary_text.insert(tk.END, f"{value}\n", "value")
        
        # Create battery health gauge
        try:
            design_capacity = int(metrics.get("Design Capacity", "0 mWh").split()[0])
            full_charge = int(metrics.get("Full Charge Capacity", "0 mWh").split()[0])
            
            gauge_fig = create_battery_health_gauge(full_charge, design_capacity)
            gauge_canvas = FigureCanvasTkAgg(gauge_fig, master=self.gauge_frame)
            gauge_canvas.draw()
            gauge_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        except Exception as e:
            print(f"Error creating gauge: {e}")
        
        # Create capacity history chart
        try:
            periods, full_charges, design_capacities = capacity_data
            if periods:
                capacity_fig = plot_capacity_history(periods, full_charges, design_capacities)
                capacity_canvas = FigureCanvasTkAgg(capacity_fig, master=self.capacity_frame)
                capacity_canvas.draw()
                capacity_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        except Exception as e:
            print(f"Error creating capacity chart: {e}")
    
    def update_details(self, metrics, details):
        """Update the details tab with all battery information"""
        self.details_text.delete(1.0, tk.END)
        
        # Add metrics section
        self.details_text.insert(tk.END, "BATTERY METRICS\n", "section")
        self.details_text.tag_configure("section", font=("Arial", 12, "bold"))
        self.details_text.insert(tk.END, "\n")
        
        for key, value in metrics.items():
            self.details_text.insert(tk.END, f"{key}: ", "label")
            self.details_text.insert(tk.END, f"{value}\n", "value")
        
        # Add additional details
        self.details_text.insert(tk.END, "\n")
        self.details_text.insert(tk.END, "ADDITIONAL DETAILS\n", "section")
        self.details_text.insert(tk.END, "\n")
        
        for key, value in details.items():
            self.details_text.insert(tk.END, f"{key}: ", "label")
            self.details_text.insert(tk.END, f"{value}\n", "value")
        
        self.details_text.tag_configure("label", font=("Arial", 11, "bold"))
        self.details_text.tag_configure("value", font=("Arial", 11))
    
    def update_history(self, usage_history):
        """Update the history tab with usage data"""
        # Clear existing data
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
        
        # Add new data
        for usage in usage_history:
            values = []
            for col in self.history_tree["columns"]:
                values.append(usage.get(col, ""))
            
            self.history_tree.insert("", "end", values=values)
    
    def update_html_preview(self, html_content):
        """Update the HTML preview tab with report content"""
        self.html_text.delete(1.0, tk.END)
        self.html_text.insert(tk.END, html_content)
    
    def open_html_report(self):
        """Open the full HTML report in default browser"""
        if self.report_path and os.path.exists(self.report_path):
            webbrowser.open(f"file://{self.report_path}")
        else:
            messagebox.showinfo("No Report", "Please generate a battery report first.")

# Function to create and run the application
def run_app():
    root = tk.Tk()
    app = BatteryHealthMonitorApp(root)
    root.mainloop()

if __name__ == "__main__":
    run_app()