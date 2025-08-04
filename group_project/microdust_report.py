import pandas as pd
import sqlite3
import datetime # <<< 이 줄이 있는지 반드시 확인하세요


# 데이터베이스 파일 경로
db_file = "microdust_report.db"
table_name = "fine_dust_realtime"

# 1. SQLite 데이터베이스에 연결
try:
    conn = sqlite3.connect(db_file)
    print(f"[{datetime.datetime.now()}] 데이터베이스 '{db_file}'에 성공적으로 연결했습니다.")

    # 2. SQL 쿼리 작성 (여기서는 모든 데이터를 선택하는 쿼리)
    query = f"SELECT * FROM {table_name} LIMIT 100" # 100개 확인

    # 3. pandas를 사용하여 쿼리 실행 및 DataFrame으로 불러오기
    # read_sql_query는 SQL 쿼리를 직접 실행하고 결과를 DataFrame으로 반환합니다.
    loaded_df = pd.read_sql_query(query, conn)

    print(f"[{datetime.datetime.now()}] '{table_name}' 테이블에서 데이터를 성공적으로 불러왔습니다.")

    # 4. 불러온 DataFrame 확인
    print("\n--- 불러온 데이터 프레임 ---")
    # print(loaded_df.head()) # 처음 5줄만 출력하여 확인
    print(loaded_df)
    print(f"\n총 데이터 건수: {len(loaded_df)} 행")
    print("\n데이터 프레임 정보:")
    loaded_df.info()

     # 5. DataFrame을 CSV 파일로 저장
    # index=False: DataFrame의 인덱스를 CSV 파일에 쓰지 않도록 합니다.

    csv_file_name = "fine_dust_data.csv" # 저장할 CSV 파일명
    loaded_df.to_csv(csv_file_name, index=False, encoding='utf-8-sig')
    print(f"\n[{datetime.datetime.now()}] 데이터를 '{csv_file_name}' 파일로 성공적으로 저장했습니다.")
    print("\n--- DB에서 데이터 불러오기 및 CSV 저장 완료 ---")

except sqlite3.Error as e:
    print(f"[{datetime.datetime.now()}] 데이터베이스 오류 발생: {e}")
except Exception as e:
    print(f"[{datetime.datetime.now()}] 알 수 없는 오류 발생: {e}")
finally:
    # 5. 데이터베이스 연결 닫기 (중요!)
    if conn:
        conn.close()
        print(f"[{datetime.datetime.now()}] 데이터베이스 연결을 닫았습니다.")