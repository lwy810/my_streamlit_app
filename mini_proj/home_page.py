import streamlit as st
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
from supabase import create_client, Client
import pandas as pd
import hashlib


# 페이지 기본 설정
st.set_page_config(
    page_title="간편한 렌터카 예약",
    layout="wide",
    initial_sidebar_state="expanded"
)

load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# 페이지 상태 초기화
if 'current_page' not in st.session_state:
    st.session_state['current_page'] = 'main'
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'user_id' not in st.session_state:
    st.session_state['user_id'] = None
if 'account_info' not in st.session_state: # 새롭게 추가된 account_info 초기화
    st.session_state['account_info'] = None

# 차량 데이터 조회 함수
def read_all_car():
    """예약 가능 차량 조회 (READ)"""
    try:
        result = supabase.table('cars').select('*').eq('reservation_state', '이용 가능').execute()
        cars = result.data
        
        print("\n=== 전체 차량 목록 ===")
        if cars:
            for car in cars:
                print(f"차량 : {car['car_model']}, 유종: {car['car_oil_type']}, path: {car['car_image_path']}")
        else:
            print("등록된 차량이 없습니다.")
        
        return cars
        
    except Exception as e:
        st.error(f"차량 정보 조회 중 오류 발생: {e}")
        return []

# --- 페이지별 함수 정의 ---

def show_main_page():
    # Supabase에서 차량 데이터 로드
    cars = read_all_car()
    
    # 제목 및 설명
    st.title("간편한 렌터카 예약 서비스 🚗")
    st.markdown("원하는 차량을 선택하고 간편하게 예약하세요.")
    st.markdown("---")

    # 차량 목록 표시
    if cars:
        st.subheader("이용 가능한 차량")

        # 2개의 컬럼을 생성하여 차량을 2열로 표시
        cols_outer = st.columns(3) 
        
        # 각 차량 정보를 이미지와 같은 형식으로 표시
        for i, car in enumerate(cars):
            # 현재 차량을 어떤 외부 컬럼에 넣을지 결정 (i % 2)
            with cols_outer[i % 2]:
                # 내부적으로 이미지와 텍스트를 위한 2개의 컬럼을 다시 생성
                col1, col2 = st.columns([1, 2]) 

                # 각 차량의 상세 페이지 URL (예시: 실제 웹사이트 구조에 따라 변경 필요)
                car_detail_url = f"/car_details?vin={car.get('car_vin', '')}"
                
                # car_image_path는 이제 외부 URL이라고 가정합니다.
                image_src_path = car.get("car_image_path", "https://placehold.co/150x100?text=No+Image")

                with col1:
                    # 이미지 표시 (외부 URL 사용)
                    st.image(image_src_path, width=150, caption=car.get('car_model', ''))
                    
                with col2:
                    # 모델명과 시리즈를 클릭 가능한 링크로 만들기
                    st.markdown(
                        f'### <a href="{car_detail_url}" style="text-decoration: none; color: inherit;">'
                        f'{car.get("car_model", "모델명 없음")} ({car.get("car_series", "시리즈 없음")})'
                        f'</a>',
                        unsafe_allow_html=True
                    )

                    # 가격 정보 (할인율은 임의로 적용)
                    original_price = car.get('car_rent_price', 0)
                    discount_rate = 0.05 # 5% 할인 예시
                    discounted_price = int(original_price * (1 - discount_rate))

                    # 가격 표시 (빨간색, 큰 글씨, 취소선, 할인율) - 전체를 a 태그로 감쌈
                    st.markdown(
                        f"""
                        <a href="{car_detail_url}" style="text-decoration: none; color: inherit;">
                            <div style="display: flex; align-items: baseline;">
                                <span style="color: red; font-size: 1.8em; font-weight: bold;">{discounted_price:,.0f}원</span>
                                <span style="font-size: 0.9em; color: #888; text-decoration: line-through; margin-left: 10px;">{original_price:,.0f}원</span>
                                <span style="background-color: #FFEBEE; color: red; padding: 3px 8px; border-radius: 5px; font-size: 0.8em; margin-left: 10px;">{int(discount_rate * 100)}% 할인</span>
                            </div>
                        </a>
                        """,
                        unsafe_allow_html=True
                    )

                    # 상세 정보 (연식 | 유종 | 승차인원)
                    st.markdown(
                        f"""
                        <a href="{car_detail_url}" style="text-decoration: none; color: inherit;">
                            <p style="font-size: 0.9em; color: #555;">
                                {car.get('car_model_year', 'N/A')}년식 | {car.get('car_oil_type', 'N/A')} | {car.get('car_type', 'N/A')}
                            </p>
                        </a>
                        """,
                        unsafe_allow_html=True
                    )
                st.markdown("---") # 각 차량 정보 구분선 (내부 컬럼에 적용)

    else:
        st.info("표시할 차량 데이터가 없습니다.")

# 예약 폼 (이전 코드와 동일)
    st.markdown("---")
    st.header("예약하기")

    # 선택된 차량 ID 저장 (Supabase에서 가져온 데이터는 car_vin으로 식별)
    selected_car_vin = None
    for car in cars:
        # 각 차량에 대한 '선택하기' 버튼을 생성하고, 클릭 시 해당 차량의 car_vin을 세션 상태에 저장
        # 이 버튼은 차량 목록 아래에 한 줄로 표시됩니다.
        if st.button(f"{car.get('car_model', '')} ({car.get('car_series', '')}) 선택하기", key=f"select_{car.get('car_vin', '')}"):
            selected_car_vin = car.get('car_vin')
            st.session_state['selected_car_vin'] = selected_car_vin
            break # 버튼 클릭 시 루프 종료

    # 세션 상태에서 선택된 차량 VIN 가져오기
    if 'selected_car_vin' in st.session_state and st.session_state['selected_car_vin']:
        selected_car_vin = st.session_state['selected_car_vin']
        selected_car = next((car for car in cars if car['car_vin'] == selected_car_vin), None)
    else:
        selected_car = None

    if selected_car:
        st.success(f"**{selected_car.get('car_model', '')} ({selected_car.get('car_series', '')})**을(를) 선택하셨습니다. 아래 폼을 작성해 주세요.")

        # 날짜 입력 위젯
        col1, col2 = st.columns(2)
        today = datetime.now().date()
        
        with col1:
            start_date = st.date_input("대여 날짜", min_value=today)
        with col2:
            end_date = st.date_input("반납 날짜", min_value=start_date)

        # 대여 기간 계산
        if end_date < start_date:
            st.error("반납 날짜는 대여 날짜보다 이전일 수 없습니다.")
        else:
            rental_duration = (end_date - start_date).days + 1
            
            # 예약 정보 입력
            st.markdown("---")
            st.subheader("예약 정보")
            name = st.text_input("이름")
            phone = st.text_input("연락처", placeholder="예: 010-1234-5678")

            # 최종 가격 계산
            if selected_car:
                total_price = rental_duration * selected_car.get('car_rent_price', 0)
                st.info(f"**총 예상 금액:** {rental_duration}일 x {selected_car.get('car_rent_price', 0):,}원 = **{total_price:,}원**")

            # 예약 확인 버튼
            if st.button("예약하기"):
                if name and phone:
                    st.balloons()
                    st.success("🎉 **예약이 완료되었습니다!** 🎉")
                    st.write("---")
                    st.write("### 예약 상세 정보")
                    st.write(f"**차량:** {selected_car.get('car_model', '')} ({selected_car.get('car_series', '')})")
                    st.write(f"**대여 기간:** {start_date} ~ {end_date} ({rental_duration}일)")
                    st.write(f"**예약자:** {name}")
                    st.write(f"**연락처:** {phone}")
                    st.write(f"**최종 금액:** {total_price:,}원")
                    st.write("예약 확정 문자를 보내드릴게요. 감사합니다!")
                else:
                    st.warning("이름과 연락처를 모두 입력해 주세요.")
    else:
        st.info("위에서 차량을 먼저 선택해 주세요.")

def show_login_page():
    # 로그인 폼을 중앙에 좁게 배치하기 위한 컬럼 설정
    # col_left와 col_right는 여백을 위해 사용되며, 직접적인 콘텐츠는 col_center에 배치
    col_left, col_center, col_right = st.columns([1, 4, 1]) # 1:4:1 비율로 중앙 컬럼을 넓게 (전체 너비의 약 66%)

    with col_center: # 모든 UI 요소를 이 블록 안에 배치하여 중앙 정렬 효과
        st.title("로그인 🔑")
        st.markdown("계정 ID와 비밀번호를 입력하여 로그인하세요.")

        with st.form("login_form"):
            account_id = st.text_input("계정 ID")
            password = st.text_input("비밀번호", type="password")
            submitted = st.form_submit_button("로그인")

            if submitted:
                hashed_pw = hash_password(password)
                try:
                    response = supabase.table('accounts').select('*').eq('account_id', account_id).execute()
                    user_data = response.data

                    if user_data:
                        # 실제 비밀번호와 해싱된 비밀번호 비교
                        if user_data[0]['password'] == hashed_pw:
                            st.success(f"환영합니다, {account_id}님!")
                            st.session_state['logged_in'] = True
                            st.session_state['user_id'] = account_id
                            st.session_state['account_info'] = user_data[0] # 로그인 성공 시 전체 계정 정보 저장
                            st.session_state['current_page'] = 'main' # 로그인 성공 시 메인 페이지로 이동
                            st.rerun() # 페이지 새로고침
                        else:
                            st.error("비밀번호가 일치하지 않습니다.")
                    else:
                        st.error("등록되지 않은 계정 ID입니다.")
                except Exception as e:
                    st.error(f"로그인 중 오류 발생: {e}")

        st.markdown("---")
        if st.button("회원가입 페이지로 이동"):
            st.session_state['current_page'] = 'signup'
            st.rerun()
        if st.button("메인 페이지로 돌아가기"):
            st.session_state['current_page'] = 'main'
            st.rerun()

def show_signup_page():
    # 회원가입 폼을 중앙에 좁게 배치하기 위한 컬럼 설정
    # col_left와 col_right는 여백을 위해 사용되며, 직접적인 콘텐츠는 col_center에 배치
    col_left, col_center, col_right = st.columns([1, 4, 1]) # 1:4:1 비율로 중앙 컬럼을 넓게 (전체 너비의 약 66%)
    
    with col_center: # 모든 UI 요소를 이 블록 안에 배치하여 중앙 정렬 효과
        st.title("회원가입 📝")
        st.markdown("새로운 계정을 생성하세요.")

        with st.form("signup_form"):
            account_id = st.text_input("계정 ID (이메일 주소 권장)")
            password = st.text_input("비밀번호", type="password")
            confirm_password = st.text_input("비밀번호 확인", type="password")
            birth = st.text_input("생년월일 (YYYY-MM-DD)")
            phone_number = st.text_input("휴대폰 번호 (010-XXXX-XXXX)")
            submitted = st.form_submit_button("회원가입")

            if submitted:
                if not (account_id and password and confirm_password and birth and phone_number):
                    st.warning("모든 필드를 입력해 주세요.")
                elif password != confirm_password:
                    st.error("비밀번호가 일치하지 않습니다.")
                else:
                    hashed_pw = hash_password(password)
                    try:
                        # 계정 ID 중복 확인
                        check_user = supabase.table('accounts').select('account_id').eq('account_id', account_id).execute()
                        if check_user.data:
                            st.error("이미 존재하는 계정 ID입니다. 다른 ID를 사용해 주세요.")
                        else:
                            # 새 계정 삽입
                            response = supabase.table('accounts').insert({
                                "account_id": account_id,
                                "password": hashed_pw, # 실제 서비스에서는 더 강력한 해싱 필요
                                "birth": birth,
                                "phone_number": phone_number
                            }).execute()

                            if response.data:
                                st.success("회원가입이 성공적으로 완료되었습니다! 로그인해 주세요.")
                                st.session_state['current_page'] = 'login' # 회원가입 성공 시 로그인 페이지로 이동
                                st.rerun()
                            else:
                                st.error(f"회원가입 중 오류가 발생했습니다: {response.status_code}")
                    except Exception as e:
                        st.error(f"회원가입 중 오류 발생: {e}")

        st.markdown("---")
        if st.button("로그인 페이지로 이동"):
            st.session_state['current_page'] = 'login'
            st.rerun()
        if st.button("메인 페이지로 돌아가기"):
            st.session_state['current_page'] = 'main'
            st.rerun()

# --- 페이지 렌더링 로직 ---

# 상단에 로그인/회원가입 버튼 배치
col_auth1, col_auth2, col_auth3 = st.columns([0.8, 0.1, 0.1]) # 좌측 여백을 크게 줌

with col_auth1:
    if st.session_state['logged_in']:
        st.write(f"환영합니다, **{st.session_state['user_id']}**님!")
    else:
        st.write("") # 로그인 전에는 빈 공간

with col_auth2:
    if st.session_state['logged_in']:
        if st.button("로그아웃"):
            st.session_state['logged_in'] = False
            st.session_state['user_id'] = None
            st.session_state['account_info'] = None # 로그아웃 시 계정 정보 초기화
            st.session_state['current_page'] = 'main'
            st.rerun()
    else:
        if st.button("로그인"):
            st.session_state['current_page'] = 'login'
            st.rerun()

with col_auth3:
    if not st.session_state['logged_in']:
        if st.button("회원가입"):
            st.session_state['current_page'] = 'signup'
            st.rerun()

# 현재 페이지 상태에 따라 적절한 함수 호출
if st.session_state['current_page'] == 'main':
    show_main_page()
elif st.session_state['current_page'] == 'login':
    show_login_page()
elif st.session_state['current_page'] == 'signup':
    show_signup_page()
