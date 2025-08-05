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
import csv

def WebsiteFactory(website):
    
    if website == "yahoo":
        return YahooNFL()

    return None

def PlayerFactory(positionId):

    if positionId == "Receiving":
        return Receiver()

    return None

class Player():

    player = ""
    positionId = ""
    team = ""
    url = ""

class Receiver(Player):
   
    stats_dictionary = { 
        "RECEPTIONS" : -1,
        "TARGETS" : -1,
        "RECEIVING_YARDS" : -1,
        "RECEIVING_YARDS_PER_RECEPTION" : -1,
        "LONGEST_RECEPTION" : -1,
        "RECEIVING_FIRST_DOWNS" : -1,
        "RECEIVING_TOUCHDOWNS" : -1,
        "FUMBLES" : -1,
        "FUMBLES_LOST" : -1
    }

    def to_string(self):
        print(f"""
            Player = {self.player}
            Team = {self.team}    
            {self.stats_dictionary}
        """)

    def extract_data_from_json_dicts(self, data):

        self.player = data["player"]["displayName"]
        self.positionId = data["player"]["positions"][0]["positionId"]
        self.url = data["player"]["alias"]["url"]
        self.team = data["player"]["team"]["displayName"]

        for stat in data['stats']:
            statId = stat["statId"]
            self.stats_dictionary[statId] = stat["value"] if stat["value"] is not None else 0

        self.to_string()

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
        # TODO: Is this really necessary?
        #options.add_argument("--disable-blink-features=AutomationControlled")
        #options.add_argument("--no-sandbox")
        #options.add_argument("--disable-dev-shm-usage")

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

            keyword = ["Receiving"]
            i = 0
            receiving_data = self.find_key_recursive(app_data, "weeklyStatsFootball" + keyword[i])
            
            receiving = (receiving_data
                .get("nfl", {})
                .get("200", {})
                .get("2025", {})
                .get("1", {})
                .get("PRESEASON", {})
                .get("", {})
                .get("RECEIVING_YARDS", {})
            )

            leaders = receiving["leagues"][0]["leagueWeeks"][0]["leaders"]
            for leader in leaders:

                #positionId = leader["player"]["positions"][0]["positionId"]
                player = PlayerFactory(keyword[i])
                player.extract_data_from_json_dicts(leader)

            #
            # Debugging: This dumps the data
            #
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

