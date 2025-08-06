# Streamlit 앱을 실행하기 위한 공식 파이썬 이미지를 사용합니다.
FROM python:3.9-slim

# 작업 디렉터리를 설정합니다.
WORKDIR /app

# apt-get을 업데이트하고, wget 및 gnupg 패키지를 설치합니다.
RUN apt-get update && apt-get install -y \
    wget \
    gnupg

# 구글 크롬 저장소 키를 가져와 추가합니다.
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add -

# 구글 크롬 저장소를 apt 소스 리스트에 추가합니다.
RUN sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list'

# 패키지 목록을 다시 업데이트하고, google-chrome-stable 패키지를 설치합니다.
# Playwright가 필요로 하는 추가적인 시스템 의존성도 함께 설치합니다.
RUN apt-get update && apt-get install -y \
    google-chrome-stable \
    libnss3 \
    libatk-bridge2.0-0 \
    libxkbcommon0 \
    libdrm-dev \
    libgbm-dev \
    libasound2

# requirements.txt 파일을 복사하고 파이썬 라이브러리를 설치합니다.
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# 현재 디렉터리의 모든 파일을 컨테이너로 복사합니다.
COPY . .

# Streamlit 앱을 실행하는 명령을 정의합니다.
CMD ["streamlit", "run", "app.py"]