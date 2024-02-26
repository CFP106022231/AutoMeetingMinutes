from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
from time import sleep

class MeetingAutomation:
    def __init__(self, driver):
        self.driver = driver

    def login_with_ID(self, ID, pwd):

        self.driver.get("https://igp.sen.edu.tw/")

        button = self.driver.find_element('xpath','//*[@id="home"]/div/div/span')
        button.click() # 點擊按鈕

        username_input = self.driver.find_element("name", "acc")
        password_input = self.driver.find_element("name", "pwd")
        captcha_input = self.driver.find_element("name", "code")

        # 輸入帳號、密碼、驗證碼
        username_input.send_keys(ID)
        password_input.send_keys(pwd)
        captcha_input.send_keys(input())

        captcha_input.send_keys(Keys.RETURN) # 模擬Enter鍵，提交表單


        element = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.LINK_TEXT, "IGP檔案撰寫"))
        )
        element.click()
        
    def login_with_cookies(self, cookies_file):

        self.driver.get("https://igp.sen.edu.tw/igp/main/igpstudentlist/233")

        with open(cookies_file) as f:
            cookies_data = json.load(f)

        for cookie in cookies_data:
            self.driver.add_cookie(cookie)

    def login(self, cookies_file, ID, pwd):

        try:
            self.login_with_cookies(cookies_file)
        except:
            self.login_with_ID(ID, pwd)
    
    def read_meeting_map(self, file_path):
        meeting_map = {}
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                name, title = line.strip().split(' ')
                meeting_map[name] = title
        return meeting_map

    def add_meeting(self,meetingName, date, nameID):

        # 找到新增會議記錄按鈕
        add_meeting_button_xpath = "(//button[contains(text(), '新增會議記錄')])"
        add_meeting_button = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, add_meeting_button_xpath))
        )
        add_meeting_button.click()

        # 輸入日期
        date_input = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.NAME, "recordtime"))
        )
        date_input.clear()
        date_input.send_keys(date)

        # 找到特定 value 的 checkbox

        if meetingName in ["IGP會議", "課程安排", "師資安排", "安置評估"]:
            value_to_find = meetingName
        else:
            value_to_find = "其他_"
            
        checkbox_xpath = f'//input[@type="checkbox" and @value="{value_to_find}"]'
        checkbox = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, checkbox_xpath))
        )
        # 判斷 checkbox 是否已被勾選
        if not checkbox.is_selected():
            # 如果尚未勾選，則進行勾選
            checkbox.click()
            # 填寫會議名稱
        if value_to_find == "其他_":
            meeting_name_input = driver.find_element(By.XPATH, "//input[@type='text']") 
            meeting_name_input.send_keys(meetingName)

        # 新增與會人員
        new_person = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "btn.btn-s.table-btn-full"))
        )

        for name, title in nameID.items():
            new_person.click()
            self.driver.implicitly_wait(2)
            name_inputs = self.driver.find_elements(By.XPATH, "//input[@type='text']")
            name_inputs[-2].send_keys(name)
            name_inputs[-1].send_keys(title)

        xpath = "(//button[contains(text(), '新增')])"
        final = self.driver.find_elements(By.XPATH, xpath)

        final[2].click()

        sleep(3)

    def automate_meetings_for_students(self, student_ids, nameID):
        for student_id in student_ids:
            self.driver.get(f"https://my-link/{student_id}/meetings")
            # 添加兩個不同日期的會議
            # self.add_meeting("IGP會議", "002023/08/31", nameID)
            # self.add_meeting("IGP會議", "002023/12/15", nameID)
            self.add_meeting("特推會", "002023/11/23", nameID)
            
if __name__ == "__main__":
    # 創建 WebDriver 實例
    driver = webdriver.Chrome()

    # 創建 MeetingAutomation 實例
    meeting_automation = MeetingAutomation(driver)

    # 登入
    meeting_automation.login("cookiesfile.json", "MyID", "Mypwd")
    
    meeting_automation.driver.get("https://my link")

    # 學生編號和參與會議名單
    student_ids = [str(i) for i in range(14136, 14137)] #網頁中的學生編號
    nameID = meeting_automation.read_meeting_map('others.txt')#替換成參與會議名單

    # 自動化會議
    meeting_automation.automate_meetings_for_students(student_ids, nameID)

    print("輸入完成！")
    driver.quit() # 關閉瀏覽器
