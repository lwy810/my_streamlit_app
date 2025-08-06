# 구글 크롬 저장소 키 가져오기
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -

# 구글 크롬 저장소 추가
sudo sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'

# 패키지 목록 업데이트
sudo apt-get update