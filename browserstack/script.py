import json
import os

from dotenv import load_dotenv
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# from browserstack.local import Local

load_dotenv()
BROWSERSTACK_USERNAME = os.environ.get("BROWSERSTACK_USERNAME")
BROWSERSTACK_ACCESS_KEY = os.environ.get("BROWSERSTACK_ACCESS_KEY")
URL = "https://{}:{}@hub.browserstack.com/wd/hub".format(
    BROWSERSTACK_USERNAME, BROWSERSTACK_ACCESS_KEY)

# # Creates an instance of Local
# bs_local = Local()

# # You can also set an environment variable - "BROWSERSTACK_ACCESS_KEY".
# bs_local_args = {"key": BROWSERSTACK_ACCESS_KEY}

# # Starts the Local instance with the required arguments
# bs_local.start(**bs_local_args)

# # Check if BrowserStack local instance is running
# print("Local binary connected: ", bs_local.isRunning())

desired_cap = {
    "os": "OS X",
    "osVersion": "Sierra",
    "buildName": "browserstack-build-1",
    "sessionName": "BStack local python",
    "local": "false",
    "userName": BROWSERSTACK_USERNAME,
    "accessKey": BROWSERSTACK_ACCESS_KEY
}
desired_cap["source"] = "python:sample-main:v1.0"
options = ChromeOptions()
options.add_argument("--no-sandbox")
options.add_argument("--headless")
options.set_capability('bstack:options', desired_cap)
driver = webdriver.Remote(command_executor=URL, options=options)

driver.get("https://www.google.com")
print(driver.title)
driver.quit()