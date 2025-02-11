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
    print(d)
myUser = d["username"]
myPassword = d["password"]
keepFriends = d["friends"]

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
driver.maximize_window()
API_ENDPOINT = "https://users.roblox.com/v1/usernames/users"

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

new_ID_List = []
running = True
while running:
    print(new_ID_List)
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, "avatar-cards")))
    ID_List = driver.find_element(By.CLASS_NAME, "avatar-cards")
    ID_List = ID_List.text.split()
    for name in ID_List:
        if name[0] == "@":
            if name[1:] in new_ID_List:
                running = False
                break
            new_ID_List.append(name[1:])
    try:
        driver.find_element(By.CLASS_NAME, "pager-next").click()
    except:
        running = False
    time.sleep(1)
    
ID_List = []
for i, playerName in enumerate(new_ID_List):
    if playerName not in keepFriends:
        playerID = getUserId(playerName)
        if playerID != None:
            ID_List.append(playerID)

for i, playerID in enumerate(ID_List):
    driver.get(f"https://www.roblox.com/users/{playerID}/profile")
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "unfriend-btn")))
    driver.find_element(By.ID, "unfriend-btn").click()
    time.sleep(1)