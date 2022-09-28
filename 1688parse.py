from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
import time
import os
import logging
import sys
import random
from datetime import datetime
import requests


def parse(url):

    print("\n  目標網址:   " + url)
    
    # 日誌設定
    dev_logger: logging.Logger = logging.getLogger(name='dev')
    dev_logger.setLevel(logging.INFO)
    handler_file: logging.StreamHandler = logging.FileHandler('logfile.log', encoding='utf-8')
    dev_logger.addHandler(handler_file)


    # selenium 瀏覽器選項配置
    s = Service(r"C:\Program Files\Google\Chrome\Application\chromedriver.exe")
    chrome_options = Options()
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("detach", True)
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_experimental_option("prefs", {"profile.password_manager_enabled": False, "credentials_enable_service": False})
    chrome_options.use_chromium = True

    # 初始化 webdriver
    browser = webdriver.Chrome(options=chrome_options, service=s)
    browser.maximize_window()


    # 紀錄日誌
    timeString = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    dev_logger.info("[INFO] " + url + " " + timeString)

    # 取得網頁內容
    browser.get(url)

    time.sleep(4)
    
    ###  是否進到驗證頁面
    try:
        # 定位
        captcha_location = browser.find_element(By.CLASS_NAME, 'warnning-text')

        # 做滑鼠操作
        actions = ActionChains(browser)
        actions.click(captcha_location)
        actions.move_by_offset(-120, 100).perform() 
        actions.click_and_hold()
        for i in range(5):
            actions.move_by_offset(xoffset=10, yoffset=0).perform()
            time.sleep(0.08)
        for i in range(5):
            actions.move_by_offset(xoffset=54, yoffset=0).perform()
            time.sleep(0.01)
        actions.release()

    except NoSuchElementException as e:
        timeString = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        dev_logger.info("[WARNING] " + "未進入驗證頁面 " + timeString)
        pass
        

    time.sleep(3)
    browser.current_window_handle
    

    #############################################
    #### 如驗證失敗，則關閉瀏覽器，使用者須重新啟動
    title = browser.title
    if title == '驗證碼攔截':
        time.sleep(1)
        print("\n\n--------     驗證失敗，待數秒後請重新操作。     --------\n\n")
        timeString = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        dev_logger.info("[FAIL] " + "驗證失敗 " + timeString)
        browser.close()    
        return
    ##############################################


    dev_logger.info("[INFO] " + title + " " + timeString)

    # 捲動頁面，讓第二區塊凸顯示出來
    actions = ActionChains(browser)
    for i in range(17):
        actions.key_down(Keys.PAGE_DOWN).key_up(Keys.PAGE_DOWN).perform()
        time.sleep(random.uniform(0.4, 1))


    # 建立 images 資料夾
    if not os.path.exists("images"):
        os.mkdir("images")


    # 第一區圖片
    target_class_1 = browser.find_elements(By.CLASS_NAME, 'detail-gallery-img') # img class
    
    # 第二區圖片
    target_class_2 = browser.find_elements(By.CLASS_NAME, 'desc-img-loaded') # img class


    if len(target_class_1) or len(target_class_2) > 0:

        # 建立該次下載資料夾
        folder = title[:8] + str(int(datetime.now().timestamp()))
        if not os.path.exists("images\\" + folder):
            os.mkdir("images\\" + folder)

        print("\n--------     開始下載。     --------\n")


    index = 0
    for target in target_class_1:
        # 下載圖片
        link = target.get_attribute("src")
        img = requests.get(link)
        print(link)
        with open(f"images\\{folder}\\" + "1_" + str(index+1) + ".jpg", "wb") as file:  # 開啟資料夾及命名圖片檔
            file.write(img.content)  # 寫入圖片的二進位碼
        index += 1
        timeString = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    dev_logger.info("[SUCCESS] " + f"第一區共下載 {index} 個檔案 " + timeString)


    index_2 = 0
    for target in target_class_2:
        # 下載圖片
        link = target.get_attribute("src")
        img = requests.get(link)
        print(link)
        with open(f"images\\{folder}\\" + "2_" + str(index_2 + 1) + ".jpg", "wb") as file:  # 開啟資料夾及命名圖片檔
            file.write(img.content)  # 寫入圖片的二進位碼
        index_2 += 1
        timeString = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    dev_logger.info("[SUCCESS] " + f"第二區共下載 {index_2} 個檔案 " + timeString)



    browser.quit()
    print("\n\n下載成功。\n\n")




def main():
    
    if len(sys.argv) > 1:
        url = sys.argv[1]
        parse(url)
    else:
        print("\n ***** WARNING ! ***** 請在空格後貼上欲爬蟲網址。")



if __name__ == '__main__':
    main()