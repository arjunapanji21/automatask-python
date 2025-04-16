import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext
import json
from web_automation import WebAutomator
from excel_handler import ExcelHandler
from config_manager import ConfigManager

class AutomataskGUI:
    VERSION = "1.0.0"
    AUTHOR = "Arjuna Panji Prakarsa"
    WEBSITE = "https://arjunaprakarsa.com"

    def __init__(self):
        self.root = tk.Tk()
        self.root.title(f"Automatask v{self.VERSION}")
        self.root.geometry("1024x800")  # Wider window
        self.root.resizable(True, True)
        
        self.config_manager = ConfigManager()
        
        self.stop_flag = False
        self.automation_running = False
        self.paused = False
        
        # Create main scrollable frame
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.create_widgets()
        self.create_status_bar()
        self.add_tooltips()
    
    def create_widgets(self):
        # Add version and author info at top
        info_frame = ttk.Frame(self.main_frame)
        info_frame.pack(fill="x", pady=(0, 10))
        
        version_label = ttk.Label(
            info_frame, 
            text=f"Automatask v{self.VERSION} | By {self.AUTHOR}", 
            font=("Segoe UI", 9, "bold")
        )
        version_label.pack(side="left")
        
        website_label = ttk.Label(
            info_frame, 
            text=self.WEBSITE,
            foreground="blue",
            cursor="hand2",
            font=("Segoe UI", 9, "underline")
        )
        website_label.pack(side="right")
        website_label.bind("<Button-1>", lambda e: self.open_website())

        # Basic Settings Frame
        basic_frame = ttk.LabelFrame(self.main_frame, text="Basic Settings")
        basic_frame.pack(fill="x", pady=(0, 10))
        
        # URL entries in grid layout - side by side
        url_frame = ttk.Frame(basic_frame)
        url_frame.pack(fill="x", padx=5, pady=5)
        
        # Login URL - Left side
        login_frame = ttk.Frame(url_frame)
        login_frame.pack(side="left", fill="x", expand=True, padx=(0, 5))
        ttk.Label(login_frame, text="Login URL:").pack(side="left")
        self.url_entry = ttk.Entry(login_frame)
        self.url_entry.pack(side="left", fill="x", expand=True, padx=5)
        
        # Form URL - Right side
        form_frame = ttk.Frame(url_frame)
        form_frame.pack(side="left", fill="x", expand=True, padx=(5, 0))
        ttk.Label(form_frame, text="Form URL:").pack(side="left")
        self.form_url_entry = ttk.Entry(form_frame)
        self.form_url_entry.pack(side="left", fill="x", expand=True, padx=5)

        # Credentials and Excel file in one row
        cred_file_frame = ttk.Frame(basic_frame)
        cred_file_frame.pack(fill="x", padx=5, pady=5)
        
        # Credentials - Left side
        cred_frame = ttk.Frame(cred_file_frame)
        cred_frame.pack(side="left", fill="x", expand=True, padx=(0, 5))
        ttk.Label(cred_frame, text="Username:").pack(side="left", padx=(0, 2))
        self.username_entry = ttk.Entry(cred_frame, width=20)
        self.username_entry.pack(side="left", padx=(0, 5))
        ttk.Label(cred_frame, text="Password:").pack(side="left", padx=(5, 2))
        self.password_entry = ttk.Entry(cred_frame, show="*", width=20)
        self.password_entry.pack(side="left")
        
        # Excel File - Right side
        file_frame = ttk.Frame(cred_file_frame)
        file_frame.pack(side="left", fill="x", expand=True, padx=(5, 0))
        ttk.Label(file_frame, text="Excel File:").pack(side="left")
        self.file_path = tk.StringVar()
        ttk.Label(file_frame, textvariable=self.file_path, width=30).pack(side="left", padx=5)
        ttk.Button(file_frame, text="Browse", command=self.select_file).pack(side="left")

        # Create container frame for side by side layout
        container_frame = ttk.Frame(self.main_frame)
        container_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        # Field Mapping Frame with Scrollbar - Left side
        mapping_frame = ttk.LabelFrame(container_frame, text="Field Mapping")
        mapping_frame.pack(fill="both", expand=True, side="left", padx=(0, 5))
        
        # Mapping controls
        control_frame = ttk.Frame(mapping_frame)
        control_frame.pack(fill="x", padx=5, pady=5)
        ttk.Button(control_frame, text="Add Field", command=self.add_field_mapping).pack(side="left", padx=5)
        ttk.Button(control_frame, text="Remove Selected", command=self.remove_selected_mapping).pack(side="left")
        
        # Mapping list with headers and bindings
        self.mapping_tree = ttk.Treeview(mapping_frame, columns=("Excel Column", "Selector Type", "Web Selector"), show="headings")
        self.mapping_tree.heading("Excel Column", text="Excel Column")
        self.mapping_tree.heading("Selector Type", text="Selector Type")
        self.mapping_tree.heading("Web Selector", text="Web Selector")
        
        # Update tree column widths for side by side layout
        self.mapping_tree.column("Excel Column", width=150)
        self.mapping_tree.column("Selector Type", width=100)
        self.mapping_tree.column("Web Selector", width=200)
        self.mapping_tree.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Bind double-click event
        self.mapping_tree.bind('<Double-1>', self.edit_field_mapping)
        
        # Add Post-Submit Actions Frame - Right side
        actions_frame = ttk.LabelFrame(container_frame, text="Post-Submit Actions")
        actions_frame.pack(fill="both", expand=True, side="left", padx=(5, 0))
        
        # Actions controls
        action_control_frame = ttk.Frame(actions_frame)
        action_control_frame.pack(fill="x", padx=5, pady=5)
        ttk.Button(action_control_frame, text="Add Action", command=self.add_action).pack(side="left", padx=5)
        ttk.Button(action_control_frame, text="Remove Selected", command=self.remove_selected_action).pack(side="left")
        
        # Actions list with headers
        self.actions_tree = ttk.Treeview(actions_frame, columns=("Order", "Action Type", "Selector Type", "Selector", "Delay"), show="headings")
        self.actions_tree.heading("Order", text="#")
        self.actions_tree.heading("Action Type", text="Action")
        self.actions_tree.heading("Selector Type", text="Selector Type")
        self.actions_tree.heading("Selector", text="Selector")
        self.actions_tree.heading("Delay", text="Delay(s)")
        
        # Update action tree column widths for side by side layout
        self.actions_tree.column("Order", width=40)
        self.actions_tree.column("Action Type", width=100)
        self.actions_tree.column("Selector Type", width=100)
        self.actions_tree.column("Selector", width=200)
        self.actions_tree.column("Delay", width=60)
        self.actions_tree.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Bind double-click event for actions
        self.actions_tree.bind('<Double-1>', self.edit_action)
        
        # Control buttons at bottom
        btn_frame = ttk.Frame(self.main_frame)
        btn_frame.pack(fill="x", pady=10)
        
        # Left side buttons
        ttk.Button(btn_frame, text="Load Config", command=self.load_config).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Save Config", command=self.save_config).pack(side="left")
        
        # Right side buttons
        self.start_button = ttk.Button(btn_frame, text="Start Automation", command=self.start_automation)
        self.start_button.pack(side="right", padx=5)
        self.pause_button = ttk.Button(btn_frame, text="Pause", command=self.pause_automation, state="disabled")
        self.pause_button.pack(side="right", padx=5)
        self.stop_button = ttk.Button(btn_frame, text="Stop", command=self.stop_automation, state="disabled")
        self.stop_button.pack(side="right", padx=5)
        
        # Progress bar
        self.progress = ttk.Progressbar(self.main_frame, mode='determinate')
        self.progress.pack(fill="x", pady=(0, 5))
        
        # Status text area
        self.status_text = scrolledtext.ScrolledText(self.main_frame, height=5)
        self.status_text.pack(fill="x")
    
    def create_status_bar(self):
        status_frame = ttk.Frame(self.root)
        status_frame.pack(fill="x", side="bottom", pady=(5,0))
        
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        self.status_bar = ttk.Label(
            status_frame, 
            textvariable=self.status_var,
            relief="sunken",
            padding=(5,2)
        )
        self.status_bar.pack(fill="x", side="left", expand=True)
        
        version_label = ttk.Label(
            status_frame,
            text=f"v{self.VERSION}",
            relief="sunken",
            padding=(5,2)
        )
        version_label.pack(side="right", padx=(5,0))
    
    def add_tooltips(self):
        self.create_tooltip(self.url_entry, "Enter the website login URL")
        self.create_tooltip(self.form_url_entry, "Enter the URL of the form page after login")
        self.create_tooltip(self.username_entry, "Enter your login username")
        self.create_tooltip(self.password_entry, "Enter your login password")
        self.create_tooltip(self.mapping_tree, "Map Excel columns to web page elements")
    
    def create_tooltip(self, widget, text):
        def show_tooltip(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            
            label = ttk.Label(tooltip, text=text, background="#ffffe0", relief="solid", borderwidth=1)
            label.pack()
            
            def hide_tooltip():
                tooltip.destroy()
            
            widget.bind('<Leave>', lambda e: hide_tooltip())
            tooltip.bind('<Leave>', lambda e: hide_tooltip())
        
        widget.bind('<Enter>', show_tooltip)
    
    def add_field_mapping(self):
        self.mapping_tree.insert("", "end", values=("New Column", "CSS", "CSS Selector"))
    
    def remove_selected_mapping(self):
        selected = self.mapping_tree.selection()
        for item in selected:
            self.mapping_tree.delete(item)
    
    def edit_field_mapping(self, event):
        # Get the item and column that was clicked
        item_id = self.mapping_tree.selection()[0]
        column = self.mapping_tree.identify_column(event.x)
        column_id = int(column[1]) - 1  # Convert column identifier to index
        
        # Get current value
        current_values = self.mapping_tree.item(item_id)['values']
        
        # Create editing popup
        edit_window = tk.Toplevel(self.root)
        edit_window.title("Edit Mapping")
        edit_window.geometry("300x100")
        
        # Center popup
        edit_window.geometry(f"+{self.root.winfo_x() + 150}+{self.root.winfo_y() + 150}")
        
        # Add entry field
        ttk.Label(edit_window, text="Enter new value:").pack(pady=5)
        entry = ttk.Entry(edit_window, width=40)
        entry.insert(0, current_values[column_id])
        entry.pack(pady=5)
        
        # Add selector type dropdown if editing selector type column
        if column_id == 1:  # Selector Type column
            entry.destroy()  # Remove the entry widget
            selector_type = ttk.Combobox(edit_window, values=["CSS", "ID", "XPATH"], state="readonly")
            selector_type.set(current_values[column_id])
            selector_type.pack(pady=5)
            entry = selector_type
        
        entry.select_range(0, tk.END)
        entry.focus()
        
        def save_changes():
            # Update the value in the tree
            new_values = list(current_values)
            new_values[column_id] = entry.get()
            self.mapping_tree.item(item_id, values=new_values)
            edit_window.destroy()
        
        # Add save button
        ttk.Button(edit_window, text="Save", command=save_changes).pack(pady=5)
        
        # Handle Enter key
        entry.bind('<Return>', lambda e: save_changes())
        
        # Make window modal
        edit_window.transient(self.root)
        edit_window.grab_set()
        self.root.wait_window(edit_window)
    
    def add_action(self):
        next_order = len(self.actions_tree.get_children()) + 1
        self.actions_tree.insert("", "end", values=(next_order, "click", "CSS", "button[type='submit']", "1"))

    def remove_selected_action(self):
        selected = self.actions_tree.selection()
        for item in selected:
            self.actions_tree.delete(item)
        self.reorder_actions()

    def reorder_actions(self):
        items = self.actions_tree.get_children()
        for i, item in enumerate(items, 1):
            values = list(self.actions_tree.item(item)['values'])
            values[0] = i
            self.actions_tree.item(item, values=values)

    def edit_action(self, event):
        item_id = self.actions_tree.selection()[0]
        column = self.actions_tree.identify_column(event.x)
        column_id = int(column[1]) - 1
        
        current_values = self.actions_tree.item(item_id)['values']
        
        edit_window = tk.Toplevel(self.root)
        edit_window.title("Edit Action")
        edit_window.geometry("300x150")
        edit_window.geometry(f"+{self.root.winfo_x() + 150}+{self.root.winfo_y() + 150}")
        
        if column_id == 1:  # Action Type
            combo = ttk.Combobox(edit_window, values=["click", "input", "wait"], state="readonly")
            combo.set(current_values[column_id])
            combo.pack(pady=5)
            entry = combo
        elif column_id == 2:  # Selector Type
            combo = ttk.Combobox(edit_window, values=["CSS", "ID", "XPATH"], state="readonly")
            combo.set(current_values[column_id])
            combo.pack(pady=5)
            entry = combo
        else:
            entry = ttk.Entry(edit_window, width=40)
            entry.insert(0, current_values[column_id])
            entry.pack(pady=5)
        
        def save_changes():
            new_values = list(current_values)
            new_values[column_id] = entry.get()
            self.actions_tree.item(item_id, values=new_values)
            edit_window.destroy()
        
        ttk.Button(edit_window, text="Save", command=save_changes).pack(pady=5)
        entry.bind('<Return>', lambda e: save_changes())
        
        edit_window.transient(self.root)
        edit_window.grab_set()
    
    def select_file(self):
        filename = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx *.xls")])
        if filename:
            self.file_path.set(filename)
    
    def save_config(self):
        # Get mapping values directly from the Treeview items
        mappings = []
        for item_id in self.mapping_tree.get_children():
            values = self.mapping_tree.item(item_id)['values']
            mappings.append({
                "excel_column": values[0],
                "selector_type": values[1],
                "web_selector": values[2]
            })
            
        # Get post-submit actions
        actions = []
        for item_id in self.actions_tree.get_children():
            values = self.actions_tree.item(item_id)['values']
            actions.append({
                "order": values[0],
                "action": values[1],
                "selector_type": values[2],
                "selector": values[3],
                "delay": float(values[4])
            })
        
        config = {
            "url": self.url_entry.get(),
            "form_url": self.form_url_entry.get(),
            "username": self.username_entry.get(),
            "password": self.password_entry.get(),
            "field_mappings": mappings,
            "excel_file": self.file_path.get(),
            "post_submit_actions": actions
        }
        self.config_manager.save_config(config)
        self.update_status("Configuration saved successfully.")
    
    def load_config(self):
        config = self.config_manager.load_config()
        if config:
            self.config_manager.apply_config(self, config)
            self.update_status("Configuration loaded successfully.")
    
    def start_automation(self):
        self.stop_flag = False
        self.automation_running = True
        self.start_button.configure(state="disabled")
        self.pause_button.configure(state="normal")
        self.stop_button.configure(state="normal")
        
        # Get mapping values directly from the Treeview items
        mappings = []
        for item_id in self.mapping_tree.get_children():
            values = self.mapping_tree.item(item_id)['values']
            mappings.append({
                "excel_column": values[0],
                "selector_type": values[1],
                "web_selector": values[2]
            })
            
        # Get post-submit actions
        actions = []
        for item_id in self.actions_tree.get_children():
            values = self.actions_tree.item(item_id)['values']
            actions.append({
                "order": values[0],
                "action": values[1],
                "selector_type": values[2],
                "selector": values[3],
                "delay": float(values[4])
            })
        
        config = {
            "url": self.url_entry.get(),
            "form_url": self.form_url_entry.get(),
            "username": self.username_entry.get(),
            "password": self.password_entry.get(),
            "field_mappings": mappings,
            "excel_file": self.file_path.get(),
            "post_submit_actions": actions
        }
        
        excel_handler = ExcelHandler(self.file_path.get())
        web_automator = WebAutomator(config, self)  # Pass 'self' as gui parameter
        self.update_status("Automation started.")
        web_automator.run_automation(excel_handler.get_data())
        
        self.automation_running = False
        self.start_button.configure(state="normal")
        self.pause_button.configure(state="disabled")
        self.stop_button.configure(state="disabled")
        self.update_status("Automation completed.")
    
    def pause_automation(self):
        if self.automation_running:
            self.paused = not self.paused
            status = "paused" if self.paused else "resumed"
            self.pause_button.configure(text="Resume" if self.paused else "Pause")
            self.update_status(f"Automation {status}")

    def stop_automation(self):
        if self.automation_running:
            self.stop_flag = True
            self.update_status("Stopping automation...")
    
    def update_status(self, message):
        self.status_var.set(message)
        self.status_text.insert("end", f"{message}\n")
        self.status_text.see("end")
        self.root.update()

    def open_website(self):
        import webbrowser
        webbrowser.open(self.WEBSITE)

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = AutomataskGUI()
    app.run()
