from selenium.webdriver import *;
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
import time
import json

# Your info
with open('EditMe.json') as f:
    d=json.load(f)
myUser = d["username"]
myPassword = d["password"]
keepFriends = d["friends"]
API_ENDPOINT = "https://users.roblox.com/v1/usernames/users"

# Gets userID of player
def getUserId(username):
    requestPayload = {
        "usernames": [
            username
        ],
        "excludeBannedUsers": True
    }
    responseData = requests.post(API_ENDPOINT, json=requestPayload)
    # Make sure the request succeeded
    assert responseData.status_code == 200
    userId = responseData.json()["data"][0]["id"]
    return userId

# Initialize Chromium
options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--ignore-ssl-errors')
driver = webdriver.Chrome(options=options)

# Login to roblox
driver.get('http://www.roblox.com/login')
username = WebDriverWait(driver, 20).until(EC.element_to_be_clickable(driver.find_element(By.ID, "login-username")))
username.send_keys(myUser)
password = driver.find_element(By.ID, "login-password")
password.send_keys(myPassword)
driver.find_element(By.ID, "login-button").click()

# Go to friends list
while (driver.current_url != "https://www.roblox.com/home"):
    continue
driver.get('https://www.roblox.com/users/friends#!/friends')

friendList = requests.get(f"https://friends.roblox.com/v1/users/{getUserId(myUser)}/friends").json()["data"]

for i, player in enumerate(friendList):
    if player["name"] not in keepFriends:
        driver.get(f"https://www.roblox.com/users/{player["id"]}/profile")
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, "unfriend-btn")))
        driver.find_element(By.ID, "unfriend-btn").click()
        print(f"PURGE STATUS: {round((i + 1) / (len(friendList) - len(keepFriends)) * 100, 2)}%")
        time.sleep(0.5)

print("PURGE COMPLETED")
driver.close()