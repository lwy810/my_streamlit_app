import requests
import pandas as pd
import sqlite3
import datetime
import time


# category 코드 → 사람이 읽을 수 있는 이름으로 매핑 (이 매핑은 직접적으로 사용되지 않음, 정보성으로 유지)
category_map = {
    "dataDate": "발령일",
    "districtName": "지역명",
    "itemCode": "항목명", # stationName도 중요한 정보
    "issueGbn": "경보단계",
    "issueTime": "발령시간",
    "issueVal": "발령농도",
    "clearDate": "해제일",
    "clearTime": "해제시간",
    "clearVal": "해제농도"
}

# 데이터 수집 + 전처리 + 저장 함수
def fetch_and_store():
    now = datetime.datetime.now()

    # API 파라미터 설정
    # getCtprvnRltmMesureDnsty는 base_date, base_time 파라미터가 필요 없습니다.
    params = {
        "serviceKey": "IlKf+/s38dEMDB7W9oToxSVtk9Cre94VFL3jEPuj/Gf4LU7jE9CfQBxrkymu3+2Ix2JfgnCSOuitIzZgfGIjWw==",  # 본인의 인증키로 교체하세요
        "returnType": "JSON",
        "numOfRows": "100",  # 시도 내 모든 측정소 데이터를 가져오기 위해 충분히 크게 설정
        "pageNo": "1",
        "year": "2020",  # '수원시'의 시도는 '경기' 입니다. 시도명은 문자열로 입력
        "itemCode": "PM10"  # 문서에 따르면 '1.3' 버전이 최신입니다.
    }

    url = "http://apis.data.go.kr/B552584/UlfptcaAlarmInqireSvc/getUlfptcaAlarmInfo"

    try:
        print(f"[{now}] API 호출 시작...")
        response = requests.get(url, params=params, verify=False) # 이 부분을 추가

        # 응답 텍스트 직접 출력 (디버깅용)
        print(f"[{now}] API 응답 상태 코드: {response.status_code}") # 이 줄도 확인
        print(f"[{now}] Raw API Response: {response.text}") # 이 줄을 활성화해서 전체 응답을 보세요
        
        # HTTP 오류 발생 시 바로 예외 처리 (4xx, 5xx 에러)
        response.raise_for_status()

        # 응답이 비어있는 경우를 대비
        if not response.text.strip(): # 공백도 제거하고 확인
            print(f"[{now}] 오류 발생: API 응답이 비어있습니다.")
            return

        # 응답 텍스트 직접 출력 (디버깅용)
        # print(f"[{now}] API 응답 텍스트 (일부): {response.text[:1000]}...") # 길면 일부만 출력

        data = response.json() # 여기서 'Expecting value' 오류가 나면 응답 텍스트를 다시 확인해야 합니다.

        # 응답 구조 확인 및 데이터 추출
 
        items = data['response']['body']['items']
            
        if not items:
            print(f"[{now}] API 응답에 측정소 정보가 없습니다. (items 리스트가 비어있음)")
            return

        df = pd.DataFrame(items)
        
        # 필요한 컬럼만 선택
        selected_columns = [
            'dataDate', 'itemCode', 'districtName',
            'issueGbn', 'issueVal','issueDate', 'issueTime',
            'clearVal', 'clearDate', 'clearTime'
        ]
        
        # DataFrame에 해당 컬럼이 없는 경우를 대비하여 추가 (NaN으로 채워짐)
        # 이 API는 해당 컬럼들을 항상 제공하므로 사실상 큰 의미는 없지만, 안전을 위해 유지
        for col in selected_columns:
            if col not in df.columns:
                df[col] = pd.NA

            df = df[selected_columns]

        # 유효한 미세먼지 값 (pm10Value 또는 pm25Value)이 있는 행만 유지 (선택 사항)
        # 모두 NaN인 행은 제거하지 않도록 how='all' 사용

        # SQLite에 저장
            conn = sqlite3.connect("microdust_report.db")
            # 테이블명 변경 (미세먼지 데이터이므로 더 적절한 이름으로)
            df.to_sql("fine_dust_realtime", conn, if_exists='replace', index=False,
                        dtype = {
                            'dataDate': 'TEXT',
                            'itemCode': 'TEXT',
                            'districtName': 'TEXT',
                            'issueGbn': 'TEXT',
                            'issueVal': 'INTEGER',
                            'issueDate': 'TEXT',
                            'issueTime': 'TEXT',
                            'clearVal': 'INTEGER',
                            'clearDate': 'TEXT',
                            'clearTime': 'TEXT'
                        })
            conn.close()

            print(f"[{datetime.datetime.now()}] 저장 완료: {len(df)}건")
        else:
            print(f"[{datetime.datetime.now()}] API 응답 구조가 예상과 다릅니다: {data}. 전체 응답: {response.text}")

    except requests.exceptions.HTTPError as http_err:
        print(f"[{datetime.datetime.now()}] HTTP 오류 발생: {http_err} (Status Code: {response.status_code}, Response: {response.text})")
    except requests.exceptions.ConnectionError as conn_err:
        print(f"[{datetime.datetime.now()}] 연결 오류 발생: {conn_err}")
    except requests.exceptions.Timeout as timeout_err:
        print(f"[{datetime.datetime.now()}] 타임아웃 오류 발생: {timeout_err}")
    except requests.exceptions.RequestException as req_err:
        print(f"[{datetime.datetime.now()}] 기타 요청 오류 발생: {req_err}")
    except ValueError as json_err:
        # 이 오류가 발생하면 response.text를 출력하여 실제 응답 내용을 확인해야 합니다.
        print(f"[{datetime.datetime.now()}] JSON 디코딩 오류 발생 (응답 내용 확인 필요): {json_err}.")
        print(f"Raw API Response: {response.text}")
    except Exception as e:
        print(f"[{datetime.datetime.now()}] 알 수 없는 오류 발생: {e}")

# 1시간마다 자동 실행
while True:
    fetch_and_store()
    time.sleep(3600)  # 1시간(3600초)동안 중지
    


