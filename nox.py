import time
from appium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
 
# 常量用大写表示
PLATFROM = "Android"
DEVIE_NAME = "127.0.0.1:62001"
APP_PACKAGE = "com.tencent.mm"
APP_ACTIVITY = ".ui.LauncherUI"
DEIVER_SERVER = "http://127.0.0.1:4723/wd/hub"
TIMROUT = 300
USERNAME = "账号"
PASSWORD = "密码"
 
FLICK_START_X = 300
FLICK_START_Y = 300
FLICK_DISTANCE = 700
 
 
class Moments(object):
    def __init__(self):
        """
        初始化操作
        """
        # 驱动配置操作
        self.desired_caps = {
            "platformName": PLATFROM,
            "deviceName": DEVIE_NAME,
            "appPackage": APP_PACKAGE,
            "appActivity": APP_ACTIVITY,
            "noReset": True # 这个很重要 True表示不删除相关信息，不写每一次都需要重新登录
        }
 
        self.driver = webdriver.Remote(DEIVER_SERVER, self.desired_caps)
        self.wait = WebDriverWait(self.driver, TIMROUT)
 
    def login(self):
        """
        登陆操作
        :return:
        """
 
        # 登陆操作
        login = self.wait.until(EC.presence_of_element_located((By.ID, "com.tencent.mm:id/d75")))
        login.click()
        time.sleep(3)
 
        # 手机号输入
        phone = self.wait.until(EC.presence_of_element_located((By.ID, "com.tencent.mm:id/hz")))
 
        phone.set_text(USERNAME)
        time.sleep(1)
 
        # 点击下一步
        next = self.wait.until(EC.presence_of_element_located((By.ID, "com.tencent.mm:id/alr")))
        next.click()
        time.sleep(3)
        # 输入密码
        password = self.wait.until(EC.presence_of_element_located((By.ID, "com.tencent.mm:id/hz")))
        password.set_text(PASSWORD)
        time.sleep(1)
 
        # 点击登陆
        submit = self.wait.until(EC.presence_of_element_located((By.ID, "com.tencent.mm:id/alr")))
        submit.click()
 
        # 解决提示 点击否
        submit = self.wait.until(EC.presence_of_element_located((By.ID, "com.tencent.mm:id/an2")))
        submit.click()
        time.sleep(10)
 
    def enter(self):
        # 发现
 
        tab = self.wait.until(
            EC.presence_of_all_elements_located((By.XPATH, '//*[@resource-id=\"com.tencent.mm:id/cdh\"]')))[2]
        tab.click()
        time.sleep(3)
 
        # 朋友圈页面
        tab = self.wait.until(
            EC.presence_of_all_elements_located((By.XPATH, """//*[@resource-id=\"com.tencent.mm:id/aaf\"]""")))[0]
        tab.click()
 
    def crawl(self):
        for i in range(100):
            # 向上滑动
            self.driver.swipe(FLICK_START_X, FLICK_START_Y + FLICK_DISTANCE, FLICK_START_X, FLICK_START_Y,200)
            print("滑动一次")
            time.sleep(1)
 
            # 解析
            items_list = self.wait.until(
                EC.presence_of_all_elements_located((By.XPATH, """//*[@resource-id=\"com.tencent.mm:id/dkb\"]""")))
            for item in items_list:
                try:
                    # 昵称
                    nick_name = item.find_element_by_id('com.tencent.mm:id/as6').get_attribute("text")
                    # 正文
                    content = item.find_element_by_id('com.tencent.mm:id/dkf').get_attribute("text")
 
                    # 时间
                    date = item.find_element_by_id('com.tencent.mm:id/dfw').get_attribute("text")
                    print(nick_name)
                    print(content)
                    print(date)
                except:
                    pass

duix = Moments()
# duix.login()
time.sleep(3)
duix.enter()
time.sleep(2)
duix.crawl()