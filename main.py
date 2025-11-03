from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

app = Flask(__name__)

def find_first(driver, xpaths, wait_time=10):
    for xpath in xpaths:
        try:
            element = WebDriverWait(driver, wait_time).until(
                EC.presence_of_element_located((By.XPATH, xpath))
            )
            return element
        except Exception:
            continue
    return None

def js_click(driver, element):
    try:
        driver.execute_script("arguments[0].click();", element)
    except Exception:
        pass

def click_services_and_rc_related(driver):
    services_dropdown = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//a[contains(@class,'nav-link dropdown-toggle') and normalize-space(text())='Services']"))
    )
    services_dropdown.click()
    rc_related_services_dropdown = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//a[contains(@class,'dropdown-item') and normalize-space(text())='RC Related Services']"))
    )
    rc_related_services_dropdown.click()
    schedule_renewal_option = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//a[@id='fitbalcTest' and normalize-space(text())='Re-Schedule Renewal of Fitness Application']"))
    )
    schedule_renewal_option.click()

def enter_registration_and_chassis(driver, registration_number, chassis_number):
    reg_field = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "balanceFeesFine:tf_reg_no"))
    )
    reg_field.clear()
    reg_field.send_keys(registration_number)
    chassis_field = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "balanceFeesFine:tf_chasis_no"))
    )
    chassis_field.clear()
    chassis_field.send_keys(chassis_number)
    validate_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//span[normalize-space(text())='Validate Details']"))
    )
    validate_button.click()

def get_mobile_number(driver):
    mobile_number_field = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "balanceFeesFine:tf_mobile"))
    )
    return mobile_number_field.get_attribute("value")

def click_proceed_button_in_dialog(driver):
    dlg = find_first(driver, [
        "//div[contains(@class,'ui-dialog') and contains(@style,'display') and not(contains(@style,'display: none'))]",
        "//div[contains(@class,'modal') and contains(@class,'show')]",
        "//div[contains(@class,'modal') and contains(@style,'display: block')]",
    ])
    if dlg:
        btn = find_first(dlg, [
            ".//button[normalize-space(.)='Proceed']",
            ".//a[normalize-space(.)='Proceed']",
            ".//span[normalize-space(.)='Proceed']/ancestor::button[1]",
            ".//button[contains(@class,'btn') and contains(.,'Proceed')]",
            ".//button[contains(@class,'ui-button') and .//span[normalize-space(.)='Proceed']]",
        ])
        if btn:
            try:
                btn.click()
                time.sleep(0.8)
                return True
            except Exception:
                js_click(driver, btn)
                time.sleep(0.8)
                return True
    return False

def create_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.binary_location = "/usr/bin/google-chrome"
    service = Service("/usr/local/bin/chromedriver")
    return webdriver.Chrome(service=service, options=chrome_options)

def process_vahan_request(registration_number, chassis_number):
    driver = create_driver()
    try:
        driver.get("https://vahan.parivahan.gov.in/vahanservice/vahan/ui/statevalidation/homepage.xhtml?statecd=Mzc2MzM2MzAzNjY0MzIzODM3NjIzNjY0MzY2MjM3NDQ0Yw==")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "fit_c_office_to_label")))

        try:
            close_popup_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.CLASS_NAME, "btn-close"))
            )
            close_popup_button.click()
        except:
            pass

        select_rto = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "fit_c_office_to_label"))
        )
        select_rto.click()
        rto_option = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//li[contains(text(),'LONI ROAD (DL5)')]"))
        )
        rto_option.click()
        checkbox_icon = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//span[@class='ui-chkbox-icon ui-icon ui-icon-blank ui-c']"))
        )
        checkbox_icon.click()
        proceed_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "proccedHomeButtonId"))
        )
        proceed_button.click()
        click_proceed_button_in_dialog(driver)
        click_services_and_rc_related(driver)
        enter_registration_and_chassis(driver, registration_number, chassis_number)
        mobile_number = get_mobile_number(driver)
        return {"status": "success", "mobile_number": mobile_number}
    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        driver.quit()

@app.route("/vahan", methods=["GET"])
def vahan_api():
    reg = request.args.get("reg")
    chassis = request.args.get("chassis")

    if not reg or not chassis:
        return jsonify({"status": "error", "message": "Missing 'reg' or 'chassis' parameter"}), 400

    result = process_vahan_request(reg, chassis)
    return jsonify(result)

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
