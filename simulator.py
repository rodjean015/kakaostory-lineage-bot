import datetime
import sys
from tkinter import DISABLED, messagebox
from functions import arduino as ards
import ttkbootstrap as tb

class ArduinoPort:
    def __init__(self, root):

        # Port frame
        self.port_frame = tb.LabelFrame(root, padding=7, text="Available COM Ports")
        self.port_frame.grid(row=0, column=0, sticky="nsew", padx=10)

        # Make the frame responsive
        for col in range(6):
            self.port_frame.grid_columnconfigure(col, weight=1)

        # List available COM ports
        self.ports_list = ards.list_ports()
        self.com_entry = tb.Combobox(self.port_frame, values=self.ports_list, width=10, state="readonly")
        self.com_entry.grid(row=0, column=0, sticky="ew", padx=5)

        # Define buttons and their properties in a list
        buttons = {
            "connect_button": {"text": "Connect", "command": self.select_port, "grid": (0, 1), "bootstyle": None, "hidden": False},
            "disconnect_button": {"text": "Disconnect", "command": self.disconnect, "grid": (0, 1), "bootstyle": "danger", "hidden": True},
            "upload_button": {"text": "Upload", "command": ards.upload_code, "grid": (0, 2), "state": DISABLED},
        }

        # Create buttons and assign them as instance variables
        for name, btn in buttons.items():
            button = tb.Button(
                self.port_frame, text=btn["text"], command=btn["command"],
                width=14, bootstyle=btn.get("bootstyle"), state=btn.get("state", "normal")
            )
            button.grid(row=btn["grid"][0], column=btn["grid"][1], padx=5, pady=5, sticky="ew")
            if btn.get("hidden"):
                button.grid_remove()
            setattr(self, name, button)  # Assign button to an instance variable with the name

    def select_port(self):
        selected_port = self.com_entry.get().strip()
        if not selected_port:
            print("COM port not found. Please try again.")
            messagebox.showerror("Error", "COM port not found. Please try again.")
        else:
            if ards.init_serial(selected_port):
                messagebox.showinfo("Info", f"Connected to {selected_port}.")
                self.connect_button.grid_remove()
                self.disconnect_button.grid()
                self.upload_button['state'] = 'normal'
            else:
                print(f"Failed to connect to {selected_port}. Please check the connection.")
                messagebox.showerror("Error", f"Failed to connect to {selected_port}. Please check the connection.")

    def disconnect(self):
        if messagebox.askokcancel("Warning", "Are you sure you want to disconnect?"):
            ards.close_serial()
            self.disconnect_button.grid_remove()
            self.connect_button.grid()
            self.upload_button['state'] = DISABLED

class Command:
    def __init__(self, root):
        self.command_frame = tb.LabelFrame(root, padding=7, text="Command Button")
        self.command_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)

        self.command_frame.grid_columnconfigure(0, weight=1)         

        # Create buttons and assign them as instance variables
        buttons = {
            "enter_game": {"text": "Enter Game", "command": lambda: self.execute_command('enter_game', "Enter Game executed successfully."), "grid": (0, 0), "bootstyle": None},
            "enter_sched": {"text": "Enter Schedule", "command": lambda: self.execute_command('enter_sched', "Enter Schedule executed successfully."), "grid": (1, 0), "bootstyle": None},
            "set_sched": {"text": "Set Schedule", "command": lambda: self.execute_command('set_sched', "Set Schedule executed successfully."), "grid": (2, 0), "bootstyle": None},
            "enter_psm": {"text": "Enter Power Saving", "command": lambda: self.execute_command('enter_psm', "Enter Power Saving executed successfully."), "grid": (3, 0), "bootstyle": None},
            "click_psm": {"text": "Click Power Saving", "command": lambda: self.execute_command('click_psm', "Click Power Saving executed successfully."), "grid": (4, 0), "bootstyle": None},
            "click_penalty": {"text": "Click Penalty", "command": lambda: self.execute_command('click_penalty', "Click Penalty executed successfully."), "grid": (5, 0), "bootstyle": None},
        }

        for name, btn in buttons.items():
            button = tb.Button(
                self.command_frame, text=btn["text"], command=btn["command"], 
                bootstyle=btn.get("bootstyle"), state=btn.get("state", "normal")
            )
            button.grid(row=btn["grid"][0], column=btn["grid"][1], padx=5, pady=5, sticky="ew")
            setattr(self, name, button)  # Assign button to an instance variable with the name

    def execute_command(self, command, prompt_message):
        # Show confirmation message box first
        if messagebox.askokcancel("Confirmation", prompt_message):
            # Execute the command only if the user clicks OK
            ards.send_command(command)

class ConsoleLog:
    def __init__(self, root, log_file=None):
        # Format the current time for the log file name
        formatted_now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = log_file if log_file else f"logs/log{formatted_now}.txt"

        # Create the console frame
        console_frame = tb.LabelFrame(root, text="Console", padding=10)
        console_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=5)

        # Make the frame responsive
        console_frame.grid_rowconfigure(0, weight=1)
        console_frame.grid_columnconfigure(0, weight=1)

        # Create a ScrolledText widget for the console log
        self.console = tb.Text(console_frame, wrap="word")
        self.console.grid(row=0, column=0, sticky="nsew")

        # Add scrollbar to the Text widget
        scrollbar = tb.Scrollbar(console_frame, command=self.console.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.console.config(yscrollcommand=scrollbar.set)

    def write(self, message):
        if message.strip():  # Avoid logging empty messages
            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.console.insert(tb.END, f"[{current_time}] {message}\n")
            self.console.see(tb.END)  # Scroll to the end

    def flush(self):
        pass  # Needed for Python's file-like objects, especially when redirecting stdout

    def save_to_file(self):
        try:
            # Save the console log content to the log file
            with open(self.log_file, "w") as file:
                file.write(self.console.get("1.0", tb.END))  # Get all text from the start to the end
            print("Success: Logs saved successfully!")
        except Exception as e:
            print(f"Error: Failed to save logs: {e}")

class App:
    def __init__(self, root):
        root.title("Lineage II")
        root.iconbitmap("assets/excel.ico")  # Replace with your default icon file
        root.minsize(400, 500)    # Set minimum size to prevent the window from getting too small
        root.maxsize(400, 500)

        # Make the root window responsive
        root.grid_columnconfigure(0, weight=1)
        root.grid_rowconfigure(2, weight=1)

if __name__ == "__main__":
    # Create the ttkbootstrap-themed window
    root = tb.Window(themename="darkly")
    arduino = ArduinoPort(root)
    btn = Command(root)
    logs = ConsoleLog(root)
    sys.stdout =logs
    app = App(root)
    root.mainloop()
