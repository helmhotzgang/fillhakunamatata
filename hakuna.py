import time
import os
import random
import string
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException, TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
from multiprocessing import Process, Value


# Function to generate random data
def generate_random_string(length):
    return ''.join(random.choices(string.ascii_letters, k=length))


def generate_random_email():
    return generate_random_string(10) + "@" + generate_random_string(5) + ".com"

def get_thread_count():
    """Prompt the user to input a number between 1 and 1000."""
    while True:
        try:
            thread_count = int(input("Enter the number of threads (between 1 and 1000): "))
            if 1 <= thread_count <= 1000:
                return thread_count
            else:
                print("Please enter a number between 1 and 1000.")
        except ValueError:
            print("Invalid input. Please enter an integer.")

def read_proxies_from_file(filename="proxies.txt"):
    """Reads proxy list from the file if it exists and is not empty."""
    if os.path.exists(filename) and os.path.getsize(filename) > 0:
        with open(filename, 'r') as file:
            proxies = [line.strip() for line in file.readlines() if line.strip()]
        if proxies:
            print(f"Loaded {len(proxies)} proxies from file.")
            return proxies
    print("No proxies found or the file is empty. Proceeding without proxies.")
    return None

def run_browser_instance(thread_id, proxies=None):
    proxy_index = 0  # Start with the first proxy
    proxy = None

# If proxies are provided, set one for each login attempt
    if proxies:
        proxy = proxies[proxy_index]  # Use the first proxy initially


    url = "https://hm.helmholtzschule.de/"  # Website URL

    # Start the WebDriver using webdriver-manager
    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Run Chrome in headless mode for faster performance
    if proxy:
        options.add_argument(f"--proxy-server={proxy}")  # Set the initial proxy
    driver = webdriver.Chrome(service=service, options=options)

    retry_limit = 3  # Number of retry attempts for each error
    max_proxy_switches = len(proxies) if proxies else 0  # Max number of proxy switches (i.e., number of proxies available)
    failures_since_last_proxy = 0  # Counter to track how many consecutive failures occurred


    try:
        while True:
            retry_count = 0  # Reset retry counter for each iteration
            while retry_count < retry_limit:
                try:
                    # Timer starts
                    start_time = time.time()

                    # Open the website
                    driver.get(url)

                    # Wait for the "Ich habe keinen Account/keinen Zugriff" button to be clickable
                    WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, "//p[text()='Ich habe keinen Account/keinen Zugriff']"))
                    )

                    # Click the button
                    driver.find_element(By.XPATH, "//p[text()='Ich habe keinen Account/keinen Zugriff']").click()

                    # Wait for the form to load and fill it
                    WebDriverWait(driver, 3).until(
                        EC.presence_of_element_located((By.CLASS_NAME, 'v-form'))
                    )

                    # Enter the name field
                    name_input = driver.find_element(By.ID, "input-15")
                    name_input.send_keys(generate_random_string(8))
                    name_input.send_keys(Keys.TAB)

                    # Enter the email field
                    email_input = driver.find_element(By.ID, "input-18")
                    email_input.send_keys(generate_random_email())
                    email_input.send_keys(Keys.TAB)

                    # Select the class
                    class_input = driver.find_element(By.XPATH, "//div[@role='button' and @aria-expanded='false']")
                    class_input.click()

                    # Click the first class option
                    first_class_option = WebDriverWait(driver, 1).until(
                        EC.presence_of_element_located(
                            (By.XPATH, "(//div[@role='listbox']//div[@class='v-list-item__content'])[1]")
                        )
                    )
                    first_class_option.click()

                    # Click the "Weiter" button
                    driver.execute_script("window.scrollTo(0, 800);")  # Scroll down to ensure the button is in view
                    WebDriverWait(driver, 3).until(
                        EC.element_to_be_clickable((By.XPATH, "//button/span[text()='Weiter']"))
                    ).click()

                    # Click the "Anmelden" button directly
                    WebDriverWait(driver, 3).until(
                        EC.element_to_be_clickable((By.XPATH, "//button/span[text()='Anmelden']"))
                    ).click()

                    # Timer ends
                    end_time = time.time()
                    duration = end_time - start_time
                    print(f"Thread {thread_id}: Login process completed in {duration:.2f} seconds.")

                    with total_logins.get_lock():
                        total_logins.value += 1

                    break  # Exit retry loop if successful

                except (TimeoutException, WebDriverException) as e:
                    retry_count += 1
                    print(f"Thread {thread_id}: Error occurred - Retrying {retry_count}/{retry_limit}...")

                    if retry_count == retry_limit:
                        failures_since_last_proxy += 1
                        print(f"Thread {thread_id}: Max retries reached for current proxy.")

                        # Switch proxy after max retries if there are more proxies
                        if failures_since_last_proxy >= retry_limit and proxy_index < len(proxies) - 1:
                            proxy_index += 1
                            proxy = proxies[proxy_index]  # Switch to next proxy
                            failures_since_last_proxy = 0  # Reset failure counter
                            print(f"Thread {thread_id}: Switching to proxy {proxy}.")
                            driver.quit()  # Quit the previous driver
                            options.add_argument(f"--proxy-server={proxy}")  # Set the new proxy
                            driver = webdriver.Chrome(service=service, options=options)  # Restart with new proxy
                        else:
                            print(f"Thread {thread_id}: No more proxies available. Skipping iteration.")
                            break  # Skip this iteration after max retries and proxy changes


    except Exception as e:
        print(f"Thread {thread_id}: A critical error occurred.")

    finally:
        driver.quit()
        print(f"Thread {thread_id}: Browser instance closed.")


if __name__ == "__main__":
    def start_thread(thread_id, proxies):
        """Function to start a thread with a given thread_id."""
        print(f"Thread {thread_id}: Starting...")  # Print when the thread starts
        process = Process(target=run_browser_instance, args=(thread_id, proxies))

        process.start()
        return process
    total_logins = Value('i', 0)
    proxies = read_proxies_from_file()  # Load proxies from file

    num_threads = get_thread_count()
    # Create and start 10 browser processes, monitoring for crashes
    processes = {}
    for thread_id in range(1, num_threads + 1):  # Use user-defined number of threads
        processes[thread_id] = start_thread(thread_id, proxies)

    try:
        while True:
            # Monitor processes and restart any that have crashed
            for thread_id, process in processes.items():
                if not process.is_alive():  # Check if the process is no longer running
                    print(f"Thread {thread_id} crashed. Restarting...")
                    processes[thread_id] = start_thread(thread_id, proxies)

            time.sleep(1)  # Check every second

    except KeyboardInterrupt:
        print("Script stopped by user.")
    finally:
        for process in processes.values():
            process.terminate()
            process.join()
        print("All browser instances closed.")
        print(f"Total Logins completed: {total_logins.value}")