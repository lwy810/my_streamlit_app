import streamlit as st
import pandas as pd
import requests
import plotly.express as px
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import io # PDF/Excel 파일 스트림 처리를 위함
import os # 환경 변수 등 사용을 위함

# --- 1. API 키 및 설정 (실제 앱에서는 보안상 .env 파일 등으로 관리) ---
API_KEY = "YOUR_AIRKOREA_API_KEY"
AIRKOREA_API_URL = "http://apis.data.go.kr/B552584/ArpltnInforInqireSvc/getMsrstnAcctoRltmMesureDnsty"

# --- 2. 미세먼지 등급 정의 ---
FINE_DUST_GRADE = {
    "PM10": {
        "좋음": (0, 30),
        "보통": (31, 80),
        "나쁨": (81, 150),
        "매우 나쁨": (151, 999),
    },
    "PM25": {
        "좋음": (0, 15),
        "보통": (16, 35),
        "나쁨": (36, 75),
        "매우 나쁨": (76, 999),
    }
}

def get_grade(value, pollutant_type):
    """미세먼지 농도에 따른 등급 반환"""
    if pd.isna(value):
        return "정보 없음"
    value = int(value)
    for grade, (min_val, max_val) in FINE_DUST_GRADE[pollutant_type].items():
        if min_val <= value <= max_val:
            return grade
    return "알 수 없음"

def get_color(grade):
    """등급에 따른 색상 반환"""
    colors = {
        "좋음": "green",
        "보통": "darkgoldenrod", # 보통은 노랑/주황에 가까운 색
        "나쁨": "red",
        "매우 나쁨": "darkred",
        "정보 없음": "gray",
        "알 수 없음": "gray"
    }
    return colors.get(grade, "gray")

# --- 3. 데이터 가져오기 함수 (실제 API 호출 로직) ---
@st.cache_data(ttl=600) # 10분마다 캐시 갱신
def fetch_dust_data(station_name):
    try:
        params = {
            'serviceKey': API_KEY,
            'returnType': 'json',
            'numOfRows': '1',
            'pageNo': '1',
            'stationName': station_name,
            'dataTerm': 'DAILY',
            'ver': '1.3'
        }
        response = requests.get(AIRKOREA_API_URL, params=params)
        response.raise_for_status() # HTTP 오류 발생 시 예외 발생