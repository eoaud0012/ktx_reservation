import random
import time
from datetime import datetime

from src.request_to_korail import login, train_search, is_login, after_reserve, driver

cnt = 0
login()
# train_search()
while not train_search():
    cnt += 1
    print("[%s]%d 번째 시도중" % (datetime.now(), cnt))
    time.sleep(random.randint(1, 12) / 10)
    is_login()

after_reserve()

driver.quit()