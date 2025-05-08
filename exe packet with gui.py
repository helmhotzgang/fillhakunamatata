import requests
import json
import threading
import random
import os
import time
from faker import Faker
from tkinter import *
from tkinter import filedialog, messagebox
from queue import Queue
from collections import defaultdict

# Global vars
proxy_queue = Queue()
total_logins = [0]
login_lock = threading.Lock()
run_event = threading.Event()
run_event.set()  # This enables the threads to keep running
max_attempts = 1
attempts_per_course = defaultdict(int)
is_running = False
threads = []


fake = Faker("de_DE")

# List of classes
classes = ["5A", "6A", "7A", "7E", "7EM", "7N", "8A", "8E", "8EM", "8N", "9A", "9E", "9EM", "9N", "10A", "10E", "10EM", "10N", "11", "12"]

course_ids = []
course_lock = threading.Lock()
proxy_list = []

# GUI Setup
root = Tk()
root.title("Registration Script Settings")

# Add labels and input fields for proxies, threads, and max attempts
def browse_file():
    filepath = filedialog.askopenfilename(title="Select Proxies File", filetypes=(("Text Files", "*.txt"), ("All Files", "*.*")))
    if filepath:
        proxies_file.set(filepath)

def start_script():
    global max_attempts, proxy_list, num_threads, is_running, threads

    if is_running:
        # Stop the script
        run_event.clear()
        is_running = False
        start_button.config(text="Start Script")
        print("Stopping threads... Please wait.")
        for t in threads:
            t.join(timeout=2)
        threads.clear()
        print(f"All threads stopped. Total successful registrations: {total_logins[0]}")
        return

    try:
        max_attempts = int(max_attempts_entry.get())
        num_threads = int(thread_count_entry.get())
        run_event.set()
        is_running = True
        start_button.config(text="Stop Script")

        if proxies_file.get():
            read_proxies_from_file(proxies_file.get())
            if proxy_list:
                print("Using proxies.")
            else:
                print("Proxy file selected but empty. Using your own IP.")
        else:
            print("No proxy file selected. Using your own IP.")

        # Start course updater thread
        updater = threading.Thread(target=update_course_ids, daemon=True)
        updater.start()

        # Wait for course_ids to populate
        print("Waiting for course list to populate...")
        while not course_ids and run_event.is_set():
            time.sleep(0.5)

        threads = []
        for i in range(num_threads):
            t = threading.Thread(target=register_user, name=f"Thread-{i+1}", daemon=True)
            t.start()
            threads.append(t)

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")
        run_event.clear()
        is_running = False
        start_button.config(text="Start Script")


# GUI Layout
frame = Frame(root)
frame.pack(padx=10, pady=10)

Label(frame, text="Max Attempts:").grid(row=0, column=0, sticky=W)
max_attempts_entry = Entry(frame)
max_attempts_entry.grid(row=0, column=1)

Label(frame, text="Thread Count:").grid(row=1, column=0, sticky=W)
thread_count_entry = Entry(frame)
thread_count_entry.grid(row=1, column=1)

Label(frame, text="Proxies File:").grid(row=2, column=0, sticky=W)
proxies_file = StringVar()
proxies_file_entry = Entry(frame, textvariable=proxies_file)
proxies_file_entry.grid(row=2, column=1)
Button(frame, text="Browse", command=browse_file).grid(row=2, column=2)

start_button = Button(frame, text="Start Script", command=start_script)
start_button.grid(row=3, column=0, columnspan=3, pady=10)

# Function to read proxies from file
def read_proxies_from_file(filename="proxies.txt"):
    global proxy_list
    if os.path.exists(filename) and os.path.getsize(filename) > 0:
        with open(filename, 'r') as file:
            proxy_list = [line.strip() for line in file if line.strip()]
        print(f"Loaded {len(proxy_list)} proxies.")
    else:
        print("No proxies found or the file is empty. Proceeding without proxies.")

def update_course_ids():
    global course_ids
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    while run_event.is_set():
        try:
            response = requests.get("https://hm.helmholtzschule.de/script/register-user.php", headers=headers, timeout=10)
            try:
                data = response.json()
            except ValueError:
                data = json.loads(response.text)

            with course_lock:
                course_ids = [entry["course_id"] for entry in data if "course_id" in entry]
            print(f"Updated course IDs: {len(course_ids)} found.")
        except Exception as e:
            print(f"Error updating course IDs: {e}")
        time.sleep(10)

def generate_name_and_email():
    full_name = fake.name()
    first_name = full_name.split()[0]
    last_name = full_name.split()[-1]
    email = f"{last_name.lower()}{first_name[0].lower()}@helmholtzschule.de"
    return f"{first_name} {last_name}", email

def check_all_courses_blacklisted():
    """Check if all courses have been blacklisted (max_attempts reached)."""
    with course_lock:
        for course_id in course_ids:
            if attempts_per_course[course_id] < max_attempts:
                return False  # If any course hasn't reached max attempts, return False
    return True  # All courses have been blacklisted

def register_user():
    thread_name = threading.current_thread().name.replace("Thread-", "")
    
    while run_event.is_set():
        proxy = random.choice(proxy_list) if proxy_list else None
        proxies = {"http": proxy, "https": proxy} if proxy else None

        with course_lock:
            if not course_ids:
                print(f"Thread {thread_name}: Waiting for course list...")
                time.sleep(2)
                continue
            course_id = random.choice(course_ids)

            # Check if the course has reached the max attempts, skip it if so
            if attempts_per_course[course_id] >= max_attempts:
                print(f"Thread {thread_name}: Skipping course {course_id} as it has reached the max attempts.")
                continue  # Skip this course and pick another course in the next loop

        name, email = generate_name_and_email()
        random_class = random.choice(classes)

        payload = {
            "course_id": course_id,
            "method": "USER",
            "name": name,
            "email": email,
            "class": random_class
        }
        headers = {
            "Content-Type": "application/json"
        }

        try:
            response = requests.post(
                "https://hm.helmholtzschule.de/script/register-user.php",
                headers=headers,
                data=json.dumps(payload),
                proxies=proxies,
                timeout=15
            )

            attempts_per_course[course_id] += 1

            with login_lock:
                total_logins[0] += 1
            print(f"Thread {thread_name}: Status {response.status_code} | Course: {course_id} | Proxy: {proxy if proxy else 'None'} | Class: {random_class}")
        except Exception as e:
            print(f"Thread {thread_name}: Error with proxy {proxy}: {e}")
        finally:
            continue  # Keep going until Ctrl+C

if __name__ == "__main__":
    root.mainloop()
