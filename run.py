import time
from datetime import datetime

from src.request_to_korail import login, train_search, is_login, after_reserve, driver

cnt = 0
login()
train_search()
while not train_search(True):
    cnt += 1
    print("[%s]%d 번째 시도중" % (datetime.now(), cnt))
    time.sleep(1)
    is_login()

after_reserve()

driver.quit()