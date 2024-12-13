import time
import random
import string
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from multiprocessing import Process


# Function to generate random data
def generate_random_string(length):
    return ''.join(random.choices(string.ascii_letters, k=length))


def generate_random_email():
    return generate_random_string(10) + "@example.com"


def run_browser_instance(thread_id):
    url = "file:///C:/My%20Web%20Sites/hm%20site/index.html"  # Website URL

    # Start the WebDriver using webdriver-manager
    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Run Chrome in headless mode for faster performance
    driver = webdriver.Chrome(service=service, options=options)

    # Set implicit wait for all elements to 2 seconds for faster search
    driver.implicitly_wait(3)

    is_first_visit = True  # Flag to check if it's the first time loading the page

    try:
        while True:
            # Timer starts
            start_time = time.time()

            # Open the website
            driver.get(url)
            #print("Website loaded.")

            # Wait for the "Ich habe keinen Account/keinen Zugriff" button to be clickable
            WebDriverWait(driver, 3).until(
                EC.element_to_be_clickable((By.XPATH, "//p[text()='Ich habe keinen Account/keinen Zugriff']"))
            )


            # Click the "Ich habe keinen Account/keinen Zugriff" button
            driver.find_element(By.XPATH, "//p[text()='Ich habe keinen Account/keinen Zugriff']").click()
            #print("Clicked on the 'Ich habe keinen Account/keinen Zugriff' button.")

            # Wait for the form to load and fill it
            WebDriverWait(driver, 3).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'v-form'))
            )
            #print("Form loaded successfully.")

            # Enter the name field
            name_input = driver.find_element(By.ID, "input-15")
            name_input.send_keys(generate_random_string(8))
            #print("Entered random name.")
            name_input.send_keys(Keys.TAB)

            # Enter the email field
            email_input = driver.find_element(By.ID, "input-18")
            email_input.send_keys(generate_random_email())
            #print("Entered random email.")
            email_input.send_keys(Keys.TAB)

            class_input = driver.find_element(By.XPATH, "//div[@role='button' and @aria-expanded='false']")
            class_input.click()

            # Directly locate and click the first class option without waiting unnecessarily
            first_class_option = WebDriverWait(driver, 1).until(
                EC.presence_of_element_located(
                    (By.XPATH, "(//div[@role='listbox']//div[@class='v-list-item__content'])[1]"))
            )
            first_class_option.click()
            #print("Selected a class.")

            # Click the "Weiter" button
            driver.execute_script("window.scrollTo(0, 800);")  # Scroll down to make sure the button is in view
            WebDriverWait(driver, 3).until(
                EC.element_to_be_clickable((By.XPATH, "//button/span[text()='Weiter']"))
            ).click()
            #print("Weiter button clicked.")

            # Click the "Anmelden" button directly
            WebDriverWait(driver, 3).until(
                EC.element_to_be_clickable((By.XPATH, "//button/span[text()='Anmelden']"))
            ).click()
            #print("Anmelden button clicked.")

            # Timer ends
            end_time = time.time()
            duration = end_time - start_time
            print(f"Thread {thread_id}: Login process completed in {duration:.2f} seconds.")

            #print("Reloading the page...\n")

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        # Close the driver when done
        driver.quit()
        #print("Browser instance closed.")


if __name__ == "__main__":
    # Create and start 10 browser processes, passing the thread_id to each process
    processes = []
    for thread_id in range(1, 11):  # Thread ids from 1 to 10
        process = Process(target=run_browser_instance, args=(thread_id,))
        process.start()
        processes.append(process)

    try:
        # Keep the main script alive while the subprocesses run
        for process in processes:
            process.join()
    except KeyboardInterrupt:
        print("Script stopped by user.")
    finally:
        for process in processes:
            process.terminate()
            process.join()
        print("All browser instances closed.")
