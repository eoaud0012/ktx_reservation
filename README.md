# KTX 자동 예매
명절 혹은 연휴때 기차표 예매하느라 모니터 쳐다보기 귀찮음.
컴퓨터야, 코레일 들어가서 로그인하고 내가 알려준 시간대 기차 조회하고 자리 있으면 예약하고 알려도!  

## 중요 로직
### web driver
Selenium + chrome driver
### 로그인
```python
driver.get('http://www.letskorail.com/korail/com/login.do')
driver.execute_script('document.form1.selInputFlg.value = "2"')
driver.execute_script('document.form1.txtMember.value = "%s"' % korail_id)
driver.execute_script('document.form1.txtPwd.value = "%s"' % korail_pw)
driver.execute_script('Login(2)')
```
### 기차 조회
```python
driver.get('http://www.letskorail.com/')
driver.implicitly_wait(0)
driver.execute_script('document.form1.txtGoStart.value = "%s"' % s_start)
driver.execute_script('document.form1.txtGoEnd.value = "%s"' % s_end)
driver.execute_script('document.form1.selGoTrain.value = "00"')
driver.execute_script('document.form1.selGoYear.value = 2020')
driver.execute_script('document.form1.selGoMonth.value = %s' % s_month)
driver.execute_script('document.form1.selGoDay.value = %s' % s_day)
driver.execute_script('document.form1.selGoHour.value = %s' % s_hour)
driver.execute_script('inqSchedule()')
WebDriverWait(driver, 2).until(expected_conditions.title_contains('일반승차권'))
```
여기서 얻은 페이지에서 html 파싱을 통해 예매가능 유무 판단.
### 푸시 메세지
슬랙 API를 통해 알림.
### 오류 처리
`driver.save_screenshot('capture.png')` 스크린샷을 슬랙으로 보냄. 
## VM 사용시 setting
### Ubuntu
```
git clone https://github.com/pyenv/pyenv.git ~/.pyenv

echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bash_profile
echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bash_profile
echo 'eval "$(pyenv init -)"' >> ~/.bash_profile

source ~/.bash_profile
pyenv versions


pyenv install 3.7.3
or
pyenv install 3.7.4


sudo apt-get install -y make build-essential zlib1g-dev libffi-dev libssl-dev \
libreadline-dev libsqlite3-dev libbz2-dev

git clone https://github.com/yyuu/pyenv-virtualenv.git ~/.pyenv/plugins/pyenv-virtualenv
echo 'eval "$(pyenv virtualenv-init -)"' >> ~/.bash_profile
source ~/.bash_profile

pyenv virtualenv 3.5.2 test-env

pyenv activate test-env

(project_dir) pyenv local test-env

pip install -r requirements.txt

sudo apt-get install chromium-browser   (버전확인 필수.)
chromium-browser --version

project/driver/chromdriver_(os명)

python run.py

```