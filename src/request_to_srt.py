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
from datetime import datetime

from selenium import webdriver
from selenium.common.exceptions import NoSuchAttributeException, NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait

from src.config.keys import korail_id, korail_pw, srt_id, srt_pw
from src.config.select_day import s_hour, s_day, s_month, s_start, s_end, s_page, s_year, s_person
from src.json_param import browser_options
from src.send_slacker import *

DriverDirPath = os.path.join(os.path.dirname(__file__), '..', 'driver')

f_platform = platform.system()
options = webdriver.ChromeOptions()

for o in browser_options:
    options.add_argument(o)

# options.add_argument('headless')
# options.add_argument('window-size=1920x1080')


if f_platform == 'Windows':
    driver_path = os.path.join(DriverDirPath, 'chromedriver_win_v85.exe')
    # options.add_argument('disable-gpu')
elif f_platform == 'Linux':
    driver_path = os.path.join(DriverDirPath, 'chromedriver_linux_v79')
else:
    print('에러 OS 확인 %s' % f_platform)
    send_msg('에러 OS 확인 %s' % f_platform)
    raise OSError
driver = webdriver.Chrome(driver_path, options=options)

booking_list = []


def login():
    driver.get('https://etk.srail.kr/cmc/01/selectLoginForm.do')
    driver.execute_script('document.querySelector("#srchDvNm01").value = "%s"' % srt_id)
    driver.execute_script('document.querySelector("#hmpgPwdCphd01").value = "%s"' % srt_pw)
    driver.execute_script('document.querySelector("#login-form > fieldset > div.input-area.loginpage.clear > div.fl_l > div.con.srchDvCd1 > div > div.fl_r > input").click()')
    send_msg('로그인.')
    return True


def train_search():
    if driver.current_url == 'https://etk.srail.kr/hpg/hra/01/selectScheduleList.do?pageId=TK0101010000':
        driver.refresh()
    else:
        driver.get('https://etk.srail.kr/main.do')
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
        '''
        # 출발
        $('search-form').dptRsStnCd.options[ % s].selected
        # 도착
        $('search-form').arvRsStnCd.options[ % s].selected
        # 일자 2020.10.03
        $('search-form').dptDt = "%s"
        # 시간 2시간텀, [0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22].index
        $('search-form').dptTm.options[ % s].selected
        # 어른 인원수
        $('search-form').psgInfoPerPrnb1.value = "%s"
        '''
        station_code_table = {'수서': 1, '동탄': 2, '동대구': 8, '부산': 11}
        driver.execute_script('$("search-form").dptRsStnCd.options[%s].selected = true' % station_code_table[s_start])
        driver.execute_script('$("search-form").arvRsStnCd.options[%s].selected = true' % station_code_table[s_end])
        driver.execute_script('$("search-form").dptDt.value = "%s"' % datetime(year=int(s_year),
                                                                         month=int(s_month),
                                                                         day=int(s_day)).strftime('%Y%m%d'))

        srt_time_table = [0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22]
        driver.execute_script('$("search-form").dptTm.options[%s].selected = true' % srt_time_table.index(int(s_hour)))
        driver.execute_script('$("search-form").psgInfoPerPrnb1.value = "%s"' % s_person)  # 인원수
        driver.execute_script('selectScheduleList()')
        WebDriverWait(driver, 2).until(expected_conditions.title_contains('일반승차권'))

    ## Check
    try:
        reserve_table_body = driver.find_element_by_xpath('//*[@id="result-form"]/fieldset/div[6]/table').find_element_by_tag_name('tbody')
    except NoSuchElementException:
        # send_msg('tableResult NoSuchElementException')
        return False
    for a in reserve_table_body.find_elements_by_tag_name('a'):
        h = a.get_attribute('class')
        if h and ('btn_burgundy_dark' in str(h).split(' ')):
            # 빈자리 ( 바로 예매 )
            a.click()
            corona_alert = WebDriverWait(driver, 1).until(
                expected_conditions.presence_of_element_located((By.XPATH, '/html/body/div[12]/div[3]/div/button')))
            corona_alert.click()
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
            # elif str(h).split(':')[1][8] == '1':
            #     print(h)
            #     if str(h).split(':')[1][10] in booking_list:
            #         continue
            #     a.click()
            #     booking_list.append(str(h).split(':')[1][10])
            #     try:
            #         WebDriverWait(driver, 2).until(expected_conditions.alert_is_present())
            #         alert = driver.switch_to.alert
            #         alert.accept()
            #     except:
            #         print('No alert')
            #         send_msg('에러?!\n%s' % traceback.print_exc())
            #     send_msg('예약 걸어둠.')
    return False


def is_login():
    try:
        # cfg.isLogin
        is_login_val = driver.execute_script('return cfg.isLogin')
        print('로그인체크')
        print(is_login_val)
        if is_login_val:
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