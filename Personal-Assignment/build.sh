#!/bin/bash

# Python 의존성 설치 (requirements.txt에 있는 모든 패키지 설치)
pip install -r requirements.txt

# Playwright 브라우저 바이너리 설치 (Chromium만 설치)
playwright install chromium