
import threading
import numpy as np
import pyautogui
import cv2
import arduino as ards
import time

class DetectStatus:
    def __init__(self):

        self.regions = {
            'Enter': (545, 310, 350, 269),
            'Killed': (583, 582, 272, 41),
            'Start': (1059, 744, 350, 67),
            'Pause': (1059, 744, 350, 67),
            'Powersave': (545, 310, 350, 269),
        }

        self.templates = {
            'Enter': cv2.imread('assets/template/enter.png', 0),
            'Killed': cv2.imread('assets/template/killed.png', 0),
            'Start': cv2.imread('assets/template/start.png', 0),
            'Pause': cv2.imread('assets/template/pause.png', 0),
            'Powersave': cv2.imread('assets/template/powersave.png', 0),
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
        status_messages = {'Enter': "Enter Game", 'Killed': "Killed", 'Start': "Schedule Start", 'Pause': "Schedule Pause", 'Powersave': "Powersave"}
        
        for status, message in status_messages.items():
            if self.check_status(status):
                print(message)
                return
            
        print("No Matching!!!")

    def main_loop(self):
        while not self.stop_automate:
            self.check_stats()

    def start_automation(self):
        self.stop_automate = False
        
        # Start the detection thread if it's not already running
        if self.detection_thread is None or not self.detection_thread.is_alive():
            self.detection_thread = threading.Thread(target=self.main_loop)
            self.detection_thread.daemon = True  # Ensures the thread exits when the main program does
            self.detection_thread.start()

    def stop_automation(self):
        self.stop_automate = True
    