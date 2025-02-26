import ttkbootstrap as ttk
import tkinter as tk
import json
import time
from pathlib import Path
from selenium.webdriver import *;
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests

PROJECT_DIR = Path(__file__).parent

# Your info
with open(rf'{PROJECT_DIR}/UserData.json') as f:
    d=json.load(f)
myUser = d["username"]
myPassword = d["password"]
friendsToKeep = d["friends"]
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

def Initialize_Chromium():
    global driver
    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--ignore-ssl-errors')
    driver = webdriver.Chrome(options=options)
    driver.minimize_window()

def loginToRoblox():
    Initialize_Chromium()
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

def purge_event(userName, passWord, friendList):
    global myUser, myPassword
    myUser, myPassword,  = userName.replace("\n", ""), passWord.replace("\n", "")
    with open(rf"{PROJECT_DIR}/UserData.json", "r") as f:
        file = json.load(f)
    file["username"] = myUser
    file["password"] = myPassword
    file["friends"] = friendList.splitlines()
    with open(rf"{PROJECT_DIR}/UserData.json", "w") as f:
        json.dump(file, f)
    loginToRoblox()
    for widget in app.winfo_children():
        widget.destroy()
    topFrame = ttk.Frame(app)
    topFrame.grid(row=0, columnspan=3)
    mainName = ttk.Label(topFrame, text="ROBLOX Friends List Purger", font=("Arial", 40), padding=25)
    mainName.pack(side="top")
    listOfFriends = requests.get(f"https://friends.roblox.com/v1/users/{getUserId(myUser)}/friends").json()["data"]
    numberOfIters = len(listOfFriends) - len(friendsToKeep)
    progressFrame = ttk.Frame(app)
    progressFrame.grid(row=1, columnspan=3)
    bar = ttk.Progressbar(progressFrame, length=750, maximum=100, mode="determinate")
    bar.pack(padx=12)
    progressFrame = ttk.Frame(app)
    progressFrame.grid(row=3, columnspan=3)
    progressPercentage = ttk.Label(progressFrame, text=f"0.00%", font=("Arial", 40), padding=25) # transparent
    progressPercentage.pack()
    app.update()
    bar.start()
    i = 1
    for player in listOfFriends:
        if player["name"] not in friendsToKeep:
            driver.get(f"https://www.roblox.com/users/{player["id"]}/profile")
            WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, "unfriend-btn")))
            driver.find_element(By.ID, "unfriend-btn").click()
            progressPercentage.destroy()
            progressPercentage = ttk.Label(progressFrame, text=f"{round((i)/numberOfIters * 100, 2)}%", font=("Arial", 40), padding=25) # transparent
            progressPercentage.pack()
            bar['value'] = (i)/numberOfIters * 100
            bar.update_idletasks()
            app.update()
            i += 1
    bar.stop()
    app.update()
    driver.close()
    for widget in app.winfo_children():
        widget.destroy()
    time.sleep(3)
    progressPercentage.destroy()
    progressPercentage = ttk.Label(progressFrame, text="Purge Complete!", font=("Arial", 40), padding=25) # transparent
    progressPercentage.pack()
    exit()

app = ttk.Window(title="ROBLOX Friends List Purger", themename="darkly", size=(775,400))
app.resizable(False, False)
app.grid()

topFrame = ttk.Frame(app)
topFrame.grid(row=0, columnspan=2)
mainName = ttk.Label(topFrame, text="ROBLOX Friends List Purger", font=("Arial", 40), padding=25)
mainName.pack(side="top")

friendsFrame = ttk.Frame(app)
friendsFrame.grid(row=1, column=0, padx=20)
friendsLabel = ttk.Label(friendsFrame, text="Enter all usernames of friends you would like to keep on seperate lines (CASE SENSITIVE):", font=("Arial", 12), padding=7, wraplength=350)
friendsLabel.pack()
keepFriends = ttk.Text(friendsFrame, foreground="grey", height=10, width=50)
for i, friend in enumerate(d["friends"]):
    keepFriends.insert(f"{i}.0", f"{friend}\n")
keepFriends.pack()

loginFrame = ttk.Frame(app)
loginFrame.grid(row=1, column=1, padx=20)
loginLabel = ttk.Label(loginFrame, text="Login Info", font=("Arial", 18), padding=7)
loginLabel.pack(side="top")
userLabel = ttk.Label(loginFrame, text="Username:", font=("Arial", 12), padding=7)
userLabel.pack(side="top")
userName = ttk.Text(loginFrame, foreground="grey", height=1, width=50)
userName.insert("0.0", f"{d["username"]}")
userName.pack(side="top")
passLabel = ttk.Label(loginFrame, text="Password:", font=("Arial", 12), padding=7)
passLabel.pack(side="top")
password = ttk.Text(loginFrame, foreground="grey", height=1, width=50)
password.insert("0.0", f"{d["password"]}")
password.pack(side="top")

topFrame = ttk.Frame(app)
topFrame.grid(row=2, columnspan=3, padx=20, pady=20)
purgeButton = ttk.Button(topFrame, command=lambda:purge_event(userName.get("0.0", "end"), password.get("0.0", "end"), keepFriends.get("0.0", "end")), text="PURGE", width=115)
purgeButton.pack()

app.mainloop()
