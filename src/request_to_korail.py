'''

http://www.letskorail.com/ebizprd/EbizPrdTicketPr21111_i1.do

post
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3
Accept-Encoding: gzip, deflate
Accept-Language: ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7
Content-Type: application/x-www-form-urlencoded
Cache-Control: max-age=0
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36

'''

# Headless chrome
import os
import platform
import traceback

from selenium import webdriver
from selenium.common.exceptions import NoSuchAttributeException, NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait

from src.config.keys import korail_id, korail_pw
from src.config.select_day import s_hour, s_day, s_month, s_start, s_end, s_page, s_year
from src.json_param import browser_options
from src.send_slacker import *

DriverDirPath = os.path.join(os.path.dirname(__file__), '..', 'driver')

f_platform = platform.system()
options = webdriver.ChromeOptions()

for o in browser_options:
    options.add_argument(o)

options.add_argument('headless')
options.add_argument('window-size=1920x1080')


if f_platform == 'Windows':
    driver_path = os.path.join(DriverDirPath, 'chromedriver_win_v78.exe')
    options.add_argument('disable-gpu')
elif f_platform == 'Linux':
    driver_path = os.path.join(DriverDirPath, 'chromedriver_linux_v79')
else:
    print('에러 OS 확인 %s' % f_platform)
    send_msg('에러 OS 확인 %s' % f_platform)
    raise OSError
driver = webdriver.Chrome(driver_path, options=options)

booking_list = []


def login():
    driver.get('http://www.letskorail.com/korail/com/login.do')
    driver.execute_script('document.form1.selInputFlg.value = "2"')
    driver.execute_script('document.form1.txtMember.value = "%s"' % korail_id)
    driver.execute_script('document.form1.txtPwd.value = "%s"' % korail_pw)
    driver.execute_script('Login(2)')
    send_msg('로그인.')
    return True


def train_search():
    if driver.current_url == 'http://www.letskorail.com/ebizprd/EbizPrdTicketPr21111_i1.do':
        driver.refresh()
    else:
        driver.get('http://www.letskorail.com/')
        '''
        출발역
        //*[@id="txtGoStart"]
        도착역
        //*[@id="txtGoEnd"]
        도착일
        //*[@id="selGoStartDay"]
        시간 (select)
        //*[@id="time"]
        예매 버튼
        //*[@id="res_cont_tab01"]/form/div/fieldset/p/a
        '''
        driver.implicitly_wait(0)

        driver.execute_script('document.form1.txtGoStart.value = "%s"' % s_start)
        driver.execute_script('document.form1.txtGoEnd.value = "%s"' % s_end)
        # 00- ktx 01 - 새마을 02 - 무궁화 03 - ?? 04- 무궁화 05- 무궁화 새마을 06 - ?? 07 - ?? 08 - 새마을
        driver.execute_script('document.form1.selGoTrain.value = "00"')

        driver.execute_script('document.form1.selGoYear.value = 2020')
        driver.execute_script('document.form1.selGoMonth.value = %s' % s_month)
        driver.execute_script('document.form1.selGoDay.value = %s' % s_day)
        driver.execute_script('document.form1.selGoHour.value = %s' % s_hour)
        driver.execute_script('inqSchedule()')
        WebDriverWait(driver, 2).until(expected_conditions.title_contains('일반승차권'))
    last_time = 0
    for i in range(s_page):
        print('%d PAGE' % (i + 1))
        ## Check
        try:
            reserve_table_body = driver.find_element_by_xpath('//*[@id="tableResult"]').find_element_by_tag_name('tbody')
        except NoSuchElementException:
            # send_msg('tableResult NoSuchElementException')
            return False
        for a in reserve_table_body.find_elements_by_tag_name('a'):
            h = a.get_attribute('href')
            if h and str(h).split(':')[1][:7] == 'infochk':
                # 빈자리 ( 바로 예매 )
                if str(h).split(':')[1][8] == '1':
                    print(h)
                    a.click()
                    try:
                        WebDriverWait(driver, 2).until(expected_conditions.alert_is_present())
                        alert = driver.switch_to.alert
                        alert.accept()
                    except :
                        print('No alert')
                        send_msg('에러?!\n%s' % traceback.print_exc())
                    send_msg('빈자리 발견!')
                    after_reserve()
                # 예약 대기
                elif str(h).split(':')[1][8] == '1':
                    print(h)
                    if str(h).split(':')[1][10] in booking_list:
                        continue
                    a.click()
                    booking_list.append(str(h).split(':')[1][10])
                    try:
                        WebDriverWait(driver, 2).until(expected_conditions.alert_is_present())
                        alert = driver.switch_to.alert
                        alert.accept()
                    except:
                        print('No alert')
                        send_msg('에러?!\n%s' % traceback.print_exc())
                    send_msg('예약 걸어둠.')
        last_time = find_last_time(reserve_table_body.text)
        if s_page > 1 and last_time != 0:
            driver.execute_script("btnNextReserve('%s%s%s', '%s00');" % (s_year, s_month, s_day, last_time))
            WebDriverWait(driver, 2).until(expected_conditions.presence_of_element_located((By.ID, "tableResult")))
    return False


def find_last_time(tr: str):
    res = tr.split('\n')[-4]
    last_time = ''.join(e for e in str(res) if e.isnumeric())
    if len(last_time) != 4:
        print('다음 페이지 찾을수없음. last_time error - %s' % res)
        return 0
    return last_time


def is_login():
    try:
        login_el = driver.find_element_by_xpath('//*[@id="header"]/div[1]/div/ul/li[2]')
        if login_el.get_attribute('class') == 'log_nm':
            return
    except NoSuchAttributeException:
        capture_current_page()
        send_msg('에러?!\n%s' % traceback.print_exc())

    login()


def after_reserve():
    try:
        WebDriverWait(driver, 10).until(expected_conditions.alert_is_present())
        alert = driver.switch_to.alert
        alert.accept()
    except:
        print('No alert')
        capture_current_page()
        send_msg('에러?!\n%s' % traceback.print_exc())

    try:
        WebDriverWait(driver, 10).until(expected_conditions.alert_is_present())
        alert = driver.switch_to.alert
        alert.accept()
        capture_current_page()
    except:
        print('No alert')
        capture_current_page()
        send_msg('에러?!\n%s' % traceback.print_exc())

    try:
        capture_current_page()
        WebDriverWait(driver, 5).until(expected_conditions.title_contains('예약'))
        print('예약 완료.')
        send_msg('예약완료, 결제 ㄱㄱ')
        return True
    except:
        print('에러?')
        capture_current_page()
        send_msg('에러?!\n%s' % traceback.print_exc())

    # return False


def capture_current_page():
    try:
        driver.save_screenshot('capture.png')
        file = open('capture.png', 'rb')
        file_upload(file)
        file.close()
    except:
        send_msg('스크린샷 보내기 실패.')


# if __name__ == '__main__':

    # cnt = 0
    # login()
    # train_search()
    # capture_current_page()
    # while not train_search(True):
    #     cnt += 1
    #     print("[%s]%d 번째 시도중" % (datetime.now(), cnt))
    #     # time.sleep(1)
    #     is_login()
    #
    # after_reserve()

    # driver.quit()