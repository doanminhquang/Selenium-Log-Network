import time
import json
from selenium import webdriver
from selenium.common import exceptions
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

# constants
URL_WEBSITE = "https://qlms.xyz/"
API_NAME = "server-qlms" 
Time_Sleep = 10

def log_filter(log_):
	return (
		log_["method"] == "Network.responseReceived"
		and "params" in log_.keys() 
		and "json" in log_["params"]["response"]["mimeType"]
	)

def process_browser_logs_for_network_events_and_write_to_file(logs_raw_):
	logs = [json.loads(lr["message"])["message"] for lr in logs_raw_]

	fristItem = True
	with open("network_log.json", "w", encoding="utf-8") as f:
		f.write("[")
		for log in filter(log_filter, logs):
			resp_url = log["params"]["response"]["url"]
			print(f"Caught {resp_url}")
			if API_NAME in resp_url:
				request_id = log["params"]["requestId"]
				try:
					resp_body = driver.execute_cdp_cmd("Network.getResponseBody", {"requestId": request_id})
					dic_data = {"url": resp_url, "body": json.loads(resp_body['body'])}
					if fristItem:
						write_data = json.dumps(dic_data, ensure_ascii=False)
						fristItem = False
					else:
						write_data = ","+json.dumps(dic_data, ensure_ascii=False)
					f.write(write_data)
				except exceptions.WebDriverException:
					print('response.body is null or pending')
		f.write("]")
  
if __name__ == "__main__":
	# Config Chrome
	desired_capabilities = DesiredCapabilities.CHROME
	desired_capabilities["goog:loggingPrefs"] = {"performance": "ALL","browser": "ALL"}
	options = webdriver.ChromeOptions()
	### Ẩn giao diện Chrome ###
	options.add_argument('headless')
	options.add_argument("--ignore-certificate-errors")
    
	driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options = options, desired_capabilities=desired_capabilities) 

	driver.get(URL_WEBSITE)
    
	time.sleep(Time_Sleep)
	
	try:
		myElem = WebDriverWait(driver, Time_Sleep).until(EC.presence_of_element_located((By.CLASS_NAME, 'active')))
		print("Element is ready!")
	except TimeoutException:
		print("Loading took too much time!")

	logs_raw = driver.get_log("performance")
	process_browser_logs_for_network_events_and_write_to_file(logs_raw)

	print("Quitting Selenium WebDriver")
	driver.quit()
