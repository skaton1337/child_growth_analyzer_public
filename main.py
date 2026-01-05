import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import os
import re
from io import StringIO
import ctypes
from datetime import datetime
from who_data import create_percentile_interpolators, calculate_exact_percentile

class ChildGrowthAnalyzer:
    def __init__(self, root):
        self.root = root
        self.root.title("Child Growth Analyzer v1.1.3 - by David Kühlwein")
        
        # Add last used directory tracking
        self.last_used_directory = os.path.dirname(os.path.abspath(__file__))
        
        # Set window and taskbar icon
        icon_path = 'app_icon.ico'
        self.root.iconbitmap(icon_path)
        # Set taskbar icon explicitly
        try:
            # This is needed for Windows taskbar icon
            import ctypes
            myappid = 'davidkuehlwein.childgrowthanalyzer.1.0.0'  # arbitrary string
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
            self.root.iconbitmap(default=icon_path)
        except Exception as e:
            print(f"Could not set taskbar icon: {e}")
        
        # Get screen dimensions
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        
        # Set window size to 90% of screen size
        window_width = int(screen_width * 0.9)
        window_height = int(screen_height * 0.9)
        
        # Calculate position for center of screen
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        # Set window size and position
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # Create main frame with scrollbars
        main_frame = ttk.Frame(root)
        main_frame.grid(row=0, column=0, sticky="nsew")
        
        # Configure root grid
        root.grid_rowconfigure(0, weight=1)
        root.grid_columnconfigure(0, weight=1)
        
        # Create canvas with scrollbar
        canvas = tk.Canvas(main_frame)
        scrollbar_y = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollbar_x = ttk.Scrollbar(main_frame, orient="horizontal", command=canvas.xview)
        
        # Configure canvas
        canvas.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        
        # Create frame for content
        self.content_frame = ttk.Frame(canvas)
        
        # Pack scrollbars and canvas
        scrollbar_y.pack(side="right", fill="y")
        scrollbar_x.pack(side="bottom", fill="x")
        canvas.pack(side="left", fill="both", expand=True)
        
        # Add content frame to canvas
        canvas.create_window((0, 0), window=self.content_frame, anchor="nw")
        
        # Configure content frame grid
        self.content_frame.grid_columnconfigure(1, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=1)
        
        # Data storage
        self.datasets = {}  # Format: {name: {'df': DataFrame, 'birthdate': 'DD.MM.YYYY'}}
        self.colors = ['red', 'blue', 'green', 'purple', 'orange']
        
        # Create main containers
        self.setup_gui()
        
        # Update scroll region when content changes
        self.content_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        # Add WHO data interpolators
        self.who_interpolators = create_percentile_interpolators()
        
    def setup_gui(self):
        # Create main frames in content_frame instead of root
        self.create_control_frame()
        self.create_plot_frame()
        
    def create_control_frame(self):
        # Change parent to content_frame
        control_frame = ttk.LabelFrame(self.content_frame, text="Controls", padding="10")
        control_frame.grid(row=0, column=0, padx=10, pady=5, sticky="nsew")
        
        # Configure grid weights
        control_frame.grid_columnconfigure(8, weight=1)  # Row before exit button
        
        # File operations
        ttk.Button(control_frame, text="Load Dataset", command=self.load_dataset).grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
        ttk.Button(control_frame, text="Save Dataset", command=self.save_dataset).grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
        ttk.Button(control_frame, text="Clear All", command=self.clear_all).grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
        
        # Add Gender Selection (new)
        ttk.Label(control_frame, text="WHO Standard Gender:").grid(row=3, column=0, padx=5, pady=5)
        self.gender_var = tk.StringVar(value="both")
        gender_combo = ttk.Combobox(control_frame, 
                                  textvariable=self.gender_var,
                                  values=["both", "boys", "girls"],
                                  state="readonly")
        gender_combo.grid(row=3, column=1, padx=5, pady=5, sticky="ew")
        
        # Add Age Calculator section (adjust row numbers)
        ttk.Label(control_frame, text="Age Calculator").grid(row=4, column=0, columnspan=2, pady=(20,5))
        
        self.age_result_var = tk.StringVar()
        self.age_result_var.set("Age: -- years (select a dataset)")
        ttk.Label(control_frame, textvariable=self.age_result_var).grid(row=5, column=0, columnspan=2, padx=5, pady=5)
        
        # Separator
        ttk.Separator(control_frame, orient='horizontal').grid(row=6, column=0, columnspan=2, sticky='ew', pady=10)
        
        # Dataset selection (adjust row numbers)
        ttk.Label(control_frame, text="Active Dataset:").grid(row=7, column=0, padx=5, pady=5)
        self.dataset_combo = ttk.Combobox(control_frame, state='readonly')
        self.dataset_combo.grid(row=7, column=1, padx=5, pady=5, sticky="ew")
        self.dataset_combo.bind('<<ComboboxSelected>>', lambda e: self.update_table_display())
        
        # Birthdate display and edit (adjust row numbers)
        ttk.Label(control_frame, text="Birthdate:").grid(row=8, column=0, padx=5, pady=5)
        self.birthdate_display = ttk.Label(control_frame, text="--")
        self.birthdate_display.grid(row=8, column=1, padx=5, pady=5, sticky="w")
        ttk.Button(control_frame, text="Edit Birthdate", 
                  command=self.edit_birthdate).grid(row=8, column=1, padx=5, pady=5, sticky="e")
        
        # Manual data entry (adjust row numbers)
        ttk.Label(control_frame, text="Add New Data Point").grid(row=9, column=0, columnspan=2, pady=(20,5))
        
        ttk.Label(control_frame, text="Age (years):").grid(row=10, column=0, padx=5, pady=5)
        self.age_display_entry = ttk.Entry(control_frame, state='readonly')
        self.age_display_entry.grid(row=10, column=1, padx=5, pady=5)
        
        ttk.Label(control_frame, text="Height (cm):").grid(row=11, column=0, padx=5, pady=5)
        self.height_entry = ttk.Entry(control_frame)
        self.height_entry.grid(row=11, column=1, padx=5, pady=5)
        
        ttk.Button(control_frame, text="Add Data Point", 
                  command=self.add_data_point).grid(row=12, column=0, columnspan=2, pady=10)
        
        # Data display (adjust row number)
        self.tree = ttk.Treeview(control_frame, columns=("Age", "Height"), show="headings")
        self.tree.heading("Age", text="Age (years)")
        self.tree.heading("Height", text="Height (cm)")
        self.tree.grid(row=13, column=0, columnspan=2, pady=10, sticky="nsew")
        
        # Scrollbar for treeview
        scrollbar = ttk.Scrollbar(control_frame, orient="vertical", command=self.tree.yview)
        scrollbar.grid(row=13, column=2, sticky="ns")
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Create custom style for exit button (before creating the button)
        style = ttk.Style()
        style.configure('Exit.TButton', foreground='red', font=('TkDefaultFont', 10, 'bold'))
        
        # Exit button at bottom left with proper cleanup (same size as Load Dataset button)
        exit_button = ttk.Button(control_frame, text="Exit", 
                                  command=self.quit_app, style='Exit.TButton')
        exit_button.grid(row=14, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
        
    def create_plot_frame(self):
        # Change parent to content_frame
        plot_frame = ttk.LabelFrame(self.content_frame, text="Growth Chart", padding="10")
        plot_frame.grid(row=0, column=1, padx=10, pady=5, sticky="nsew")
        
        # Simplify button frame to just save button
        ttk.Button(plot_frame, text="Save Plot as JPEG", 
                  command=self.save_plot).pack(pady=5)
        
        # Create matplotlib figure
        self.fig, self.ax = plt.subplots(figsize=(12, 8))
        self.canvas = FigureCanvasTkAgg(self.fig, master=plot_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Configure axis formatting
        self.ax.xaxis.set_major_formatter(plt.FormatStrFormatter('%.2f'))
        self.ax.yaxis.set_major_formatter(plt.FormatStrFormatter('%.0f'))
        
        # Add tooltip annotation
        self.annot = self.ax.annotate("", xy=(0,0), xytext=(10,10),
                                     textcoords="offset points",
                                     bbox=dict(boxstyle="round", fc="w", ec="0.5", alpha=0.9),
                                     arrowprops=dict(arrowstyle="->"))
        self.annot.set_visible(False)
        
        # Connect mouse events
        self.canvas.mpl_connect('motion_notify_event', self.on_mouse_move)

    def save_plot(self):
        file_path = filedialog.asksaveasfilename(
            initialdir=self.last_used_directory,
            defaultextension=".jpg",
            filetypes=[("JPEG files", "*.jpg")],
            initialfile="growth_chart.jpg"
        )
        
        if file_path:
            # Update last used directory
            self.last_used_directory = os.path.dirname(file_path)
            
            try:
                self.fig.savefig(file_path, format='jpg', dpi=300, bbox_inches='tight')
                messagebox.showinfo("Success", "Plot saved successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save plot: {str(e)}")

    def on_mouse_move(self, event):
        if event.inaxes is None:
            self.annot.set_visible(False)
            self.canvas.draw_idle()
            return
        
        # Find the closest point
        min_dist = float('inf')
        closest_point = None
        closest_dataset = None
        
        for dataset_name, dataset_info in self.datasets.items():
            df = dataset_info['df']
            for _, row in df.iterrows():
                dist = ((event.xdata - row['Age'])**2 + 
                       (event.ydata - row['Height'])**2)**0.5
                if dist < min_dist:
                    min_dist = dist
                    closest_point = (row['Age'], row['Height'])
                    closest_dataset = dataset_name
        
        if min_dist < 0.5:
            self.annot.xy = closest_point
            
            # Calculate WHO percentiles based on selected gender
            gender = self.gender_var.get()
            percentiles = calculate_exact_percentile(closest_point[0], 
                                                  closest_point[1], 
                                                  self.who_interpolators,
                                                  gender=gender)
            
            # Create tooltip text based on gender selection
            text = [f"Dataset: {closest_dataset}",
                   f"Age: {closest_point[0]:.2f} years",
                   f"Height: {closest_point[1]:.0f} cm",
                   f"WHO Percentiles:"]
            
            if gender == "both":
                text.extend([f"Boys: {percentiles['boys']}th",
                           f"Girls: {percentiles['girls']}th"])
            elif gender == "boys":
                text.append(f"Boys: {percentiles['boys']}th")
            else:  # girls
                text.append(f"Girls: {percentiles['girls']}th")
            
            self.annot.set_text('\n'.join(text))
            self.annot.set_visible(True)
        else:
            self.annot.set_visible(False)
            
        self.canvas.draw_idle()

    def load_dataset(self):
        try:
            # Use last used directory instead of current directory
            file_path = filedialog.askopenfilename(
                initialdir=self.last_used_directory,
                title="Select CSV file",
                filetypes=[("CSV files", "*.csv")]
            )
            
            if file_path:
                # Update last used directory
                self.last_used_directory = os.path.dirname(file_path)
                
                try:
                    # Read CSV with semicolon separator and show content for debugging
                    print(f"Attempting to read file: {file_path}")
                    
                    # First read the file content to handle decimal delimiters
                    with open(file_path, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                    
                    # Check if first line contains birthdate
                    birthdate = None
                    data_start = 0
                    
                    if lines and lines[0].strip().startswith('Birthdate'):
                        # Extract birthdate from first line (format: Birthdate;DD.MM.YYYY)
                        try:
                            parts = lines[0].strip().split(';')
                            if len(parts) >= 2:
                                birthdate = parts[1].strip()
                                # Validate date format
                                datetime.strptime(birthdate, "%d.%m.%Y")
                            data_start = 1
                        except (ValueError, IndexError):
                            # Invalid birthdate format, treat as old format
                            birthdate = None
                            data_start = 0
                    
                    # Join remaining lines for processing
                    content = ''.join(lines[data_start:])
                    
                    # Replace commas with dots in numbers
                    # This regex looks for numbers with commas and replaces the comma with a dot
                    content = re.sub(r'(\d+),(\d+)', r'\1.\2', content)
                    
                    # Convert the modified content to a StringIO object for pandas
                    df = pd.read_csv(StringIO(content), sep=';', encoding='utf-8')
                    
                    print("DataFrame loaded:")
                    print(df.head())
                    
                    # Convert columns to numeric, forcing conversion of string numbers
                    df['Age'] = pd.to_numeric(df['Age'], errors='coerce')
                    df['Height'] = pd.to_numeric(df['Height'], errors='coerce')
                    
                    # Remove any rows with invalid numbers
                    df = df.dropna()
                    
                    # Validate columns
                    required_columns = ['Age', 'Height']
                    if not all(col in df.columns for col in required_columns):
                        messagebox.showerror("Error", 
                            f"CSV file must contain 'Age' and 'Height' columns.\nFound columns: {', '.join(df.columns)}")
                        return
                    
                    # Extract filename without extension as default dataset name
                    default_name = os.path.splitext(os.path.basename(file_path))[0]
                    
                    # Ask for dataset name with default value
                    dataset_name = simpledialog.askstring("Dataset Name", 
                        "Enter a name for this dataset:",
                        initialvalue=default_name,
                        parent=self.root)
                    
                    if dataset_name:
                        if dataset_name in self.datasets:
                            if not messagebox.askyesno("Warning", 
                                f"Dataset '{dataset_name}' already exists. Do you want to replace it?"):
                                return
                        
                        # If no birthdate found, ask user for it
                        if birthdate is None:
                            birthdate = simpledialog.askstring("Birthdate", 
                                f"Enter birthdate for {dataset_name} (DD.MM.YYYY):",
                                parent=self.root)
                            if birthdate:
                                try:
                                    datetime.strptime(birthdate, "%d.%m.%Y")
                                except ValueError:
                                    messagebox.showerror("Error", "Invalid date format. Please use DD.MM.YYYY")
                                    birthdate = None
                        
                        # Store dataset with birthdate
                        self.datasets[dataset_name] = {
                            'df': df,
                            'birthdate': birthdate
                        }
                        self.update_dataset_combo()
                        self.update_display()
                        messagebox.showinfo("Success", f"Dataset '{dataset_name}' loaded successfully with {len(df)} data points")
                        
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to load CSV: {str(e)}\n\nPlease ensure the file:\n"
                                       f"1. Uses semicolons (;) as separators\n"
                                       f"2. Has 'Age' and 'Height' columns\n"
                                       f"3. Contains valid numeric values (using either , or . as decimal separator)")
                    print(f"Error details: {str(e)}")
                    
        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error: {str(e)}")
            print(f"Error details: {str(e)}")
    
    def save_dataset(self):
        dataset_name = self.dataset_combo.get()
        if not dataset_name:
            messagebox.showerror("Error", "Please select a dataset to save")
            return
        
        file_path = filedialog.asksaveasfilename(
            initialdir=self.last_used_directory,
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            initialfile=f"{dataset_name}.csv"
        )
        
        if file_path:
            # Update last used directory
            self.last_used_directory = os.path.dirname(file_path)
            
            try:
                dataset_info = self.datasets[dataset_name]
                df = dataset_info['df']
                birthdate = dataset_info.get('birthdate', None)
                
                # Write birthdate in first row if available
                with open(file_path, 'w', encoding='utf-8') as f:
                    if birthdate:
                        f.write(f"Birthdate;{birthdate}\n")
                    # Write the dataframe
                    df.to_csv(f, sep=';', index=False)
                
                messagebox.showinfo("Success", f"Dataset '{dataset_name}' saved successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save dataset: {str(e)}")
    
    def clear_all(self):
        if messagebox.askyesno("Confirm", "Are you sure you want to clear all datasets?"):
            self.datasets.clear()
            self.birthdate_display.config(text="--")
            self.update_dataset_combo()
            self.update_display()
    
    def edit_birthdate(self):
        """Edit birthdate for the currently selected dataset"""
        dataset_name = self.dataset_combo.get()
        if not dataset_name:
            messagebox.showerror("Error", "Please select a dataset")
            return
        
        dataset_info = self.datasets[dataset_name]
        current_birthdate = dataset_info.get('birthdate', '')
        
        new_birthdate = simpledialog.askstring("Edit Birthdate", 
            f"Enter birthdate for {dataset_name} (DD.MM.YYYY):",
            initialvalue=current_birthdate,
            parent=self.root)
        
        if new_birthdate:
            try:
                # Validate date format
                datetime.strptime(new_birthdate, "%d.%m.%Y")
                dataset_info['birthdate'] = new_birthdate
                # Update display and recalculate age
                self.update_table_display()
            except ValueError:
                messagebox.showerror("Error", "Invalid date format. Please use DD.MM.YYYY")
    
    def add_data_point(self):
        dataset_name = self.dataset_combo.get()
        if not dataset_name:
            messagebox.showerror("Error", "Please select a dataset")
            return
        
        dataset_info = self.datasets[dataset_name]
        birthdate = dataset_info.get('birthdate', None)
        
        if not birthdate:
            messagebox.showerror("Error", "Please set a birthdate for this dataset first")
            return
        
        try:
            # Calculate age automatically from birthdate
            from datetime import datetime
            birth_date = datetime.strptime(birthdate, "%d.%m.%Y")
            current_date = datetime.now()
            age_days = (current_date - birth_date).days
            age = age_days / 365.25  # Account for leap years
            
            # Get height from user input
            height = float(self.height_entry.get())
            
            new_data = pd.DataFrame({'Age': [age], 'Height': [height]})
            dataset_info['df'] = pd.concat([dataset_info['df'], new_data], 
                                          ignore_index=True)
            
            # Clear only height entry (age is auto-calculated)
            self.height_entry.delete(0, tk.END)
            
            self.update_display()
            
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid height value")
    
    def update_dataset_combo(self):
        current = self.dataset_combo.get()
        self.dataset_combo['values'] = list(self.datasets.keys())
        if current in self.datasets:
            self.dataset_combo.set(current)
        elif self.datasets:
            self.dataset_combo.set(list(self.datasets.keys())[0])
    
    def update_table_display(self):
        """Update only the table view based on selected dataset"""
        # Clear existing items
        self.tree.delete(*self.tree.get_children())
        
        # Get selected dataset
        dataset_name = self.dataset_combo.get()
        if dataset_name and dataset_name in self.datasets:
            dataset_info = self.datasets[dataset_name]
            df = dataset_info['df']
            birthdate = dataset_info.get('birthdate', None)
            
            # Update birthdate display
            if birthdate:
                self.birthdate_display.config(text=birthdate)
            else:
                self.birthdate_display.config(text="Not set")
            
            # Automatically calculate and update age
            self.calculate_age()
            
            # Sort by age before displaying
            df_sorted = df.sort_values('Age')
            for _, row in df_sorted.iterrows():
                self.tree.insert("", "end", values=(f"{row['Age']:.2f}", f"{row['Height']:.0f}"))

    def update_display(self):
        # Update table
        self.update_table_display()
        
        # Update plot
        self.ax.clear()
        
        # Plot each dataset with different colors
        for i, (name, dataset_info) in enumerate(self.datasets.items()):
            df = dataset_info['df']
            color = self.colors[i % len(self.colors)]
            
            # Plot scatter points
            self.ax.scatter(df['Age'], df['Height'], color=color, label=name)
            
            # Sort by age for line plot
            df_sorted = df.sort_values('Age')
            
            # Plot connecting line
            self.ax.plot(df_sorted['Age'], df_sorted['Height'], 
                        color=color, alpha=0.5)
        
        self.ax.set_xlabel("Age (years)")
        self.ax.set_ylabel("Height (cm)")
        self.ax.set_title("Child Growth Chart")
        self.ax.grid(True)
        self.ax.legend()
        
        # Format axis
        self.ax.xaxis.set_major_formatter(plt.FormatStrFormatter('%.2f'))
        self.ax.yaxis.set_major_formatter(plt.FormatStrFormatter('%.0f'))
        
        # Recreate the annotation after clearing the plot
        self.annot = self.ax.annotate("", xy=(0,0), xytext=(10,10),
                                     textcoords="offset points",
                                     bbox=dict(boxstyle="round", fc="w", ec="0.5", alpha=0.9),
                                     arrowprops=dict(arrowstyle="->"))
        self.annot.set_visible(False)
        
        self.canvas.draw()

    def calculate_age(self):
        """Calculate age automatically from the selected dataset's birthdate"""
        dataset_name = self.dataset_combo.get()
        if not dataset_name or dataset_name not in self.datasets:
            self.age_result_var.set("Age: -- years (select a dataset)")
            self.age_display_entry.config(state='normal')
            self.age_display_entry.delete(0, tk.END)
            self.age_display_entry.insert(0, "--")
            self.age_display_entry.config(state='readonly')
            return
        
        dataset_info = self.datasets[dataset_name]
        birthdate = dataset_info.get('birthdate', None)
        
        if not birthdate:
            self.age_result_var.set("Age: -- years (birthdate not set)")
            self.age_display_entry.config(state='normal')
            self.age_display_entry.delete(0, tk.END)
            self.age_display_entry.insert(0, "--")
            self.age_display_entry.config(state='readonly')
            return
        
        try:
            from datetime import datetime
            
            # Parse birthdate
            birth_date = datetime.strptime(birthdate, "%d.%m.%Y")
            # Use current date
            current_date = datetime.now()
            
            # Calculate age
            age_days = (current_date - birth_date).days
            age_years = age_days / 365.25  # Account for leap years
            
            # Update result with 2 decimal places
            self.age_result_var.set(f"Age: {age_years:.2f} years")
            
            # Update age display entry
            self.age_display_entry.config(state='normal')
            self.age_display_entry.delete(0, tk.END)
            self.age_display_entry.insert(0, f"{age_years:.2f}")
            self.age_display_entry.config(state='readonly')
            
        except ValueError as e:
            self.age_result_var.set("Age: -- years (invalid birthdate format)")
            self.age_display_entry.config(state='normal')
            self.age_display_entry.delete(0, tk.END)
            self.age_display_entry.insert(0, "--")
            self.age_display_entry.config(state='readonly')

    def quit_app(self):
        """Properly close the application"""
        try:
            # Close matplotlib figure to prevent memory leaks
            plt.close(self.fig)
            
            # Destroy the main window
            self.root.quit()
            self.root.destroy()
            
        except Exception as e:
            print(f"Error during cleanup: {e}")
            # Force quit if normal cleanup fails
            self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = ChildGrowthAnalyzer(root)
    root.mainloop() 