# 실행 방법
# python weather_auto_fetcher.py
# 종료: ctrl+C

import requests
import pandas as pd
import sqlite3
import datetime
import time


# category 코드 → 사람이 읽을 수 있는 이름으로 매핑
category_map = {
    "dataTime": "측정일시",
    "sidoName": "시도명",
    "pm10Value": "미세먼지(PM10) 농도",
    "pm25Value": "미세먼지(PM2.5) 농도",
    "pm10Grade": "미세먼지(PM10) 24시간 등급자료",
    "pm25Grade": "미세먼지(PM2.5) 24시간 등급자료"
}

# 데이터 수집 + 전처리 + 저장 함수
def fetch_and_store():
    now = datetime.datetime.now() # 현재 날짜와 시간 객체(datetime) 가져옴
    base_date = now.strftime("%Y%m%d")  # 현재 날짜를 YYYYMMDD 형식의 문자열로 변환
    base_time = now.strftime("%H00")  # 정시 기준 (예: 1500)

    # API 파라미터 설정
    params = {
        "serviceKey": "IlKf+/s38dEMDB7W9oToxSVtk9Cre94VFL3jEPuj/Gf4LU7jE9CfQBxrkymu3+2Ix2JfgnCSOuitIzZgfGIjWw==",  # 본인의 인증키로 교체하세요
        "returnType": "JSON",
        "numOfRows": "100",
        "pageNo": "1",
        "sidoName" : "경기",
        "ver" : "1.3"
    }

    url = "http://apis.data.go.kr/B552584/ArpltnInforInqireSvc/getCtprvnRltmMesureDnsty"

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # 응답의 HTTP 상태 코드를 확인하고 오류가 발생할 때 예외 발생
        data = response.json()
        items = data['response']['body']['items']

        if not items:
            print(f"[{datetime.datetime.now()}] API 응답에 측정소 정보가 없습니다.")
            return

        df = pd.DataFrame(items)

        # 전처리
        df['datetime'] = pd.to_datetime(df['baseDate'] + df['baseTime'], format='%Y%m%d%H%M')

        selected_columns = [
            'dataTime', 'sidoName',
            'pm10Value', 'pm10Grade',
            'pm25Value', 'pm25Grade'
        ]        
        df = df[selected_columns]

        df['category_name'] = df['category'].map(category_map)
        df = df[['datetime', 'category', 'category_name', 'obsrValue']]
        df = df.sort_values(by='datetime').reset_index(drop=True)
        df['obsrValue'] = pd.to_numeric(df['obsrValue'], errors='coerce')
        df = df.dropna(subset=['obsrValue'])  # NaN 제거

        # SQLite에 저장
        conn = sqlite3.connect("microdust_report.db")
        df.to_sql("ultra_short_forecast", conn, if_exists='append', index=False,
                  dtype={
                    'dataTime': 'TEXT',
                    'sidoName': 'TEXT',
                    'stationName': 'TEXT',
                    'pm10Value': 'REAL',
                    'pm10Grade': 'INTEGER',
                    'pm25Value': 'REAL',
                    'pm25Grade': 'INTEGER'
                  })
        conn.close()

        print(f"[{datetime.datetime.now()}] 저장 완료: {len(df)}건")

    except Exception as e:
        print(f"[{datetime.datetime.now()}] 오류 발생: {e}") # 예시: [2025-07-15 15:00:12.345678] 오류 발생: 404 Client Error:

# 1시간마다 자동 실행
while True:
    fetch_and_store()
    time.sleep(3600)  # 1시간(3600초)동안 중지 