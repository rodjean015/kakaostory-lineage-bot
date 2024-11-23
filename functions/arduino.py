import os
import subprocess
import urllib.request
import zipfile
import serial
import serial.tools.list_ports
from tkinter import Tk, messagebox


# Function to download a file
def download_file(url, save_path):
    try:
        urllib.request.urlretrieve(url, save_path)
        print(f"Downloaded: {save_path}")
        return True
    except Exception as e:
        print(f"Error downloading {url}: {e}")
        return False


# Function to install Arduino CLI
def install_arduino_cli():
    cli_url = "https://downloads.arduino.cc/arduino-cli/arduino-cli_latest_Windows_64bit.zip"
    cli_zip_path = "arduino-cli.zip"
    cli_extracted_dir = "arduino-cli"

    if not os.path.exists(cli_extracted_dir):
        # Download Arduino CLI
        if download_file(cli_url, cli_zip_path):
            try:
                with zipfile.ZipFile(cli_zip_path, 'r') as zip_ref:
                    zip_ref.extractall(cli_extracted_dir)
                os.remove(cli_zip_path)
                print("Arduino CLI installed successfully.")
                return True
            except Exception as e:
                print(f"Error extracting Arduino CLI: {e}")
                return False
        else:
            return False
    else:
        print("Arduino CLI already installed.")
        return True


# Function to install Arduino drivers
def install_arduino_drivers():
    drivers_url = "https://www.arduino.cc/en/uploads/Main/arduino-drivers.zip"
    drivers_zip_path = "arduino-drivers.zip"
    drivers_extracted_dir = "arduino-drivers"

    if not os.path.exists(drivers_extracted_dir):
        # Download Arduino drivers
        if download_file(drivers_url, drivers_zip_path):
            try:
                with zipfile.ZipFile(drivers_zip_path, 'r') as zip_ref:
                    zip_ref.extractall(drivers_extracted_dir)
                os.remove(drivers_zip_path)

                # Run driver installer
                driver_installer_path = os.path.join(drivers_extracted_dir, "dpinst-amd64.exe")
                if os.path.exists(driver_installer_path):
                    subprocess.run(driver_installer_path, shell=True)
                    print("Arduino drivers installed successfully.")
                    return True
                else:
                    print("Driver installer not found.")
                    return False
            except Exception as e:
                print(f"Error extracting Arduino drivers: {e}")
                return False
        else:
            return False
    else:
        print("Arduino drivers already installed.")
        return True


# Function to install required Arduino platform (e.g., arduino:avr)
def install_arduino_core(core_name="arduino:avr"):
    command = f'arduino-cli core install {core_name}'
    try:
        output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
        print(output.decode('utf-8'))
        print(f"Platform {core_name} installed successfully.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error installing platform {core_name}: {e.output.decode('utf-8')}")
        messagebox.showerror("Error", f"Failed to install platform {core_name}.")
        return False


# Function to compile Arduino sketch
def compile_sketch(sketch_path):
    core_name = "arduino:avr"
    board = "leonardo"  # Change to a compatible board
    command = f'arduino-cli compile --fqbn {core_name}:{board} "{sketch_path}"'

    # Ensure core is installed before compiling
    if not install_arduino_core(core_name):
        print(f"Failed to install core {core_name}. Compilation aborted.")
        return False

    try:
        output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
        print(output.decode())
        messagebox.showinfo("Success", "Sketch compiled successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error during compilation: {e.output.decode()}")
        messagebox.showerror("Error", "Compilation failed. Check the sketch and try again.")
        return False


# Function to upload Arduino sketch
def upload_sketch(sketch_path, port):
    core_name = "arduino:avr"
    board = "leonardo"  # Change to a compatible board
    command = f'arduino-cli upload -p {port} --fqbn {core_name}:{board} "{sketch_path}"'

    # Ensure core is installed before uploading
    if not install_arduino_core(core_name):
        print(f"Failed to install core {core_name}. Upload aborted.")
        return False

    # Validate port before uploading
    available_ports = [p.device for p in serial.tools.list_ports.comports()]
    if port not in available_ports:
        print(f"Error: Port {port} not found. Available ports: {available_ports}")
        messagebox.showerror("Error", f"Port {port} not found. Available ports: {available_ports}")
        return False

    try:
        output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
        print(output.decode())
        messagebox.showinfo("Success", "Sketch uploaded successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error during upload: {e.output.decode()}")
        messagebox.showerror("Error", "Upload failed. Check the connection and try again.")
        return False


# Function to list available COM ports
def list_ports():
    ports = serial.tools.list_ports.comports()
    ports_list = [port.device for port in sorted(ports)]
    print("Available COM ports:", ports_list)
    if not ports_list:
        messagebox.showwarning("Warning", "No available COM ports detected.")
    return ports_list


# Function to initialize serial communication
def init_serial(port, baudrate=9600):
    try:
        serial_inst = serial.Serial(port=port, baudrate=baudrate, timeout=1)
        print(f"Connected to {serial_inst.port}.")
        messagebox.showinfo("Info", f"Connected to {port}.")
        return serial_inst
    except serial.SerialException as e:
        print(f"Error initializing serial communication: {e}")
        messagebox.showerror("Error", f"Failed to connect to {port}. Please check the connection.")
        return None


# Main setup function
def setup_environment():
    print("Setting up environment...")
    if install_arduino_cli() and install_arduino_drivers():
        print("Environment setup completed.")
        messagebox.showinfo("Success", "Environment setup completed!")
    else:
        print("Environment setup failed. Please check logs.")
        messagebox.showerror("Error", "Environment setup failed. Please check logs.")


# Entry point
if __name__ == "__main__":
    root = Tk()
    root.withdraw()  # Hide the main Tkinter window since it's not needed
    setup_environment()
    available_ports = list_ports()

    # Example Sketch Path
    arduino_sketch_path = "path/to/your/sketch.ino"

    if available_ports:
        selected_port = available_ports[0]  # Automatically select the first port
        print(f"Using port: {selected_port}")
        if compile_sketch(arduino_sketch_path):
            upload_success = upload_sketch(arduino_sketch_path, selected_port)
            if upload_success:
                print("Upload completed successfully!")
            else:
                print("Upload failed.")
    else:
        print("No available COM ports detected.")
