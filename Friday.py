import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinter.scrolledtext import ScrolledText
from tkinter import PhotoImage
import openai
import time
import threading
import subprocess
import os
import sys
import json

KEY_FILE = "api_key.json"

def save_api_key(api_key):
    with open(KEY_FILE, "w") as f:
        json.dump({"api_key": api_key}, f)

def load_api_key():
    if os.path.exists(KEY_FILE):
        with open(KEY_FILE, "r") as f:
            data = json.load(f)
            return data.get("api_key")
    return ""

def delete_api_key():
    if os.path.exists(KEY_FILE):
        os.remove(KEY_FILE)
        api_key_entry.delete(0, tk.END)
        status.set("API key deleted.")

def call_openai_api(prompt, api_key):
    openai.api_key = api_key
    full_prompt = f"Write a Python script for the following task. The script should not use terminal inputs and should create any necessary input prompts using tkinter. The script:\n\n{prompt}\n\nPlease provide only the Python code without any explanations."
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": full_prompt}
        ],
        max_tokens=2000
    )
    return response.choices[0].message['content'].strip()

def install_package(package):
    if package == "matplotlib.pyplot":
        package = "matplotlib"
    elif package == "vlc":
        package = "python-vlc"
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
    except subprocess.CalledProcessError as e:
        status.set(f"Error installing package {package}: {e}")
        show_message(f"Error installing package {package}: {e}")

def extract_required_packages(generated_code):
    required_packages = set()
    for line in generated_code.split('\n'):
        if line.startswith("import ") or line.startswith("from "):
            package = line.split()[1].split('.')[0]
            if package not in sys.modules:
                required_packages.add(package)
    return required_packages

def install_required_packages(packages):
    for package in packages:
        install_package(package)

def run_generated_program():
    try:
        vlc_path = "C:\\Program Files\\VideoLAN\\VLC"  # Adjust the path if VLC is installed in a different location
        os.environ['PYTHON_VLC_LIB_PATH'] = vlc_path
        show_message("Program created and saved as 'generated_program.py'. Running it now...")
        progress.set(100)
        subprocess.check_call([sys.executable, "generated_program.py"])
    except subprocess.CalledProcessError as e:
        error_message = str(e.output.decode() if e.output else e)
        if "No module named" in error_message:
            missing_module = error_message.split("No module named ")[1].split("'")[1]
            install_package(missing_module)
            run_generated_program()
        else:
            show_message(f"Error: {error_message}")
            progress.set(0)
    except Exception as e:
        error_message = str(e)
        if "No module named" in error_message:
            missing_module = error_message.split("No module named ")[1]
            install_package(missing_module)
            run_generated_program()
        else:
            show_message(f"Error: {error_message}")
            progress.set(0)

def create_software(prompt, api_key):
    try:
        clear_message()  # Clear messages at the start of the process
        status.set("Generating code...")
        progress_bar.pack(pady=10, fill=tk.X)  # Show the loader
        time.sleep(1)  # Simulate time delay
        generated_code = call_openai_api(prompt, api_key)
        
        progress.set(50)
        status.set("Generated code. Saving to file...")

        # Ensure the generated code is a valid Python script
        if "```python" in generated_code:
            generated_code = generated_code.split("```python")[1].split("```")[0].strip()
        
        with open("generated_program.py", "w") as f:
            f.write(generated_code)

        progress.set(60)
        status.set("Extracting and installing required packages...")
        
        # Extract required packages from the generated code
        required_packages = extract_required_packages(generated_code)
        install_required_packages(required_packages)

        progress.set(80)
        status.set("Running the generated program...")
        time.sleep(1)
        
        run_generated_program()
    
    except Exception as e:
        show_message(f"Error: {e}")
        progress.set(0)
    finally:
        progress_bar.pack_forget()  # Hide the loader when done

def start_creation():
    prompt = prompt_entry.get()
    api_key = api_key_entry.get()
    if not prompt or not api_key:
        status.set("Please enter both the prompt and API key.")
        return
    save_api_key(api_key)
    status.set("Starting...")
    progress.set(0)
    threading.Thread(target=create_software, args=(prompt, api_key)).start()

def load_prompt_from_file():
    file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
    if file_path:
        with open(file_path, "r") as file:
            prompt_entry.delete(0, tk.END)
            prompt_entry.insert(0, file.read().strip())

def open_support_link():
    import webbrowser
    webbrowser.open("https://buymeacoffee.com/madhookah")

def show_message(message):
    if not hasattr(show_message, "message_window"):
        show_message.message_window = tk.Toplevel(root)
        show_message.message_window.title("Message")
        show_message.message_window.geometry("400x200")
        show_message.message_window.configure(bg="black")

        show_message.msg_label = tk.Label(show_message.message_window, text=message, bg="black", fg="#00FF47", wraplength=380, justify="left")
        show_message.msg_label.pack(pady=20)

        show_message.close_button = tk.Button(show_message.message_window, text="Close", command=show_message.message_window.withdraw, bg="black", fg="#00FF47")
        show_message.close_button.pack(pady=10)

    show_message.msg_label.config(text=message)
    show_message.message_window.deiconify()
    show_message.message_window.after(5000, show_message.message_window.withdraw)

def clear_message():
    status.set("")

# Create the main window
root = tk.Tk()
root.title("Fr!day")
root.geometry("650x550")
root.resizable(False, False)
root.configure(bg="black")

# Create and place the title frame
title_frame = tk.Frame(root, bg="black")
title_frame.pack(fill=tk.X, pady=10)

support_button = tk.Button(title_frame, text="Support the Creator", command=open_support_link, bg="orange", fg="black")
support_button.pack(side=tk.RIGHT, padx=10)

# Load the image
friday_image = PhotoImage(file="Friday.png")

# Create and place the image below the support creator section
image_label = tk.Label(root, image=friday_image, bg="black")
image_label.pack(side=tk.TOP, pady=10, anchor=tk.CENTER)

# Create and place the API key label and entry
api_key_label = tk.Label(root, text="Enter OpenAI API Key:", bg="black", fg="#00FF47")
api_key_label.pack(pady=5)

# Calculate the total width of the prompt entry and the load button
total_width = 50  # Total width of the prompt entry and load button combined

api_key_frame = tk.Frame(root, bg="black")
api_key_frame.pack(pady=5)

api_key_entry = tk.Entry(api_key_frame, width=total_width, show='*', bg="black", fg="#00FF47", insertbackground="#00FF47")
api_key_entry.pack(side=tk.LEFT)

# Create and place the delete API key button
delete_key_button = tk.Button(root, text="Delete API Key", command=delete_api_key, bg="black", fg="#00FF47")
delete_key_button.pack(pady=5)

# Add a horizontal line
line = tk.Frame(root, height=2, bd=1, bg="#00FF47")
line.pack(fill=tk.X, pady=10)

saved_api_key = load_api_key()
if saved_api_key:
    api_key_entry.insert(0, saved_api_key)

# Create and place the prompt label and entry
prompt_label = tk.Label(root, text="Enter Prompt:", bg="black", fg="#00FF47")
prompt_label.pack(pady=5)

prompt_frame = tk.Frame(root, bg="black")
prompt_frame.pack(pady=1)

prompt_entry = tk.Entry(prompt_frame, width=total_width-3, bg="black", fg="#00FF47", insertbackground="#00FF47")
prompt_entry.pack(side=tk.LEFT)

# Load icon for the button
file_icon = PhotoImage(file="file_icon.png")  # Ensure you have a file icon in the same directory

load_prompt_button = tk.Button(prompt_frame, image=file_icon, command=load_prompt_from_file, width=30, height=30, bg="black")
load_prompt_button.pack(side=tk.LEFT, padx=5)

# Create and place the start button
start_button = tk.Button(root, text="Hawk-Tuah", command=start_creation, width=20, height=2, font=("Helvetica", 14), relief="solid", borderwidth=2, bg="#00FF47", fg="#000000")
start_button.pack(pady=20)

# Create and place the status label
status = tk.StringVar()
status_label = tk.Label(root, textvariable=status, bg="black", fg="#00FF47")
status_label.pack(pady=5)

# Create and place the circular progress indicator (simulated)
progress = tk.IntVar()
progress_bar = ttk.Progressbar(root, variable=progress, maximum=100, style="#00FF47.Horizontal.TProgressbar")
progress_bar.pack_forget()

# Style configuration for the progress bar
style = ttk.Style()
style.configure("#00FF47.Horizontal.TProgressbar", troughcolor="black", background="#00FF47")

# Create and place the result text box with scroll
result_text = ScrolledText(root, wrap=tk.WORD, height=10, width=60, state='disabled', bg="black", fg="#00FF47", insertbackground="#00FF47")
result_text.pack_forget()

# Run the application
root.mainloop()
