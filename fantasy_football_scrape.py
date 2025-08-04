#!/usr/bin/env python3

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import json

def WebsiteFactory(website):
    
    if website == "yahoo":
        return YahooNFL()

    return None


class YahooNFL():

    def scrape_stats(self):

        # Optional: run headless (no GUI)
        options = Options()
        options.add_argument('--headless')  # Uncomment for headless mode

        # Path to your chromedriver
        # TODO: I want to use this, but can't find the path to 
        #driver_path = '/path/to/chromedriver'
        #service = Service(driver_path)
        #driver = webdriver.Chrome(service=service, options=options)

        service = Service(ChromeDriverManager().install()) 
        driver = webdriver.Chrome(service=service, options=options)

        try:
            # Load the Yahoo Sports NFL stats page (or other target)
            url = "https://sports.yahoo.com/nfl/stats/weekly/?selectedTable=2" 
            driver.get(url)

            # Wait for JS to load and populate root.App
            #time.sleep(5)  # Adjust as needed, or use WebDriverWait for reliability
            WebDriverWait(driver, timeout=10).until(
                lambda d: d.execute_script("return typeof window.App?.main !== 'undefined';")
            )

            # Use JavaScript to access the embedded object
            app_data = driver.execute_script("return window.App?.main;")

            if app_data:
                with open("app_main.json", "w") as f:
                    json.dump(app_data, f, indent=2)
                print("App data saved to app_main.json")
            else:
                print("App.main not found.")
        finally:
            driver.quit()

class Program():

    def work_loop(self):

        website = WebsiteFactory("yahoo")

        website.scrape_stats()

    def main(self):
        
        self.work_loop()
        

if __name__ == "__main__":

    p = Program()

    p.main()

