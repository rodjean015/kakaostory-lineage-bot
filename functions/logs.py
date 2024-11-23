import datetime
import ttkbootstrap as tb

class ConsoleLog:
    def __init__(self, root, app, log_file=None):
        # Format the current time for the log file name
        formatted_now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = log_file if log_file else f"logs/log{formatted_now}.txt"

        # Create the console frame
        console_frame = tb.LabelFrame(root, text="Console Logs", padding=10)
        console_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=5)

        # Make the frame responsive
        console_frame.grid_rowconfigure(0, weight=1)
        console_frame.grid_columnconfigure(0, weight=1)

        # Create a ScrolledText widget for the console log
        self.console = tb.Text(console_frame, wrap="word")
        self.console.grid(row=0, column=0, sticky="nsew")

        # Add scrollbar to the Text widget
        scrollbar = tb.Scrollbar(console_frame, command=self.console.yview)
        scrollbar.grid(row=0, column=0, sticky="nse")
        self.console.config(yscrollcommand=scrollbar.set)

        self.stop_button = tb.Button(console_frame, padding = 5, text="Stop", bootstyle="danger", command=app.stop_automation)
        self.stop_button.grid(row=0, column=1, sticky="nsew", pady=5)
        self.stop_button.grid_remove()

    def flush(self):
        pass  # Needed for Python's file-like objects, especially when redirecting stdout

    def write(self, message):
        if message.strip():  # Avoid logging empty messages
            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.console.insert(tb.END, f"[{current_time}] {message}\n")
            self.console.see(tb.END)  # Scroll to the end

    def save_to_file(self):
        try:
            # Save the console log content to the log file
            with open(self.log_file, "w") as file:
                file.write(self.console.get("1.0", tb.END))  # Get all text from the start to the end
            print("Success: Logs saved successfully!")
        except Exception as e:
            print(f"Error: Failed to save logs: {e}")
        pass