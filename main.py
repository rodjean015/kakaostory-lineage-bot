import ctypes
import datetime
import json
import os
import random
import sys
import threading
import time
import cv2
import numpy as np
import pyautogui
import ttkbootstrap as tb
from tkinter import messagebox, DISABLED
import pygetwindow as gw
from functions import arduino as ards
from functions import logs as lg

class ArduinoPort:
    def __init__(self, root, app):
        # Port frame
        arduino_sketch = "arduino/arduino/arduino.ino"
        self.port_frame = tb.LabelFrame(root, padding=7, text="Available COM Ports")
        self.port_frame.grid(row=0, column=0, sticky="nsew", padx=10)

        # Make the frame responsive
        for col in range(4):
            self.port_frame.grid_columnconfigure(col, weight=1)

        # List available COM ports
        self.ports_list = ards.list_ports()
        self.com_entry = tb.Combobox(self.port_frame, values=self.ports_list, width=3, state="readonly")
        self.com_entry.grid(row=0, column=0, sticky="ew", padx=5)

        # Define buttons and their properties in a list
        buttons = {
            "connect_button": {"text": "Connect", "command": self.select_port, "grid": (0, 1), "bootstyle": None, "hidden": False},
            "disconnect_button": {"text": "Disconnect", "command": self.disconnect, "grid": (0, 1), "bootstyle": "danger", "hidden": True},
            "upload_button": {
                "text": "Upload",
                "command": lambda: ards.upload_sketch(arduino_sketch, self.com_entry.get()),  # Get the selected port from the combobox
                "grid": (0, 2),
                "state": DISABLED,  # Initially disabled
            },
            "start_button": {"text": "Start", "command": app.start_automation, "grid": (0, 3), "bootstyle": "success"},
        }

        # Create buttons and assign them as instance variables
        for name, btn in buttons.items():
            button = tb.Button(
                self.port_frame, text=btn["text"], command=btn["command"],
                bootstyle=btn.get("bootstyle"), state=btn.get("state", "normal")
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

class CharacterConfig:
    def __init__(self, root):
        self.setup_frame = tb.LabelFrame(root, padding=7, text="Characters Setup")
        self.setup_frame.grid(row=1, column=0, sticky="nsew", padx=10)
        
        self.setup_frame.grid_columnconfigure(0, weight=1)
        
        # List to hold Combobox widgets for easy access and updating
        self.character_comboboxes = []

        setup_section = tb.Frame(self.setup_frame)
        setup_section.grid(row=0, column=0, sticky="news")

        for col in range(3):
            setup_section.grid_columnconfigure(col, weight=1)

        for row in range(3):
            setup_section.grid_rowconfigure(row, weight=1)
        
        # Initialize frames and create Comboboxes in 3 columns
        for i in range(3):  # Three main columns
            frame_section = tb.Frame(setup_section, padding=5)
            frame_section.grid(row=0, column=i, sticky="news", padx=5, pady=5)

            for j in range(6):  # Six characters per column
                char_num = i * 6 + j + 1
                
                # Frame for each character
                frame = tb.Frame(frame_section)
                frame.grid(row=j, column=0, sticky="news", pady=5)

                # Label for character title
                label_title = tb.Label(frame, text=f"Character {char_num}")
                label_title.grid(row=0, column=0, sticky="news")
                
                # Combobox for character selection
                character_name = tb.Combobox(frame, state="normal")
                character_name.grid(row=1, column=0, sticky="news")
                character_name.bind("<KeyRelease>", self.on_combobox_search)
                character_name.bind("<<ComboboxSelected>>", self.on_combobox_selected)
                self.character_comboboxes.append(character_name)

        button_section = tb.Frame(self.setup_frame, padding=5)
        button_section.grid(row=1, column=0, sticky="news")

        for col in range(3):
            button_section.grid_columnconfigure(col, weight=1)

        # Define buttons and their properties in a list
        buttons = {
            "refresh_btn": {"text": "Refresh", "command": self.refresh_window_list, "grid": (0, 0)},
            "edit_btn": {"text": "Edit", "command": self.enable_comboboxes, "grid": (0, 1), "bootstyle": "danger", "hidden": True},
            "save_btn": {"text": "Save", "command": self.disable_comboboxes, "grid": (0, 1)},
            "resize_btn": {"text": "Resize", "command": self.position_windows, "grid": (0, 2)},
        }

        # Create buttons and assign them as instance variables
        for name, btn in buttons.items():
            button = tb.Button(
                button_section, text=btn["text"], command=btn["command"], 
                bootstyle=btn.get("bootstyle"), state=btn.get("state", "normal")
            )
            button.grid(row=btn["grid"][0], column=btn["grid"][1], padx=5, pady=5, sticky="ew")
            if btn.get("hidden"):
                button.grid_remove()
            setattr(self, name, button)  # Assign button to an instance variable with the name

        self.refresh_window_list()  # Populate Comboboxes initially
        self.load_combobox_data()
        self.character_timer = None
        self.game_timer = None
    
    def on_combobox_search(self, event):
        combobox = event.widget
        search_text = combobox.get().lower()

        # Get window titles containing "lineage2m" (case insensitive)
        available_windows = [win for win in gw.getAllTitles() if "lineage2m" in win.strip().lower()]
        filtered_values = [item for item in available_windows if search_text in item.lower()]

        # Update combobox values dynamically
        combobox['values'] = filtered_values

        # Retain user input while updating and expand dropdown
        combobox.set(search_text)
        combobox.update()
        combobox.event_generate('<Button-1>')

    def refresh_window_list(self):
        """Refresh the dropdown values for all Comboboxes with the list of active windows containing '2m'."""
        windows = gw.getAllTitles()
        # Filter to include only windows containing 'lineage2m' in the title, case-insensitive
        windows = [win for win in windows if "2m" in win.strip().lower()]
        
        # Update each Combobox with the filtered windows
        self.update_comboboxes(windows)

        for combobox in self.character_comboboxes:
            combobox.set('')            # Clear the current selection

    def update_comboboxes(self, available_windows):
        """Update each Combobox with available windows excluding selected ones."""
        selected_windows = {cb.get() for cb in self.character_comboboxes if cb.get()}  # Set of currently selected windows
        
        for combobox in self.character_comboboxes:
            current_selection = combobox.get()
            
            # Filter the list to exclude selected windows, but include the current selection
            filtered_windows = [win for win in available_windows if win not in selected_windows or win == current_selection]
            
            combobox['values'] = filtered_windows  # Update values
            if current_selection:  # Retain current selection if present
                combobox.set(current_selection)
            else:
                combobox.set('')  # Clear selection if empty

    def on_combobox_selected(self, event):
        """Handle selection event for each Combobox to update available options."""
        available_windows = [win for win in gw.getAllTitles() if "lineage2m" in win.strip().lower()]
        self.update_comboboxes(available_windows) # Refresh all Comboboxes based on the updated selections
        combobox = event.widget
        selected_text = combobox.get()
        print(f"Selected: {selected_text}")

    def resize_random_window(self):
        """Resize and activate a random window from the comboboxes without repeating titles."""
        self.resized_windows = getattr(self, "resized_windows", set())
        self.previous_window = getattr(self, "previous_window", None)

        # Get windows not yet resized
        window_titles = [cb.get() for cb in self.character_comboboxes if cb.get()]
        remaining_titles = [title for title in window_titles if title not in self.resized_windows]

        if not remaining_titles:
            print("No remaining windows to resize.")
            self.resized_windows.clear()
            self.position_windows()
            self.game_timer = threading.Timer(21600, self.resize_random_window)  # Set to 6 hours
            self.game_timer.start()
            return

        random_title = random.choice(remaining_titles)
        window = gw.getWindowsWithTitle(random_title)

        if window:
            window_instance = window[0]
            window_instance.resizeTo(1440, 810)
            window_instance.moveTo(0, 0)
            if window_instance.isMinimized:
                window_instance.restore()

            # Minimize all other windows
            for cb in self.character_comboboxes:
                if cb.get() and cb.get() != random_title:
                    try:
                        other_window_list = gw.getWindowsWithTitle(cb.get())
                        if other_window_list:
                            other_window = other_window_list[0]
                            other_window.minimize()
                        window_instance = window[0]
                        window_instance.resizeTo(1440, 810)
                        window_instance.moveTo(0, 0)
                    except Exception as e:
                        print(f"Error minimizing window '{cb.get()}': {e}")

            # Activate the current window and bring it to the front
            window_hwnd = window_instance._hWnd
            if self.previous_window:
                ctypes.windll.user32.SetWindowPos(self.previous_window, 1, 0, 0, 0, 0, 0x0003)
            ctypes.windll.user32.SetWindowPos(window_hwnd, 0, 0, 0, 0, 0, 0x0003)

            self.previous_window = window_hwnd
            self.resized_windows.add(random_title)
            print(f"Resized and activated: {random_title}")
            ards.send_command('enter_game')
        else:
            print(f"No window found: {random_title}")

        self.character_timer = threading.Timer(120, self.resize_random_window)
        self.character_timer.start()
    
    def stop_schedule(self):
        """Stop all scheduled tasks."""
        if self.game_timer:
            self.game_timer.cancel()
            self.game_timer = None  # Clear the reference
        if self.character_timer:
            self.character_timer.cancel()
            self.character_timer = None  # Clear the reference
        print("All schedules stopped.")

    def save_combobox_data(self, filename="save_data/combobox_data.json"):
        """Save Combobox data to a JSON file."""
        try:
            with open(filename, "w") as json_file:
                json.dump(
                    {f"Character_{idx}": combobox.get() for idx, combobox in enumerate(self.character_comboboxes, start=1)},
                    json_file,
                    indent=4
                )
            print(f"Combobox data saved to {filename}.")
        except Exception as e:
            print(f"Error saving data: {e}")

    def load_combobox_data(self, filename="save_data/combobox_data.json"):
        """Load data from a JSON file and populate the Comboboxes."""
        try:
            # Ensure the directory exists
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            
            # Check if the file exists
            if not os.path.isfile(filename):
                # If the file doesn't exist, create an empty JSON file
                with open(filename, "w") as json_file:
                    json.dump({}, json_file)
            
            # Load the data from the file
            with open(filename, "r") as json_file:
                combobox_data = json.load(json_file)
            
            # Populate the Comboboxes
            for idx, combobox in enumerate(self.character_comboboxes, start=1):
                combobox.set(combobox_data.get(f"Character_{idx}", ""))  # Set value or clear if not found
            print(f"Combobox data loaded from {filename}.")
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading data: {e}")

    def position_windows(self):
        """Resize and position windows based on specific regions assigned to each Combobox."""
        # Define positions (left: 1-9, right: 10-18)
        positions = [(col * 384, 100 + row * 250, 384, 200) for row in range(3) for col in range(3)] + \
                    [(1152 + col * 384, 100 + row * 250, 384, 200) for row in range(3) for col in range(3)]

        for i, combobox in enumerate(self.character_comboboxes):
            if i >= len(positions) or not combobox.get():
                continue
            try:
                window = gw.getWindowsWithTitle(combobox.get())[0]
                x, y, w, h = positions[i]
                window.restore()
                window.resizeTo(w, h)
                window.moveTo(x, y)
                window.activate()
                # print(f"Positioned '{combobox.get()}' at {x}, {y} with size {w}x{h}")
            except Exception as e:
                print(f"Error positioning '{combobox.get()}': {e}")

    def disable_comboboxes(self):
        """Disable all Comboboxes in the character status frame."""
        if messagebox.askokcancel("Warning", "Are you sure you want to start automation?"):
            for combobox in self.character_comboboxes:
                combobox.config(state="disabled")

            self.save_btn.grid_remove()
            self.edit_btn.grid()
            self.refresh_btn['state'] = DISABLED
            self.save_combobox_data()

    def enable_comboboxes(self):
        """Enable all Comboboxes in the character status frame."""
        if messagebox.askokcancel("Warning", "Are you sure you want to stop automation?"):
            for combobox in self.character_comboboxes:
                combobox.config(state="normal")

            self.save_btn.grid()
            self.edit_btn.grid_remove()
            self.refresh_btn['state'] = 'normal'

class DetectStatus:
    def __init__(self):

        self.regions = {
            'Enter': (545, 310, 350, 269),
            'Killed': (583, 582, 272, 41),
            'Start': (1059, 744, 350, 67),
            'Pause': (1059, 744, 350, 67),
            'Powersave': (545, 310, 350, 269),
            'Penalty': (562, 676, 316, 68),
        }

        self.templates = {
            'Enter': cv2.imread('assets/template/enter.png', 0),
            'Killed': cv2.imread('assets/template/killed.png', 0),
            'Start': cv2.imread('assets/template/start.png', 0),
            'Pause': cv2.imread('assets/template/pause.png', 0),
            'Powersave': cv2.imread('assets/template/powersave.png', 0),
            'Penalty': cv2.imread('assets/template/penalty.png', 0),
        }

        # Check if all templates were loaded successfully
        for key, template in self.templates.items():
            if template is None:
                raise FileNotFoundError(f"Template image for '{key}' not found.")
                
        self.detection_thread = None
        self.stop_automate = False
            
    def capture_region(self, region):
        """Capture the region of the screen for template matching."""
        x, y, w, h = region
        screenshot = pyautogui.screenshot(region=(x, y, w, h))
        img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        return gray_img
    
    def check_status_area(self, region, template, method=cv2.TM_SQDIFF_NORMED, threshold=0.1):
        """Check for the presence of a template in a given screen region."""
        x, y, w, h = region  # Assuming region is a tuple (x, y, width, height)
        screenshot = pyautogui.screenshot(region=(x, y, w, h))
        img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Template matching
        result = cv2.matchTemplate(gray_img, template, method)
        min_val, _, min_loc, _ = cv2.minMaxLoc(result)
        
        return min_val < threshold
    
    def check_status(self, status):
        return self.check_status_area(self.regions[status], self.templates[status])

    def check_stats(self):
        if self.check_status('Enter'):
            ards.send_command('enter_game')

    def main_loop(self):
        pass
            

    def start_automation(self):
        self.stop_automate = False
        character.resize_random_window()
        # Start the detection thread if it's not already running
        if self.detection_thread is None or not self.detection_thread.is_alive():
            self.detection_thread = threading.Thread(target=character.resize_random_window)
            self.detection_thread.daemon = True  # Ensures the thread exits when the main program does
            self.detection_thread.start()
        
class App:
    def __init__(self, root):
        root.title("Lineage II")
        root.iconbitmap("assets/excel.ico")
        root.minsize(400, 150)
        root.maxsize(600, 700)
        root.grid_columnconfigure(0, weight=1)
        root.grid_rowconfigure(2, weight=1)
        root.attributes("-topmost", True)  # Make the window always on top
        self._set_geometry(root, 600, 700)

    def start_automation(self):
        if messagebox.askokcancel("Warning", "Are you sure you want to start automation?"):
            self._update_window("assets/Excel_icon_red_modified.ico", True)
            root.attributes("-alpha", 0.7)  # Set opacity to 80%
            arduino.port_frame.grid_remove()
            character.setup_frame.grid_remove()
            logs.stop_button.grid()
            character.resize_random_window()

    def stop_automation(self):
        if messagebox.askokcancel("Warning", "Are you sure you want to stop automation?"):
            self._update_window("assets/excel.ico", False)
            root.attributes("-alpha", 1.0)  # Reset opacity to 100%
            self._set_geometry(root, 600, 700)
            arduino.port_frame.grid()
            character.setup_frame.grid()
            logs.stop_button.grid_remove()
            character.stop_schedule()
            logs.save_to_file()

    def _update_window(self, icon_path, remove_header):
        root.iconbitmap(icon_path)
        root.overrideredirect(remove_header)
        self._set_geometry(root, 400, 150)

    @staticmethod
    def _set_geometry(root, width, height):
        screen_width = root.winfo_screenwidth()  # Get screen width
        x_position = screen_width - width       # Calculate x position for upper right corner
        root.geometry(f"{width}x{height}+{x_position}+0")  # Place window on upper right corner


if __name__ == "__main__":
    # Create the ttkbootstrap-themed window
    root = tb.Window(themename="darkly")
    character = CharacterConfig(root)
    app = App(root)
    arduino = ArduinoPort(root, app)
    comvi = DetectStatus()
    logs = lg.ConsoleLog(root, app)
    sys.stdout =logs
    root.mainloop()
