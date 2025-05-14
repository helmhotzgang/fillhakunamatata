import requests
import json
import threading
import random
import os
import time
from faker import Faker

# Config
max_courses = 100
fake = Faker("de_DE")
classes = ["5A", "6A", "7A", "7E", "7EM", "7N", "8A", "8E", "8EM", "8N", "9A", "9E", "9EM", "9N", "10A", "10E", "10EM", "10N", "11", "12"]
proxy_list = []
created_courses = [0]
run_event = threading.Event()
run_event.set()

# Preset list of valid rooms
valid_rooms = [
    "101", "102", "103", "105", "106", "107", "109",
    "201", "202", "203", "204", "205", "206", "207", "208",
    "301", "302", "304", "305",
    "K002", "K101", "K102", "K103", "K104", "K105", "K106", "K108", "K109",
    "K201", "K203", "K204", "K205", "K206", "K207", "K208", "K209",
    "K301", "K302", "K303", "K304", "K305", "K306", "K308", "K309"
]

def read_proxies(filename="proxies.txt"):
    global proxy_list
    if os.path.exists(filename):
        with open(filename, "r") as file:
            proxy_list = [line.strip() for line in file if line.strip()]
        print(f"Loaded {len(proxy_list)} proxies.")
    else:
        print("No proxy file found. Running without proxies.")

def generate_leader():
    name = fake.name()
    email = f"{name.split()[-1].lower()}{name[0].lower()}@helmholtzschule.de"
    class_ = random.choice(classes)
    return {"name": name, "email": email, "class": class_}

def generate_course():
    leaders = [generate_leader()]
    return {
        "leaders": leaders,
        "course_name": fake.catch_phrase(),
        "participants": random.randint(5, 50),
        "description": fake.text(max_nb_chars=150),
        "goal": fake.sentence(),
        "cost": round(random.uniform(0, 15), 2),
        "room_wish": random.choice(valid_rooms),  # Select a random room from the valid list
        "teacher_wish": random.choice([fake.name(), ""])
    }

def register_course():
    thread_name = threading.current_thread().name
    while run_event.is_set() and created_courses[0] < max_courses:
        course_data = generate_course()
        proxy = random.choice(proxy_list) if proxy_list else None
        proxies = {"http": proxy, "https": proxy} if proxy else None

        try:
            response = requests.post(
                "https://hm.helmholtzschule.de/script/register-course.php",
                headers = {
                    "Content-Type": "application/json",
                    "User-Agent": "Mozilla/5.0"},
                data=json.dumps(course_data),
                proxies=proxies,
                timeout=15
            )
            if response.status_code == 200:
                created_courses[0] += 1
                print(f"{thread_name}: Registered course {created_courses[0]} | {course_data['course_name']} | Proxy: {proxy or 'None'}")
            else:
                print(f"{thread_name}: Failed ({response.status_code})")
        except Exception as e:
            print(f"{thread_name}: Error with proxy {proxy}: {e}")
        time.sleep(random.uniform(0.1, 0.5))

def main():
    read_proxies()
    thread_count = int(input("Enter number of threads (1–100): "))
    threads = []

    try:
        for i in range(thread_count):
            t = threading.Thread(target=register_course, name=f"CourseThread-{i+1}", daemon=True)
            t.start()
            threads.append(t)

        while run_event.is_set() and created_courses[0] < max_courses:
            time.sleep(1)  # Sleep in the main thread to allow the threads to keep running

    except KeyboardInterrupt:
        print("Interrupted. Stopping all threads.")
        run_event.clear()  # This will stop the threads by clearing the event

    # Join all threads once the event is cleared
    for t in threads:
        t.join()

    print(f"Done. Total courses registered: {created_courses[0]}")

if __name__ == "__main__":
    main()
