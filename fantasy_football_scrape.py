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

    def find_key_recursive(self, d, key):
        if isinstance(d, dict):
            if key in d:
                return d[key]
            for k, v in d.items():
                result = self.find_key_recursive(v, key)
                if result is not None:
                    return result
        elif isinstance(d, list):
            for item in d:
                result = self.find_key_recursive(item, key)
                if result is not None:
                    return result
        return None

    def scrape_stats(self):

        # Optional: run headless (no GUI)
        options = Options()
        
        # Wait for DOMContentLoaded (don't wait for the whole page to load)
        # without this the page loads, but never finishes and the driver.get(url) times out
        options.page_load_strategy = 'eager'

        options.add_argument('--headless=new')  # Uncomment for headless mode
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/115.0 Safari/537.36")

        """
        # Use a common browser user agent string
        user_agent = (
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
        )

        options.add_argument(f"user-agent={user_agent}")
        """
        # Optional: speed it up
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        # Path to your chromedriver
        # TODO: I want to use this, but can't find the path to 
        #driver_path = '/path/to/chromedriver'
        #service = Service(driver_path)
        #driver = webdriver.Chrome(service=service, options=options)

        service = Service(ChromeDriverManager().install()) 
        driver = webdriver.Chrome(service=service, options=options)

        try:
            # Load the Yahoo Sports NFL stats page (or other target)
            url = "https://sports.yahoo.com/nfl/stats/weekly"
            print(f"driver.get({url})")
            driver.get(url)
            print("Finished.")

            # Wait for JS to load and populate root.App
            #time.sleep(5)  # Adjust as needed, or use WebDriverWait for reliability
            WebDriverWait(driver, timeout=15).until(
                lambda d: d.execute_script("return typeof window.App?.main !== 'undefined';")
            )

            # Use JavaScript to access the embedded object
            app_data = driver.execute_script("return window.App?.main;")

            receiving_data = self.find_key_recursive(app_data, "weeklyStatsFootballReceiving")
            
            receiving = (receiving_data
                .get("nfl", {})
                .get("200", {})
                .get("2025", {})
                .get("1", {})
                .get("PRESEASON", {})
                .get("", {})
                .get("RECEIVING_YARDS", {})
            )
            
            #leaders = receiving.get("leagues", [])[0].get("leagueWeeks", [])[0].get("leaders", [])
            
            leaders = receiving["leagues"][0]["leagueWeeks"][0]["leaders"]
            for leader in leaders:
                name = leader["player"]["displayName"]
                print(f"{name}")
                yards = next((s["value"] for s in leader["stats"] if s["statId"] == "RECEIVING_YARDS"), None)
                print(f"{name}: {yards} yards")

            """
            receiving_data = self.find_weekly_stats(app_data)
            if not receiving_data:
                raise ValueError("Could not find 'weeklyStatsFootballReceiving'")  

            # Navigate to the data layer you care about
            leaders = receiving_data["nfl"]["200"]["2025"]["1"]["PRESEASON"][""]["RECEIVING_YARDS"]["leagues"][0]["leagueWeeks"][0]["leaders"]

            rows = []
            for entry in leaders:
                player = entry.get("player", {})
                print(player)
                #stats = entry.get("stats", [])
            """


            if app_data:
                with open("app_main.json", "w") as f:
                    json.dump(receiving, f, indent=2)
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

