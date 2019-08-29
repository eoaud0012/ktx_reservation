import random
import time
import traceback
from datetime import datetime

from src.request_to_korail import login, train_search, is_login, after_reserve, driver, capture_current_page
from src.send_slacker import send_msg

cnt = 0
try:
    login()
    while not train_search():
        cnt += 1
        print("[%s]%d 번째 시도중" % (datetime.now(), cnt))
        # time.sleep(random.randint(1, 12) / 10)
        is_login()
        # if cnt % 1000 == 0:
            # capture_current_page()

    after_reserve()
except:
    capture_current_page()
    send_msg("꺼짐 \n %s" % traceback.print_exc())
finally:
    driver.quit()
