import time
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
from multiprocessing import Process

total_logins = 0

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


def run_browser_instance(thread_id):
    url = "https://hm.helmholtzschule.de/"  # Website URL

    # Start the WebDriver using webdriver-manager
    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Run Chrome in headless mode for faster performance
    driver = webdriver.Chrome(service=service, options=options)

    retry_limit = 3  # Number of retry attempts for each error

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
                    total_logins += 1
                    break  # Exit retry loop if successful

                except (TimeoutException, WebDriverException) as e:
                    retry_count += 1
                    print(f"Thread {thread_id}: Error occurred - Retrying {retry_count}/{retry_limit}...")

                    if retry_count == retry_limit:
                        print(f"Thread {thread_id}: Max retries reached. Skipping this iteration.")
                        break  # Skip this iteration after max retries


    except Exception as e:
        print(f"Thread {thread_id}: A critical error occurred.")

    finally:
        driver.quit()
        print(f"Thread {thread_id}: Browser instance closed.")


if __name__ == "__main__":
    def start_thread(thread_id):
        """Function to start a thread with a given thread_id."""
        print(f"Thread {thread_id}: Starting...")  # Print when the thread starts
        process = Process(target=run_browser_instance, args=(thread_id,))
        process.start()
        return process
    num_threads = get_thread_count()
    # Create and start 10 browser processes, monitoring for crashes
    processes = {}
    for thread_id in range(1, num_threads + 1):  # Use user-defined number of threads
        processes[thread_id] = start_thread(thread_id)

    try:
        while True:
            # Monitor processes and restart any that have crashed
            for thread_id, process in processes.items():
                if not process.is_alive():  # Check if the process is no longer running
                    print(f"Thread {thread_id} crashed. Restarting...")
                    processes[thread_id] = start_thread(thread_id)

            time.sleep(1)  # Check every second

    except KeyboardInterrupt:
        print("Script stopped by user.")
    finally:
        for process in processes.values():
            process.terminate()
            process.join()
        print("All browser instances closed.")
        print(f"Total Logins completed: {total_logins}")
