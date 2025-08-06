# 구글 크롬 저장소 키 가져오기
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -

# 구글 크롬 저장소 추가
sudo sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'

# 패키지 목록 업데이트
sudo apt-get update

# google-chrome-stable 패키지 설치
sudo apt-get install -y google-chrome-stable

# Playwright의 시스템 의존성 설치 (선택 사항이지만, Playwright 사용 시 권장)
# 이 명령은 Playwright가 필요로 하는 추가적인 Linux 라이브러리들을 설치합니다.
# Playwright Python 라이브러리 자체는 requirements.txt를 통해 설치됩니다.
# 이 명령은 'apt-get install -y playwright'와는 다릅니다.
# Playwright 공식 문서에서 권장하는 의존성 설치 명령어입니다.
sudo apt-get install -y libnss3 libatk-bridge2.0-0 libxkbcommon0 libdrm-dev libgbm-dev libasound2