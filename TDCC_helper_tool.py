#!/usr/bin/env python
# coding: utf-8
# author: DavidChou
# repository: https://github.com/DavidChou23/TDCC_evote_helper
# date: 2025/7/19

debug=0
from selenium import webdriver
# from selenium.webdriver.edge.service import Service --> import later, in case
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.firefox.service import Service
import subprocess
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.action_chains import ActionChains
import time
import datetime
import os
import sys
import argparse
import threading
import random
no_confirm= False
args = None
os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--log-level=3"

def short_exception_message(e: Exception) -> str:
    msg = str(e).strip()
    if not msg:
        return e.__class__.__name__
    first_line = msg.splitlines()[0].strip()
    if first_line.startswith("Message:"):
        first_line = first_line[len("Message:"):].strip()
    return first_line

def parse_args():
    parser = argparse.ArgumentParser(description="TDCC 電子投票與截圖輔助工具")

    # Optional flag argument (True if used, False otherwise)
    parser.add_argument(
        "-y",
        "--yes",
        action="store_true",
        help="啟用免確認模式，直接套用現有設定檔（y/n）"
    )

    # Optional argument with value
    parser.add_argument(
        "-d",
        "--driver_path",
        metavar="driver_path",
        type=str,
        help="指定自訂瀏覽器 Driver 執行檔路徑"
    )
    # Optional browser flags, none or one of [Edge, Chrome, Firefox]
     
    parser.add_argument(
        "-b",
        "--browser",
        metavar="browser",
        type=str,
        choices=["Edge", "Chrome", "Firefox"],
        help="指定要使用的瀏覽器：[Edge, Chrome, Firefox]"
    )
    args = parser.parse_args()
    # args.yes = True
    # args.browser = "Firefox"  # default browser
    return args

def open_browser():
    global args
    # launch a webdriver
    browser = None
    try:
        # check if the driver path exists and executable
        if args.driver_path:  # if user provided a custom driver path
            if os.path.exists(args.driver_path) and os.access(args.driver_path, os.X_OK):
                # determine which browser driver to use by subprocess driver --help
                result = subprocess.run([args.driver_path, '--help'], capture_output=True, text=True)
                if result.returncode == 0:
                    if 'Chrome' in result.stdout:
                        print("使用 Chrome Driver")
                        from selenium.webdriver.chrome.service import Service
                        service = Service(args.driver_path)
                        browser = webdriver.Chrome(service=service)
                    elif 'msedge' in result.stdout:
                        print("使用 Edge Driver")
                        from selenium.webdriver.edge.service import Service
                        service = Service(args.driver_path)
                        browser = webdriver.Edge(service=service)
                    elif 'Firefox' in result.stdout:
                        print("使用 Firefox Driver")
                        from selenium.webdriver.firefox.service import Service
                        service = Service(args.driver_path)
                        browser = webdriver.Firefox(service=service)
                    else:
                        print("無法辨識的瀏覽器 Driver")
                        raise FileNotFoundError("Unknown browser driver")
                else:
                    print("無法判斷瀏覽器 Driver 類型")
                    raise FileNotFoundError("Failed to determine browser driver")
                
                print(f"使用自訂 Driver 路徑：{args.driver_path}")

            else:
                #print to stdout
                print(f"自訂 Driver 路徑 {args.driver_path} 不存在或不可執行，將改用預設方式啟動瀏覽器。")
                #print to stderr
                print("自訂 Driver 路徑不存在或不可執行，改用預設 Driver 路徑。", file=sys.stderr)
                raise FileNotFoundError(f"Custom driver path {args.driver_path} does not exist or is not executable.")
        else: # user did not provide a custom driver path
            # if user provided a browser flag
            if args.browser == "Edge":
                print("使用 Edge WebDriver")
                browser = webdriver.Edge()
            elif args.browser == "Chrome":
                print("使用 Chrome WebDriver")
                browser = webdriver.Chrome()
            elif args.browser == "Firefox":
                print("使用 Firefox WebDriver")
                browser = webdriver.Firefox()
            else: # no browser flag provided
                raise FileNotFoundError("No custom driver path provided and no browser flag provided. Falling back to default.")
        
    except Exception as e:
        # let webdriver auto download and maintain the driver
        try:
            # Edge
            print("正在嘗試初始化 Edge WebDriver...")
            browser = webdriver.Edge()
        except Exception as e:
            print(f"初始化 Edge WebDriver 失敗：{e}")
            try:
                # Chrome
                print("正在嘗試初始化 Chrome WebDriver...")
                browser = webdriver.Chrome()
            except Exception as e:
                print(f"初始化 Chrome WebDriver 失敗：{e}")
                try:
                    # Firefox
                    print("正在嘗試初始化 Firefox WebDriver...")
                    browser = webdriver.Firefox()
                except Exception as e:
                    print(f"初始化 Firefox WebDriver 失敗：{e}")
                    sys.exit(1)
    if browser is None:
        raise AssertionError("Browser initialization failed, please check your driver path or browser flag.")
    print("WebDriver 初始化成功。")
    return browser

if __name__ == "__main__":
    args = parse_args()
    if args.yes:  # for schedule task, use exist config file
        no_confirm = True
        print("已啟用免確認模式，將直接套用現有設定檔。")
    else:
        no_confirm = False
        print("未啟用免確認模式，執行時會詢問是否套用設定檔。")

# cd to the directory of the script
def get_executable_dir():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)  # For PyInstaller
    else:
        return os.path.dirname(os.path.abspath(__file__))

# print pwd
# print("current working directory: ", os.getcwd())
os.chdir(get_executable_dir())
print("目前工作目錄：", os.getcwd())


# WARNING
print("###############  TDCC 股東投票輔助工具  ###############")
print("版本：2025.7.19")
print("作者：DavidChou")
print("中文化：LukeLai")
print("專案網址：https://github.com/DavidChou23/TDCC_evote_helper")
print("本程式僅用於協助股東提前完成投票流程。")
print("投票內容可隨時修改，不影響股東實際投票意願。")
print("使用本程式所造成的任何後果，程式作者概不負責。")
print("##########################################################")

# generate statement html
with open('./statement.html', 'w', encoding='utf-8') as f:
    f.write('''
<!DOCTYPE html>
<html lang="zh-Hant">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TDCC 股東投票輔助工具</title>
</head>
<body>
    <h1>TDCC 股東投票輔助工具</h1>
    <p>版本：2025.7.19</p>
    <p>作者：DavidChou</p>
    <p>中文化：LukeLai</p>
    <p>專案網址：<a href="https://github.com/DavidChou23/TDCC_evote_helper">https://github.com/DavidChou23/TDCC_evote_helper</a></p>
    <p>本程式僅用於協助股東提前完成投票流程。</p>
    <p>投票內容可隨時修改，不會影響股東實際投票意願。</p>
    <p>使用本程式所產生的任何結果或後果，程式作者概不負責。</p>
    <!-- <p>For more information, please visit <a href="">your website link here</a></p> -->
    <br>
    <p><strong>請在命令視窗中輸入指令。投票內容可隨時修改，不會影響股東實際投票意願。</strong></p>
</body>
</html>
    ''')

def id_check(id_number:str) -> int:
    """
    check if the id_number is a valid Taiwan ID number.
    :param id_number: Taiwan ID number
    :return: 0: valid, 1: invalid format, 2: invalid check digit
    """
    import  re
    # check ID number length
    if len(id_number) != 10:
        return 1

    # check format
    if not re.match(r'^[A-Z][12]\d{8}$', id_number):
        return 1

    # 計算檢查碼
    check_digit = int(id_number[9])
    map_table={'A':1,'B':0,'C':9,'D':8,'E':7,'F':6,'G':5,'H':4,'I':9,'J':3,'K':2,'L':2,'M':1,'N':0,'O':8,'P':9,'Q':8,'R':7,'S':6,'T':5,'U':4,'V':3,'W':1,'X':3,'Y':2,'Z':0} #from wiki
    total = map_table[id_number[0]] * 1
    for i in range(1, 9):
        total += int(id_number[i]) * (9 - i)
    total %= 10
    calculated_check_digit = (10 - total) % 10

    if check_digit != calculated_check_digit:
        return 2

    return 0

#要固定顯示的字 秒數 結束後要顯示的字
def show_msg_on_driver(txt1, timeout_second, txt2)-> None:
    try:
        # 1. **插入倒數計時的 HTML 元素**
        countdown_script = """
        var countdownDiv = document.createElement('div');
        countdownDiv.id = 'selenium-countdown';
        countdownDiv.style.position = 'fixed';
        countdownDiv.style.top = '15px';
        countdownDiv.style.left = '10px';
        countdownDiv.style.padding = '10px';
        countdownDiv.style.backgroundColor = 'rgba(0, 0, 0, 0.7)';
        countdownDiv.style.color = 'white';
        countdownDiv.style.fontSize = '16px';
        countdownDiv.style.borderRadius = '5px';
        countdownDiv.style.zIndex = '9999';
        document.body.appendChild(countdownDiv);
        """

        driver.execute_script(countdown_script)  # 執行 JavaScript 來插入倒數計時 UI

        # 2. **開始倒數計時**
        wait_time = timeout_second  # 設定等待時間 (秒)
        if wait_time==0:
            driver.execute_script(f"document.getElementById('selenium-countdown').innerText = '{txt1}';")
            time.sleep(5)
        else:
            for i in range(wait_time, 0, -1):
                driver.execute_script(f"document.getElementById('selenium-countdown').innerText = '{txt1} 剩餘時間: {i} 秒';")
                time.sleep(1)

        # 3. **結束倒數後顯示完成訊息**
        driver.execute_script(f"document.getElementById('selenium-countdown').innerText = '{txt2}';")

        # 保持頁面開啟一點時間，讓使用者看到完成訊息
        time.sleep(2)

        # 移除倒數計時 UI (可選)
        driver.execute_script("document.getElementById('selenium-countdown').remove();")
    except:
        pass
    
def getdatetime()-> str:
    now_year=str(int(datetime.datetime.now().strftime("%Y"))-1911)
    now_date=datetime.datetime.now().strftime("/%m/%d %H:%M:%S")
    return now_year+now_date

def click_element(element: webdriver.remote.webelement.WebElement) -> None:
    """
    1. use while loop to wait for the element to be clickable
    2. use action chain to move to the element and click it, in order to increase score of captcha
    3. add random sleep and random offset when moving to the element for preventing detection
    """
    max_attempts = 5
    attempts = 0
    while True:
        try:
            # move to the element
            action = ActionChains(driver)
            # random offset and random sleep
            for _ in range(3):
                time.sleep(random.uniform(0.1, 0.2))
                # random offset
                offset_x = random.randint(-5, 5)
                offset_y = random.randint(-5, 5)
                action.move_by_offset(offset_x, offset_y)
            action.move_to_element_with_offset(element, offset_x, offset_y).perform()
            time.sleep(0.2)
            # click the element
            element.click()
            break
        except Exception as e:
            if(attempts>=max_attempts):
                print("點擊元素時發生錯誤：", e)
                break
            else:
                print("點擊元素時發生錯誤：", e)
                print("正在重試...")
                attempts += 1
                time.sleep(0.5)
                continue
            time.sleep(1)

def logout() -> None:
    global driver
    # logout
    driver.get("https://stockservices.tdcc.com.tw/evote/logout.html")
    time.sleep(2*time_speed)
    print("登出成功")

def autoLogin(user_ID):
    global driver
    print("正在嘗試登入：", user_ID)
    # logout to ensure clear the session
    driver.get("https://stockservices.tdcc.com.tw/evote/logout.html")
    time.sleep(2*time_speed)
    driver.set_window_position(20, 20)
    driver.set_window_size(1000, 1000)
    # login page
    driver.get("https://stockservices.tdcc.com.tw/evote/login/shareholder.html")
    driver.find_element(By.NAME,"pageIdNo").send_keys(user_ID)
    time.sleep(1*time_speed)
    driver.find_element(By.NAME,"caType").send_keys("券商網路下單憑證")
    time.sleep(1*time_speed)
    driver.find_element(By.ID,'loginBtn').click()
    # click_element(driver.find_element(By.ID,'loginBtn'))
    print("正在登入，請稍候...（通常需要 10 到 60 秒）")
    
    ######################################################################
    # how long to wait for the login page to load
    ######################################################################
    # time.sleep(3*time_speed)
    time.sleep(5)

    try:
        driver.find_element(By.ID,"comfirmDialog_okBtn").click()
        # click_element(driver.find_element(By.ID,"comfirmDialog_okBtn"))
        time.sleep(5*time_speed)
    except:
        pass
    # thd=threading.Thread(target = show_msg_on_driver, args=("登入中請稍等·····", 20, "登入中請稍等·····"))
    # thd.start()
    # time.sleep(10)
    # thd=threading.Thread(target = show_msg_on_driver, args=("登入中請稍等·····", 10, "登入中請稍等·····"))
    # thd.start()
    # time.sleep(11)
    ######################################################################
    ######################################################################
    while(True):
        time.sleep(1)
        try:
            #我同意上列條款
            #if driver.find_element(By.CSS_SELECTOR,'a[class="btnAgree btn-style btn-b btn-lg"]'):
            if driver.find_element(By.CSS_SELECTOR,'a[class="btnAgree btn-style btn-b btn-lg"]'):
                thd=threading.Thread(target = show_msg_on_driver, args=("請閱讀條款·····", 0, "請閱讀條款·····"))
                thd.start()
                time.sleep(5)
                driver.find_element(By.CSS_SELECTOR,'a[class="btnAgree btn-style btn-b btn-lg"]').click()
                # click_element(driver.find_element(By.CSS_SELECTOR,'a[class="btnAgree btn-style btn-b btn-lg"]'))
                time.sleep(5*time_speed)
        except:
            pass
        try:
            #我同意上列條款
            if driver.find_elements(By.NAME,'btn1'):
                thd=threading.Thread(target = show_msg_on_driver, args=("請閱讀條款·····", 0, "請閱讀條款·····"))
                thd.start()
                time.sleep(5)
                driver.find_element(By.NAME,'btn1').click()
                # click_element(driver.find_element(By.NAME,'btn1'))
                time.sleep(5*time_speed)
        except:
            pass
        try:
            for element in driver.find_elements(By.CSS_SELECTOR,'div[id="tabs1"]'):
                driver.execute_script("arguments[0].setAttribute('class','tabs-block block color-b shadow show active')", element)
            for g in driver.find_elements(By.CSS_SELECTOR,'a[onclick="go();"]'):
                try:
                    g.click()
                    # click_element(g)
                except:
                    continue
            time.sleep(2*time_speed)
        except:
            pass

        try:
            driver.find_element(By.ID,"comfirmDialog_okBtn").click()
            # click_element(driver.find_element(By.ID,"comfirmDialog_okBtn"))
            time.sleep(5*time_speed)
        except:
            pass
        
        # get body's text
        if driver.find_element(By.TAG_NAME,'body').text.find("系統維護中") != -1:
            # time between 00:00~7:00
            if datetime.datetime.now().hour < 7:
                print("系統維護中，請於 7:00~24:00 之間進行投票。")
                print("按 Enter 鍵結束程式")
                input()
                logout()
                driver.quit()
                sys.exit()
            # time between 7:00~24:00
            else:
                print("系統維護中，請稍後再試")
                print(driver.find_element(By.TAG_NAME,'body').text)
                # show msg on driver and block for 5 minutes
                thd=threading.Thread(target = show_msg_on_driver, args=("系統維護中，請稍後再試", 300, "系統維護中，請稍後再試"))
                thd.start()
                time.sleep(300)
                # wait for 5 minutes
                continue
        
        if "login/shareholder" in driver.current_url:
            print("登入尚未完成，5 秒後再試一次")
            time.sleep(5)
            continue
        time.sleep(time_speed*3)
        driver.get("https://stockservices.tdcc.com.tw/evote/shareholder/000/tc_estock_welshas.html")
        time.sleep(5*time_speed)
        while(True):
            try:
                if(driver.find_element(By.NAME,'qryStockId') != None):
                    return
            except:
                time.sleep(1)
                continue
        
        

# wait for review
def voting():
    global default_vote, manual_vote, accept_list, opposite_list, abstain_list
    while(True):
        time.sleep(1) # slower but reduce possibility to be detected as robot
        #### 投票已完成，回清單
        if "投票已完成" in driver.find_element(By.TAG_NAME,'table').text:
            #print("投票已完成")
            time.sleep(3*time_speed)
            driver.find_element(By.CSS_SELECTOR,'button[onclick="doProcess();"]').click()
            # click_element(driver.find_element(By.CSS_SELECTOR,'button[onclick="doProcess();"]'))
            break


        #### 投票選項
        match default_vote:
            case "accept":
                #while(True):
                    try:
                        #全部贊成 #有空格
                        driver.find_element(By.CSS_SELECTOR,'table.c-votelist_docSection tr:nth-child(2) td:nth-child(2) a:nth-child(1)').click()
                        # click_element(driver.find_element(By.CSS_SELECTOR,'table.c-votelist_docSection tr:nth-child(2) td:nth-child(2) a:nth-child(1)'))
                        time.sleep(2*time_speed)
                        #break
                    except Exception as e:
                        #print("error: ",e)
                        #continue
                        pass
            case "opposite":
                #while(True):
                    try:
                        #全部反對 #有空格
                        driver.find_element(By.CSS_SELECTOR,'table.c-votelist_docSection tr:nth-child(2) td:nth-child(2) a:nth-child(2)').click()
                        # click_element(driver.find_element(By.CSS_SELECTOR,'table.c-votelist_docSection tr:nth-child(2) td:nth-child(2) a:nth-child(2)'))
                        time.sleep(2*time_speed)
                        #break
                    except Exception as e:
                        #print("error: ",e)
                        #continue
                        pass
            case "abstain":
                #while(True):
                    try:
                        #全部棄權 #有空格
                        driver.find_element(By.CSS_SELECTOR,'table.c-votelist_docSection tr:nth-child(2) td:nth-child(2) a:nth-child(3)').click()
                        # click_element(driver.find_element(By.CSS_SELECTOR,'table.c-votelist_docSection tr:nth-child(2) td:nth-child(2) a:nth-child(3)'))
                        time.sleep(2*time_speed)
                        #break
                    except Exception as e:
                        #print("error: ",e)
                        #continue
                        pass
        try:
            #driver.find_elements(By.XPATH,'//table[@class="o-table--card c-cardTable c-motionlist"]/tbody/tr')
            driver.find_elements(By.XPATH,'//td/input[@type="radio"]/../..')
            if manual_vote==True:
                # select all rows of vote
                ## for all /html/body/div[1]/form/table[3]/tbody/tr which has input in their children
                for i in driver.find_elements(By.XPATH,'//td/input[@type="radio"]/../..'):
                    #print(i.text)
                    if len(i.find_elements(By.TAG_NAME,'input'))==0: # not a vote
                        continue

                    print(i.find_elements(By.TAG_NAME,'td')[0].text) # statement
                    statement=i.find_elements(By.TAG_NAME,'td')[0].text
                    # if keyword in statement:
                    try:
                        if any(keyword in statement for keyword in accept_list): # accept
                            #print("accept")
                            i.find_element(By.CSS_SELECTOR,'input[value="A"]').click()
                            # click_element(i.find_element(By.CSS_SELECTOR,'input[value="A"]'))
                            print("--> 贊成")
                            time.sleep(0.5*time_speed)
                        elif any(keyword in statement for keyword in opposite_list): # opposite
                            #print("opposite")
                            i.find_element(By.CSS_SELECTOR,'input[value="O"]').click()
                            # click_element(i.find_element(By.CSS_SELECTOR,'input[value="O"]'))
                            print("--> 反對")
                            time.sleep(0.5*time_speed)
                        elif any(keyword in statement for keyword in abstain_list): # abstain
                            #print("abstain")
                            i.find_element(By.CSS_SELECTOR,'input[value="C"]').click()
                            # click_element(i.find_element(By.CSS_SELECTOR,'input[value="C"]'))
                            print("--> 棄權")
                            time.sleep(0.5*time_speed)
                    except Exception as e:
                        print("發生錯誤：",e)
                        continue
        except:
            pass

        #### 候選人投票
        try:
            #全部棄權(候選人投票)
            driver.find_element(By.CSS_SELECTOR,'a[href="javascript:giveUp();"]').click() #全部放棄
            # click_element(driver.find_element(By.CSS_SELECTOR,'a[href="javascript:giveUp();"]'))
            time.sleep(3*time_speed)
            #driver.find_element(By.CSS_SELECTOR,'button[onclick="voteObj.checkVote(); return false;"]').click() #下一步
            # click_element(driver.find_element(By.CSS_SELECTOR,'button[onclick="voteObj.checkVote(); return false;"]'))
            #time.sleep(3*time_speed)
            #driver.find_element(By.CSS_SELECTOR,'button[onclick="voteObj.ignoreVote();voteObj.goNext(); return false;"').click() #小視窗下一步
            # click_element(driver.find_element(By.CSS_SELECTOR,'button[onclick="voteObj.ignoreVote();voteObj.goNext(); return false;"]'))
            #time.sleep(3*time_speed)
        except:
            pass

        #### 下一步
        try:
            #下一步
            driver.find_element(By.CSS_SELECTOR,'button[onclick="voteObj.checkVote(); return false;"]').click()
            # click_element(driver.find_element(By.CSS_SELECTOR,'button[onclick="voteObj.checkVote(); return false;"]'))
            time.sleep(3*time_speed)
            continue
        except:
            pass

        #### 小視窗
        try:
            #小視窗下一步(棄權警告視窗1)
            driver.find_element(By.CSS_SELECTOR,'button[onclick="voteObj.ignoreVote();voteObj.goNext(); return false;"]').click()
            # click_element(driver.find_element(By.CSS_SELECTOR,'button[onclick="voteObj.ignoreVote();voteObj.goNext(); return false;"]'))
            time.sleep(3*time_speed)
        except:
            pass
        try:
            #小視窗下一步(棄權警告視窗2)
            driver.find_element(By.CSS_SELECTOR,'button[onclick="voteObj.ignoreVote();voteObj.goNext();return false;"]').click()
            # click_element(driver.find_element(By.CSS_SELECTOR,'button[onclick="voteObj.ignoreVote();voteObj.goNext();return false;"]'))
            time.sleep(3*time_speed)
        except:
            pass

        #### 確認投票
        try:
            #確認投票結果
            if driver.find_elements(By.CSS_SELECTOR,'button[onclick="voteObj.checkMeetingPartner(); return false;"]'):
                #thd=threading.Thread(target = show_msg_on_driver, args=("預投票結果如下，如需要修改，請回主頁點選修改", 10, "投票完成"))
                #thd.start()
                #time.sleep(10)
                time.sleep(3*time_speed)
                driver.find_element(By.CSS_SELECTOR,'button[onclick="voteObj.checkMeetingPartner(); return false;"]').click()
                # click_element(driver.find_element(By.CSS_SELECTOR,'button[onclick="voteObj.checkMeetingPartner(); return false;"]'))
                #time.sleep(6)
                time.sleep(3*time_speed)
        except:
            pass
        
        #### 系統異常處理
        try:
            #if "我不是機器人驗證失敗！" in driver.find_element(By.TAG_NAME,"form").text:
            if "我不是機器人驗證失敗！" in driver.find_element(By.TAG_NAME,"body").text:
                thd=threading.Thread(target = show_msg_on_driver, args=("請點選機器人驗證", 0, "請點選機器人驗證"))
                thd.start()
                time.sleep(5)
                driver.find_element(By.CSS_SELECTOR,'button[onclick="$.modal.close();return false;"]').click()
                # click_element(driver.find_element(By.CSS_SELECTOR,'button[onclick="$.modal.close();return false;"]'))
                thd=threading.Thread(target = show_msg_on_driver, args=("腳本等待中", 30, "等待結束"))
                thd.start()
                time.sleep(1)
                input("請先完成機器人驗證，再按 Enter 鍵繼續")
            
            if "系統操作逾時" in driver.find_element(By.TAG_NAME,"form").text:
                print("系統操作逾時，請關閉程式後重新開啟。")
                return
            
            if driver.find_element(By.TAG_NAME,'body').text.find("系統維護中") != -1:
                # time between 00:00~7:00
                if datetime.datetime.now().hour < 7:
                    print("系統維護中，請於 7:00~24:00 之間進行投票。")
                    print("按 Enter 鍵結束程式")
                    input()
                    logout()
                    driver.quit()
                    sys.exit()
                # time between 7:00~24:00
                else:
                    print("系統維護中，請稍後再試")
                    print(driver.find_element(By.TAG_NAME,'body').text)
                    # show msg on driver and block for 5 minutes
                    thd=threading.Thread(target = show_msg_on_driver, args=("系統維護中，請稍後再試", 300, "系統維護中，請稍後再試"))
                    thd.start()
                    time.sleep(300)
                    # wait for 5 minutes
                    continue
        except:
            pass
    return

def autovote(user_ID):
    """
    Returns: 0 for success, 1 for error
    """
    global driver, voteinfolist
    try:
        driver.get("https://stockservices.tdcc.com.tw/evote/shareholder/000/tc_estock_welshas.html")
        time.sleep(2*time_speed)
        while(True):
            try:
                driver.find_element(By.NAME,'qryStockId')
                break
            except:
                time.sleep(2*time_speed)
        print("------ 開始投票 ------")
        while(True):
            try:
                if "未投票" in driver.find_elements(By.TAG_NAME,'tr')[1].text:
                    print(driver.find_elements(By.TAG_NAME,'tr')[1].text)
                    voteinfolist[user_ID].append(driver.find_elements(By.TAG_NAME,'tr')[1].text.split(" ")[0])
                    driver.find_elements(By.TAG_NAME,'tr')[1].find_elements(By.TAG_NAME,'td')[3].find_elements(By.TAG_NAME,'a')[0].click()
                    # click_element(driver.find_elements(By.TAG_NAME,'tr')[1].find_elements(By.TAG_NAME,'td')[3].find_elements(By.TAG_NAME,'a')[0])
                    time.sleep(1)
                    try:
                        driver.find_element(By.ID,"msgDialog_okBtn").click()
                        # click_element(driver.find_element(By.ID,"msgDialog_okBtn"))
                    except:
                        pass
                    time.sleep(2)
                    voting()
                    try:
                        if "系統操作逾時" in driver.find_element(By.TAG_NAME,"form").text:
                            print("系統操作逾時，請關閉程式後重新開啟。")
                            time.sleep(2)
                            continue
                        if "系統維護中" in driver.find_element(By.TAG_NAME,"form").text:
                            print("系統維護中，請待維護結束後再重新執行程式。")
                            time.sleep(2)
                            input("按 Enter 鍵結束程式...")
                            logout()
                            driver.quit()
                            sys.exit()
                    except:
                        pass
                    write_voteinfolist(voteinfolist)
                    time.sleep(2)
                else:
                    print("------ 投票完畢，共 " + str(len(voteinfolist[user_ID])) + " 筆 ------")
                    break
            except Exception as e:
                print(f"自動投票時發生錯誤：{e}")
                return 1
        return 0
    except Exception as e:
        print(f"自動投票失敗：{e}")
        return 1

# wait for review                    
def screenshot(user_id,info):
    """
    save screenshot to the appropriate directory based on screenshot_mode.
    info[0]: stock_id, info[1]: stock_name, info[2]: stock_account_id
    Returns: 0 for success, 1 for failure, 2 for skip
    """
    global base_path, screenshot_mode
    try:
        driver.execute_script("document.body.style.zoom = '120%'")
        body_text = driver.find_element(By.TAG_NAME, 'body').text
        has_egift_text = ("eGift" in body_text) or ("電子紀念品" in body_text) or ("領取資格" in body_text)
        if has_egift_text:
            driver.execute_script("document.body.style.zoom = '100%'")
            return 2
        # adjust the window size
        while(True):
            try:
                driver.find_element(By.CSS_SELECTOR,'div[class="u-width--100 u-t_align--right"]')
                break
            except:
                time.sleep(1)
                continue
        votedate_pic = driver.find_element(By.CSS_SELECTOR,'div[class="u-width--100 u-t_align--right"]')
        driver.set_window_size(516, votedate_pic.location['y']+votedate_pic.size['height']+370)
        # scroll to the top of the page
        for _ in range(5):
            js="var q=document.documentElement.scrollTop=0"
            driver.execute_script(js) 

        if screenshot_mode == 1:
            if not os.path.exists(base_path+str(user_id)):
                os.makedirs(base_path+str(user_id))
            driver.save_screenshot(base_path+str(user_id)+"/"+ info[0] +"_"+ info[1].replace("*","") +".png")
        elif screenshot_mode == 2:
            if not os.path.exists(base_path):
                os.makedirs(base_path)
            stock_account_id = info[2]
            filename = f"{info[0]}_{info[1].replace('*','')}_{stock_account_id}.png"
            driver.save_screenshot(base_path +"/all/"+ filename)
        elif screenshot_mode == 3:
            if not os.path.exists(base_path):
                os.makedirs(base_path)
            filename = f"{info[0]}_{info[1].replace('*','')}_{user_id}.png"
            driver.save_screenshot(base_path+"/all/" + filename)
        driver.execute_script("document.body.style.zoom = '100%'")
        return 0
    except Exception as e:
        print(f"截圖失敗：{short_exception_message(e)}")
        return 1

def auto_screenshot(user_id, stock_id):
    """
    take screenshot of the stock_id
    bring driver to correct page
    Returns: 0 for success, 1 for failure, 2 for not found
    """
    global driver, voteinfolist, screenshot_mode
    try:
        driver.get("https://stockservices.tdcc.com.tw/evote/shareholder/000/tc_estock_welshas.html")
        time.sleep(2*time_speed)
        while(True):
            try:
                driver.find_element(By.NAME,'qryStockId')
                break
            except:
                time.sleep(2*time_speed)
        # search stock_id
        time.sleep(1*time_speed)
        driver.find_element(By.NAME,'qryStockId').clear()
        time.sleep(0.5*time_speed)
        driver.find_element(By.NAME,'qryStockId').send_keys(stock_id)
        time.sleep(0.9*time_speed)
        driver.find_element(By.CSS_SELECTOR,'a[onclick="qryByStockId();"]').click()
        # click_element(driver.find_element(By.CSS_SELECTOR,'a[onclick="qryByStockId();"]'))
        time.sleep(0.9*time_speed)

        # stock_id, stock_name
        voteinfo = []
        while(True):
            try:
                voteinfo.extend(driver.find_elements(By.TAG_NAME,'tr')[1].text.split(" ")[0:2])
                break   
            except IndexError:
                time.sleep(2)
                
        # click search button(should be only one after search)
        for i in driver.find_elements(By.TAG_NAME,'tr'):
            if(debug>=5):
                print(i.text)
            if "修改" in i.text:
                i.find_elements(By.TAG_NAME,'td')[3].find_elements(By.TAG_NAME,'a')[1].click()
                # click_element(i.find_elements(By.TAG_NAME,'td')[3].find_elements(By.TAG_NAME,'a')[1])
                break
            elif "修改" not in i.text and "查詢" in i.text:
                tmp=0
                for j in i.find_elements(By.TAG_NAME,'td')[3].find_elements(By.TAG_NAME,'a'):
                    if "查詢" in j.text:
                        j.click()
                        # click_element(j)
                        tmp=1
                        break
                if tmp==1:
                    break
        else: 
            print("查無此股號的搜尋結果：", stock_id)
            return 2

        time.sleep(0.6*time_speed)
        try:
            driver.find_element(By.ID,"msgDialog_okBtn").click()
            # click_element(driver.find_element(By.ID,"msgDialog_okBtn"))
            time.sleep(0.6*time_speed)
        except Exception as e:
            pass
        time.sleep(1*time_speed)
        # 附加上 股東戶號
        try:
            # Try to get 戶號 from the table
            trs = driver.find_element(By.TAG_NAME,'tbody').find_elements(By.TAG_NAME,'tr')
            found = False
            for tr in trs:
                if "戶號" in tr.find_element(By.TAG_NAME,'th').text:
                    stock_account_id = tr.find_element(By.TAG_NAME,'td').text
                    voteinfo.append(stock_account_id)
                    found = True
                    break
                if found:
                    break
            if not found:
                voteinfo.append("unknown")
        except Exception as e:
            voteinfo.append("unknown")
        ret = screenshot(user_id, voteinfo)
        if ret == 0:
            try:
                voteinfolist[user_id].remove(stock_id)
                write_voteinfolist(voteinfolist)
                print(f"{voteinfo[0]} {voteinfo[1]} 截圖成功")
            except Exception as e:
                print(f"更新 voteinfolist 失敗：{e}")
                return 1
        elif ret == 2:
            try:
                voteinfolist[user_id].remove(stock_id)
                write_voteinfolist(voteinfolist)
                print(f"{voteinfo[0]} {voteinfo[1]} 偵測為 eGift 頁面，略過截圖")
            except Exception as e:
                print(f"更新 voteinfolist 失敗：{e}")
                return 1
        else:
            print(f"{voteinfo[0]} {voteinfo[1]} 截圖失敗")
            return 1
        #返回
        try:
            driver.execute_script("arguments[0].click();", driver.find_element(By.CSS_SELECTOR,'button[onclick="back(); return false;"]'))
            time.sleep(0.5*time_speed)
        except Exception as e:
            print(f"返回上一頁失敗：{e}")
        return 0
    except Exception as e:
        print(f"自動截圖失敗：{short_exception_message(e)}")
        return 1

def write_voteinfolist(voteinfolist):
    base_path = "./screenshots/"
    # with open(base_path+"id_list.txt", 'w', encoding='utf-8') as f:
    #     f.writelines([str(id)+"\n" for id in voteinfolist.keys()])

    for id, stock_id_list in voteinfolist.items():
        path = base_path + id + "/"
        if not os.path.exists(path):
            # if the directory does not exist, create it
            os.makedirs(path)
        with open(path + "imcomplele_screenshot_list.txt", 'w', encoding='utf-8') as f:
            f.writelines([str(id)+"\n" for id in stock_id_list])

def read_voteinfolist(voteinfolist):
    base_path = "./screenshots/"
    # ls of all folders name in the directory
    folder_list = [f for f in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, f))]
    for folder in folder_list:
        if folder == "all":
            continue
        path = base_path + folder + "/"
        if not os.path.exists(path + "imcomplele_screenshot_list.txt"):
            # if the file does not exist, create it
            with open(path + "imcomplele_screenshot_list.txt", 'w', encoding='utf-8') as f:
                f.write("")
        with open(path + "imcomplele_screenshot_list.txt", 'r', encoding='utf-8') as f:
            lines = f.readlines()
            for line in lines:
                stock_id = line.strip()
                if stock_id not in voteinfolist:
                    try:
                        voteinfolist[folder].append(stock_id)
                    except AttributeError:
                        if(debug>=3):
                            print(voteinfolist)
                        voteinfolist[folder]=[stock_id]
                    except KeyError:
                        voteinfolist[folder]=[stock_id]
    
    # print the voteinfolist
    for id, stock_id_list in voteinfolist.items():
        print(f"身分證字號：{id}，股票清單：{', '.join(stock_id_list)}")

# read manual vote setting
def read_vote_setting():
    import hashlib
    global manual_vote, accept_list, opposite_list, abstain_list, default_vote
    accept_list = []
    opposite_list = []
    abstain_list = []
    hash_value = ""
    # manual vote config reader
    if os.path.exists('./vote_setting.conf'):
        with open('./vote_setting.conf', 'r', encoding = 'utf8') as f:
            lines = f.readlines()
        for line in lines:
            if "default:::" in line:
                #default_vote = line.split(":::")[-1].replace("\n","").replace("\ufeff","")
                default_vote = line.split(":::")[-1].replace("\n","").replace("\ufeff","")
            if "accept:::" in line:
                accept_list.extend(keyword for keyword in line.split(":::")[-1].replace("\n","").replace("\ufeff","").split("|/|") if keyword not in accept_list and len(keyword)>0)
            elif "opposite:::" in line:
                opposite_list.extend(keyword for keyword in line.split(":::")[-1].replace("\n","").replace("\ufeff","").split("|/|") if keyword not in opposite_list and len(keyword)>0)
            elif "abstain:::" in line:
                abstain_list.extend(keyword for keyword in line.split(":::")[-1].replace("\n","").replace("\ufeff","").split("|/|") if keyword not in abstain_list and len(keyword)>0)
            elif "manual_vote:::" in line:
                if line.split(":::")[-1].replace("\n","").replace("\ufeff","") == "True":
                    manual_vote = True
                else:
                    manual_vote = False
            elif "hash:::" in line:
                hash_value = line.split(":::")[-1].replace("\n","").replace("\ufeff","")
        # check hash value
        content=default_vote+"|/|"+"#".join(accept_list)+"|/|"+"$".join(opposite_list)+"|/|"+"%".join(abstain_list)+"|/|"+str(manual_vote)
        # hash the content
        hash_object = hashlib.sha256(content.encode())
        hex_dig = hash_object.hexdigest()
        if hash_value != hex_dig:
            print("vote_setting.conf 設定檔已損毀（雜湊值不符），請重新啟動程式後重新設定。")
            # print("hash value: ", hash_value)
            # print("calculated hash value: ", hex_dig)
            if os.path.exists('./vote_setting.conf.bak'):
                os.remove('./vote_setting.conf.bak')
            os.rename('./vote_setting.conf', './vote_setting.conf.bak')
            print("vote_setting.conf 已重新命名為 vote_setting.conf.bak")
            print("請重新設定投票內容。")
            print("按 Enter 鍵結束程式")
            sys.exit()

def write_vote_setting():
    import hashlib
    global manual_vote, accept_list, opposite_list, abstain_list, default_vote
    #clear conflict setting
    match default_vote:
        case "accept":
            if len(accept_list) > 0:
                accept_list = []
            if len(opposite_list)==0 and len(abstain_list)==0:
                manual_vote = False
            else:
                manual_vote = True
        case "opposite":
            if len(opposite_list) > 0:
                opposite_list = []
            if len(accept_list)==0 and len(abstain_list)==0:
                manual_vote = False
            else:
                manual_vote = True
        case "abstain":
            if len(abstain_list) > 0:
                abstain_list = []
            if len(accept_list)==0 and len(opposite_list)==0:
                manual_vote = False
            else:
                manual_vote = True

    with open('./vote_setting.conf', 'w', encoding = 'utf8') as f:
        f.write("default:::"+default_vote+"\n")
        f.write("accept:::")
        f.write("|/|".join(accept_list))
        f.write("\n")
        f.write("opposite:::")
        f.write("|/|".join(opposite_list))
        f.write("\n")
        f.write("abstain:::")
        f.write("|/|".join(abstain_list))
        f.write("\n")
        f.write("manual_vote:::"+str(manual_vote)+"\n")
        content=default_vote+"|/|"+"#".join(accept_list)+"|/|"+"$".join(opposite_list)+"|/|"+"%".join(abstain_list)+"|/|"+str(manual_vote)
        # hash the content
        hash_object = hashlib.sha256(content.encode())
        hex_dig = hash_object.hexdigest()
        f.write("hash:::"+hex_dig+"\n")

def vi_vote_setting():
    global manual_vote, accept_list, opposite_list, abstain_list, default_vote
    tmp=""
    accept_list=[]
    opposite_list=[]
    abstain_list=[]
    default_vote=""
    print("----------- 預設投票設定如下 -----------")
    print("預設投票：abstain")
    print("贊成(accept)關鍵字：[]")
    print("反對(opposite)關鍵字：[]")
    print("棄權(abstain)關鍵字：[]")
    print("-------------------------------------------------------")
    while(True):
        tmp=input("是否使用這組預設設定？(y/n)")
        if tmp.lower() in ["y","n"]:
            break
        print("請輸入 y 或 n")
    if tmp.lower() == "y":
        default_vote="abstain"
        accept_list=[]
        opposite_list=[]
        abstain_list=[]
        manual_vote=False
        write_vote_setting()
        print("設定已儲存")
        return
    elif tmp.lower() == "n":
        print("請在下方設定投票內容")
        print("-------------------------------------------------------")
    # default vote
    while(True):
        tmp=input("請輸入預設投票選項（accept / opposite / abstain）：")
        if tmp.lower() in ["accept","opposite","abstain"]:
            default_vote=tmp.lower()
            break
        print("請輸入 accept、opposite 或 abstain 其中之一")
    # keyword to accept
    while(True):
        tmp=input("請輸入「贊成」關鍵字，每次一個，輸入 end 結束：")
        if tmp.lower() == "end":
            break
        if tmp not in accept_list:
            accept_list.append(tmp)
    # keyword to opposite
    while(True):
        tmp=input("請輸入「反對」關鍵字，每次一個，輸入 end 結束：")
        if tmp.lower() == "end":
            break
        if tmp not in opposite_list:
            opposite_list.append(tmp)
    # keyword to abstain
    while(True):
        tmp=input("請輸入「棄權」關鍵字，每次一個，輸入 end 結束：")
        if tmp.lower() == "end":
            break
        if tmp not in abstain_list:
            abstain_list.append(tmp)
    # print the setting
    print("預設投票：",default_vote)
    print("贊成(accept)關鍵字：",accept_list)
    print("反對(opposite)關鍵字：",opposite_list)
    print("棄權(abstain)關鍵字：",abstain_list)
    print("================")

    # confirm
    while(True):
        tmp=input("是否儲存設定？(y/n)")
        if tmp.lower() in ["y","n"]:
            break
        print("請輸入 y 或 n")
    if tmp.lower() == "y":
        write_vote_setting()
        print("設定已儲存")
        return
    elif tmp.lower() == "n":
        if os.path.exists('./vote_setting.conf.bak'):
            os.remove('./vote_setting.conf.bak')
        os.rename('./vote_setting.conf', './vote_setting.conf.bak')
        return

def write_program_setting():
    import hashlib
    global time_speed, shareholderIDs, screenshot_mode
    with open('./program_setting.conf', 'w', encoding = 'utf8') as f:
        f.write("screenshot_mode:::" + str(screenshot_mode) + "\n")
        f.write("time_speed:::" + str(int(time_speed*2)) + "\n")
        f.write("shareholderIDs:::" + "|/|".join(shareholderIDs) + "\n")
        content= str(screenshot_mode) + "|/|" + str(time_speed*2) + "|/|" + "@".join(shareholderIDs)
        # hash the content
        hash_object = hashlib.sha256(content.encode())
        hex_dig = hash_object.hexdigest()
        f.write("hash:::"+hex_dig+"\n")

def read_program_setting():
    import hashlib
    global time_speed, shareholderIDs, screenshot_mode
    hash_value = ""

    with open('./program_setting.conf', 'r', encoding = 'utf8') as f:
        settings = f.readlines()
    for line in settings:
        if "screenshot_mode:::" in line:
            screenshot_mode=int(line.split(":::")[-1].replace("\n","").replace("\ufeff",""))
        elif "time_speed:::" in line:
            time_speed=(int(line.split(":::")[-1].replace("\n","").replace("\ufeff","")))/2
        elif "shareholderIDs:::" in line:
            shareholderIDs=line.split(":::")[-1].replace("\n","").replace("\ufeff","").split("|/|")
        elif "hash:::" in line:
            hash_value = line.split(":::")[-1].replace("\n","").replace("\ufeff","")
    # check hash value
    content= str(screenshot_mode) + "|/|" + str(time_speed*2) + "|/|" + "@".join(shareholderIDs)
    # hash the content
    hash_object = hashlib.sha256(content.encode())
    hex_dig = hash_object.hexdigest()
    if hash_value != hex_dig:
        print("program_setting.conf 設定檔已損毀（雜湊值不符），請重新啟動程式後重新設定。")
        # print("hash value: ", hash_value)
        # print("calculated hash value: ", hex_dig)
        if os.path.exists('./program_setting.conf.bak'):
            os.remove('./program_setting.conf.bak')
        os.rename('./program_setting.conf', './program_setting.conf.bak')
        print("program_setting.conf 已重新命名為 program_setting.conf.bak")
        print("請重新設定程式參數。")
        print("按 Enter 鍵結束程式")
        sys.exit()

def vi_program_setting():
    global time_speed, shareholderIDs, screenshot_mode
    time_speed=2
    shareholderIDs=[]

    # set screenshot mode
    screenshot_mode = choose_screenshot_mode()

    # set time speed
    while(True):
        print("請輸入執行速度 1~30（數字越小，速度越快）")
        print("若有以下情況，建議改用較大的數值：")
        print("    - 電腦速度較慢")
        print("    - 網路速度較慢")
        print("    - TDCC 伺服器判定你像機器人")
        tmp = input("請輸入執行速度（預設為 2）：")
        if tmp.isdigit() and int(tmp) >= 1 and int(tmp) <= 30:
            time_speed = int(tmp)/2
            break
        elif tmp == "":
            time_speed = 2/2
            break
        else:
            print("請輸入 1~30 之間的數字")

    # set shareholder IDs
    while(True):
        tmp = input("請輸入股東身分證字號，每次一個，輸入 end 結束：")
        if tmp.lower() == "end":
            break
        if tmp not in shareholderIDs:
            # check if the ID is valid
            id_check_result = id_check(tmp)
            match id_check_result:
                case 0:
                    shareholderIDs.append(tmp)
                case 1:
                    print(tmp+" 看起來不是有效的台灣身分證字號。")
                case 2:
                    print(tmp+" 的檢查碼有誤，請重新確認。")
                case _:
                    # should not happen
                    raise ValueError(f"Unexpected id_check_result: {id_check_result}")
    
    # print the setting
    print("截圖模式：",str(screenshot_mode) + ":"+["依身分證字號分資料夾儲存","集中到同一資料夾，檔名為 {stock_id}_{stock_name}_{stock_account_id}.png","集中到同一資料夾，檔名為 {stock_id}_{stock_name}_{user_id}.png"][screenshot_mode-1])
    print("執行速度：",time_speed*2)
    print("股東數量：",len(shareholderIDs))
    print("股東身分證字號：",shareholderIDs)

    # confirm
    while(True):
        tmp = input("是否儲存設定？(y/n)")
        if tmp.lower() in ["y","n"]:
            break
        print("請輸入 y 或 n")
    if tmp.lower() == "y":
        write_program_setting()
        print("設定已儲存")
        return
    elif tmp.lower() == "n":
        if os.path.exists('./program_setting.conf.bak'):
            os.remove('./program_setting.conf.bak')
        os.rename('./program_setting.conf', './program_setting.conf.bak')
        print("設定未儲存")
        return

def load_settings():
    global time_speed, shareholderIDs, screenshot_mode
    global manual_vote, accept_list, opposite_list, abstain_list, default_vote
    
    if not os.path.exists('./vote_setting.conf'):
        print("找不到目前的投票設定，請先完成設定。")
        vi_vote_setting()
        input("按 Enter 鍵結束程式，之後再重新執行")
        sys.exit()
    if not os.path.exists('./program_setting.conf'):
        print("找不到目前的股東名單設定，請先完成設定。")
        vi_program_setting()
        input("按 Enter 鍵結束程式，之後再重新執行")
        sys.exit()

    read_program_setting()

    # user confirm
    while(True):
        #print("setting found, use modified setting")
        print("================")
        print("截圖模式：",str(screenshot_mode) + ":"+["依身分證字號分資料夾儲存","集中到同一資料夾，檔名為 {stock_id}_{stock_name}_{stock_account_id}.png","集中到同一資料夾，檔名為 {stock_id}_{stock_name}_{user_id}.png"][screenshot_mode-1])
        print("執行速度：",time_speed*2)
        print("股東數量：",len(shareholderIDs))
        print("股東身分證字號：",shareholderIDs)
        print("================")
        if no_confirm == True:
            tmp = "y"
            break
        tmp=input("是否套用以上設定？(y/n)")
        if tmp.lower() in ["y","n"]:
            break
        print("請輸入 y 或 n")
    if tmp.lower() == "y":
        pass
    elif tmp.lower() == "n":
        vi_program_setting()
        input("按 Enter 鍵結束程式，之後再重新執行")
        sys.exit()

    read_vote_setting()
    
    # user confirm
    while(True):
        #print("setting found, use modified setting")
        print("================")
        print("預設投票：",default_vote)
        print("贊成關鍵字：",accept_list)
        print("反對關鍵字：",opposite_list)
        print("棄權關鍵字：",abstain_list)
        print("================")
        if no_confirm == True:
            tmp = "y"
            break
        tmp=input("是否套用以上投票設定？(y/n)")
        if tmp.lower() in ["y","n"]:
            break
        print("請輸入 y 或 n")
    if tmp.lower() == "y":
        print("已套用目前投票設定")
        return
    elif tmp.lower() == "n":
        vi_vote_setting()
        input("按 Enter 鍵結束程式，之後再重新執行")
        sys.exit()

def choose_screenshot_mode():
    print("請選擇截圖儲存格式：")
    print("1. 依身分證字號分資料夾儲存")
    print("2. 集中到同一資料夾，檔名為 {stock_id}_{stock_name}_{stock_account_id}.png")
    print("3. 集中到同一資料夾，檔名為 {stock_id}_{stock_name}_{user_id}.png")
    while True:
        mode = input("請輸入 1、2 或 3：").strip()
        if mode in ["1", "2", "3"]:
            if(mode in ["2","3"]):
                if not os.path.exists(base_path+"/all/"):
                    os.makedirs(base_path+"/all/")
            return int(mode)
        print("請輸入 1、2 或 3。")

###############################################    START    ######################################################
driver=""
shareholderIDs=[]
time_speed=0
screenshot_mode = 1
manual_vote=False #是否自訂部分投票
default_vote="" #預設投票方式
accept_list=[]
opposite_list=[]
abstain_list=[]

voteinfolist={}

#build working directory
base_path="./screenshots/"
if not os.path.exists(base_path):
    # if the directory does not exist, create it
    os.makedirs(base_path)

#does last time have unfinished screenshot
voteinfolist={}
read_voteinfolist(voteinfolist)

#check and delete space entry
for id, stock_id_list in voteinfolist.items():
    if len(stock_id_list) == 0:
        del voteinfolist[id]
if len(list(voteinfolist.keys()))>0:
    if(no_confirm == True):
        check = "Y"
    else:
        check=input("偵測到上次有未完成的截圖，是否要繼續處理？(Y/N)：").upper()
    if check=="Y":
        load_settings() # for screenshot mode
        print("--------- 繼續處理截圖 ---------")
        driver = webdriver.Chrome() # selenium auto install
        for id in voteinfolist.keys():
            print("身分證字號：",id)
            print("股票清單：",voteinfolist[id])
            autoLogin(id)
            while(len(voteinfolist[id])>0):
                result = auto_screenshot(id,voteinfolist[id][0])
                if result != 0:
                    print(f"{voteinfolist[id][0]} 自動截圖失敗")
        print("-----  截圖完成  -----")
        logout()
        driver.quit()

##################################################################

tmp_flag =0
while(True):
    print("-------------------------------")
    print("(1) 所有帳號自動投票並截圖")
    print("(2) 針對指定股票截圖")
    print("(3) 離開")
    print("-------------------------------")
    if no_confirm == True:
        check = "1"
    else:
        check=input("請選擇：")
    if check not in ["1","2","3"]:
        print("請輸入 1、2 或 3")
        print("請重新啟動程式後再試一次。")
        input("按 Enter 鍵結束程式")
        sys.exit()
    if check=="3" or (no_confirm==True and tmp_flag == 1):
        print("離開程式")
        input("按 Enter 鍵結束程式")
        sys.exit()
    if check=="1":
        tmp_flag = 1
        load_settings()
        # build working directory
        for id in shareholderIDs:
            path="./screenshots/"+id+"/"
            if not os.path.exists(path):
                # if the directory does not exist, create it
                os.makedirs(path)
            if id not in voteinfolist.keys():
                voteinfolist[id]=[]
        
        # driver = webdriver.Chrome() # selenium auto install
        driver = open_browser()
        for user_id in shareholderIDs:
            # open a test page (can be local or online HTML)
            driver.get("file:///" + os.path.abspath("./statement.html"))
            time.sleep(5)
            autoLogin(user_id)
            result = autovote(user_id)
            if result != 0:
                print(f"{user_id} 自動投票失敗")
            # check if the page is loaded
            while(len(voteinfolist[user_id])>0):
                result = auto_screenshot(user_id, voteinfolist[user_id][0])
                if result != 0:
                    print(f"{voteinfolist[user_id][0]} 自動截圖失敗")
            print("------ 已完成 ------")
            logout()
        driver.quit()
    elif check=="2":
        screenshot_mode = choose_screenshot_mode()
        # driver = webdriver.Chrome() # use the installed driver
        driver = open_browser()
        while(True):
            id=input("請輸入要截圖的股東身分證字號（輸入 -1 可離開）：")
            if id == "-1":
                print("離開程式")
                driver.quit()
                input("按 Enter 鍵結束程式")
                sys.exit()
            if(id_check(id) != 0):
                print("身分證字號格式不正確。")
                continue
                
            while(True):
                try:
                    autoLogin(id)
                    break
                except Exception as e:
                    print("發生錯誤：",e)
                    continue
            # check if the page is loaded
            # driver.get("https://stockservices.tdcc.com.tw/evote/shareholder/000/tc_estock_welshas.html")
            # while(True):
            #     time.sleep(1.5)
            #     # check if the page is loaded(by stock search box)
            #     if driver.find_elements(By.NAME,'qryStockId'):
            #         break
            
            while(True):
                try:
                    #stock_list=input("請輸入要擷取的股號，多個股號請用「,」分開：").upper()
                    stock_list=input('請輸入要截圖的股號，多個股號請以「,」分隔（輸入 -1 可離開）：').upper()
                    if stock_list == "-1":
                        break
                    stock_list=stock_list.replace(" ","").split(",")
                    stock_list= [i for i in stock_list if i not in [""," ","\n"] and i.isdigit() and int(i)>0]
                    if len(stock_list) == 0:
                        print("沒有偵測到有效的股號。")
                        continue
                    print("開始截圖：",stock_list)
                    if(id not in voteinfolist.keys()):
                        voteinfolist[id]=[]
                    voteinfolist[id].extend(stock_list)
                    for stock_id in stock_list:
                        result = auto_screenshot(id, stock_id)
                        if result != 0:
                            print(f"{stock_id} 自動截圖失敗")
                except Exception as e:
                    print("發生錯誤：",e)
                    continue
            logout()
