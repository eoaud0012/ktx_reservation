
# Azure VM 위에서
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