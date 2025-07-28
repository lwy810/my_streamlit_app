import streamlit as st
from datetime import datetime, timedelta
import hashlib
import pandas as pd
from st_supabase_connection import SupabaseConnection

# 페이지 기본 설정
st.set_page_config(
    page_title="간편한 렌터카 예약",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 1. Supabase 연결 초기화
# Streamlit secrets.toml에 저장된 정보를 자동으로 로드합니다.
# cache_ttl은 쿼리 결과를 캐싱할 시간을 설정합니다. (기본값은 0, 즉 캐싱 안 함)
# conn = st.connection("supabase", type=SupabaseConnection, ttl="10m")
try:
    supabase_url = st.secrets["connections"]["supabase"]["url"]
    supabase_key = st.secrets["connections"]["supabase"]["key"]
    conn = st.connection(
        "supabase",
        type=SupabaseConnection,
        url=supabase_url,  # URL 직접 전달
        key=supabase_key,  # Key 직접 전달
        ttl="10m"
    )
except KeyError as e:
    st.error(f"Streamlit secrets에서 Supabase 연결 정보를 찾을 수 없습니다: {e}")
    st.info("`.streamlit/secrets.toml` 파일이 올바른 위치에 있는지, 형식이 맞는지 확인해주세요.")
    st.stop() # 정보가 없으면 앱 실행 중단


# 비밀번호 해싱 함수
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# 페이지 상태 초기화
if 'current_page' not in st.session_state:
    st.session_state['current_page'] = 'main'
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'user_id' not in st.session_state:
    st.session_state['user_id'] = None
if 'account_info' not in st.session_state:
    st.session_state['account_info'] = None
if 'selected_car_number' not in st.session_state:
    st.session_state['selected_car_number'] = None
if 'reservation_info' not in st.session_state:
    st.session_state['reservation_info'] = None

# --- Custom CSS and JavaScript ---
st.markdown(
    """
    <style>
    /* 전체 페이지 배경색 */
    body {
        background-color: #f0f2f6;
    }
    
    /* 메인 콘텐츠 영역 너비 고정 및 중앙 정렬 */
    div.stAppViewContainer .main .block-container {
        max-width: 1200px !important;
        margin-left: auto !important;
        margin-right: auto !important;
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }
    
    .car-card-container {
        border: 2px solid #333 !important;
        padding: 0 !important;
        margin-bottom: 25px !important;
        border-radius: 12px !important;
        box-shadow: 0 6px 12px rgba(0,0,0,0.2) !important;
        background-color: #ffffff !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: flex-start !important;
        position: relative !important;
        height: auto !important;
    }
    
    .car-content-wrapper {
        display: flex !important;
        align-items: center !important;
        width: 100% !important;
        padding: 20px !important;
        gap: 20px !important;
    }
    
    .car-image-wrapper {
        flex-shrink: 0 !important;
        width: 150px !important;
        height: 100px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        overflow: hidden !important;
        border-radius: 8px !important;
    }
    
    .car-image-wrapper img {
        width: 100% !important;
        height: 100% !important;
        object-fit: cover !important;
    }
    
    .car-details-text {
        flex-grow: 1 !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: center !important;
    }
    
    .car-details-text h3 {
        margin-top: 0 !important;
        margin-bottom: 5px !important;
        font-size: 1.5em !important;
        color: #333 !important;
    }
    
    .price-info {
        display: flex !important;
        align-items: baseline !important;
        margin-bottom: 5px !important;
    }
    
    .price-info .discounted-price {
        color: red !important;
        font-size: 1.8em !important;
        font-weight: bold !important;
    }
    
    .price-info .original-price {
        font-size: 0.9em !important;
        color: #888 !important;
        text-decoration: line-through !important;
        margin-left: 10px !important;
    }
    
    .price-info .discount-badge {
        background-color: #FFEBEE !important;
        color: red !important;
        padding: 3px 8px !important;
        border-radius: 5px !important;
        font-size: 0.8em !important;
        margin-left: 10px !important;
        white-space: nowrap !important;
    }
    
    .detail-text {
        font-size: 0.9em !important;
        color: #555 !important;
        margin-top: 5px !important;
    }

    /* Streamlit 기본 버튼 스타일 */
    div[data-testid="stButton"] button {
        background-color: #007bff !important;
        color: white !important;
        border-radius: 8px !important;
        padding: 10px 20px !important;
        font-size: 16px !important;
        border: none !important;
        cursor: pointer !important;
        transition: background-color 0.3s ease, transform 0.1s ease !important;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.2) !important;
    }
    div[data-testid="stButton"] button:hover {
        background-color: #0056b3 !important;
        transform: translateY(-2px) !important;
        box-shadow: 3px 3px 8px rgba(0,0,0,0.3) !important;
    }

    </style>
    """,
    unsafe_allow_html=True
)

# JavaScript 함수를 정의하는 HTML 마크다운
st.markdown(
    """
    <script>
    function saveUserIdToLocalStorage(userId) {
        if (window.localStorage) {
            localStorage.setItem('rentcar_user_id', userId);
        }
    }
    function clearUserIdFromLocalStorage() {
        if (window.localStorage) {
            localStorage.removeItem('rentcar_user_id');
        }
    }
    </script>
    """,
    unsafe_allow_html=True
)

# 페이지 로드 시 localStorage에서 사용자 ID 복원
# st.query_params를 이용하여 페이지 상태를 관리
if 'rentcar_user_id' in st.query_params and not st.session_state['logged_in']:
    persisted_user_id = st.query_params['rentcar_user_id']
    try:
        response = conn.table('accounts').select('*').eq('account_id', persisted_user_id).execute()
        user_data = response.data
        if user_data:
            st.session_state['logged_in'] = True
            st.session_state['user_id'] = persisted_user_id
            st.session_state['account_info'] = user_data[0]
            st.success(f"환영합니다, **{persisted_user_id}**님! (세션 복원)")
            st.query_params.clear()  # 복원 후 파라미터 정리
            st.rerun()
        else:
            st.error("저장된 사용자 정보가 유효하지 않습니다.")
    except Exception as e:
        st.error(f"세션 복원 중 오류 발생: {e}")

# 차량 데이터 조회 함수
def read_all_car():
    """예약 가능 차량 조회 (READ)"""
    try:
        result = conn.table('cars').select('*').eq('reservation_state', '이용 가능').execute()
        return result.data
    except Exception as e:
        st.error(f"차량 정보 조회 중 오류 발생: {e}")
        return []

# 사용자 예약 내역 조회 함수
def read_user_reservations(account_id):
    """사용자 ID에 해당하는 예약 내역 조회"""
    # try:
    #     result = supabase.table('reservations').select('*').eq('account_id', account_id).execute()
    #     return result.data

    try:
        # 뷰 테이블 데이터 추출
        response = conn.table('reservation_details').select('*').eq('account_id', account_id).execute()
        datas = response.data # 결과에서 실제 데이터만 추출

        if datas:
            for data in datas :
                for i in data :
                    print(data[i])

        return datas          

    except Exception as e:
        st.error(f"예약 내역 조회 중 오류 발생: {e}")
        return []
            
        

# --- 페이지별 함수 정의 ---

def show_main_page():
    all_cars = read_all_car()
    
    st.title("간편한 렌터카 예약 서비스 🚗")
    st.markdown("원하는 차량을 선택하고 간편하게 예약하세요.")
    st.markdown("---")

    # 사이드바 필터
    st.sidebar.header("차량 필터")
    oil_types = sorted(list(set([car['car_oil_type'] for car in all_cars if car['car_oil_type']])))
    selected_oil_type = st.sidebar.selectbox("유종", ["전체"] + oil_types)
    car_types = sorted(list(set([car['car_type'] for car in all_cars if car['car_type']])))
    selected_car_type = st.sidebar.selectbox("차종", ["전체"] + car_types)

    # 필터링된 차량 목록
    filtered_cars = []
    for car in all_cars:
        match_oil_type = (selected_oil_type == "전체") or (car['car_oil_type'] == selected_oil_type)
        match_car_type = (selected_car_type == "전체") or (car['car_type'] == selected_car_type)
        if match_oil_type and match_car_type:
            filtered_cars.append(car)

    # 선택된 차량이 없을 때만 차량 목록을 표시
    if not st.session_state['selected_car_number']:
        st.subheader("이용 가능한 차량")
        if filtered_cars:
            cols_outer = st.columns(2)
            for i, car in enumerate(filtered_cars):
                with cols_outer[i % 2]:
                    with st.container():
                        st.markdown('<div class="car-card-container">', unsafe_allow_html=True)
                        
                        image_src_path = car.get("car_image_path", "https://placehold.co/150x100?text=No+Image")
                        original_price = car.get('car_rent_price', 0)
                        discount_rate = 0.05
                        discounted_price = int(original_price * (1 - discount_rate))

                        col_img, col_details = st.columns([1, 2])
                        with col_img:
                            st.image(image_src_path, width=150, caption="", use_container_width=True)
                        with col_details:
                            st.markdown(f'<h3>{car.get("car_model", "모델명 없음")} ({car.get("car_series", "시리즈 없음")})</h3>', unsafe_allow_html=True)
                            st.markdown(
                                f"""
                                <div class="price-info">
                                    <span class="discounted-price">{discounted_price:,.0f}원</span>
                                    <span class="original-price">{original_price:,.0f}원</span>
                                    <span class="discount-badge">{int(discount_rate * 100)}% 할인</span>
                                </div>
                                """,
                                unsafe_allow_html=True
                            )
                            st.markdown(f'<p class="detail-text">{car.get("car_model_year", "N/A")}년식 | {car.get("car_oil_type", "N/A")} | {car.get("car_type", "N/A")}</p>', unsafe_allow_html=True)

                        if st.button("예약하기", key=f"book_button_{car['car_number']}"):
                            if not st.session_state['logged_in']:
                                st.warning("로그인 후 이용 가능합니다.")
                                st.session_state['current_page'] = 'login'
                                st.rerun()
                            else:
                                st.session_state['selected_car_number'] = car['car_number']
                                st.rerun()

                        st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("선택된 필터에 해당하는 차량 데이터가 없습니다.")

    # 선택된 차량이 있을 때만 예약 폼을 표시
    if st.session_state['selected_car_number']:
        st.markdown("---")
        st.header("예약 정보 입력")
        selected_car = next((car for car in all_cars if car['car_number'] == st.session_state['selected_car_number']), None)
        
        if selected_car:
            st.success(f"**{selected_car.get('car_model', '')} ({selected_car.get('car_series', '')})**을(를) 선택하셨습니다.")
            
            if st.button("다른 차량 선택"):
                st.session_state['selected_car_number'] = None
                st.rerun()

            col1, col2 = st.columns(2)
            today = datetime.now().date()
            
            with col1:
                start_date = st.date_input("대여 날짜", min_value=today)
            with col2:
                end_date = st.date_input("반납 날짜", min_value=start_date)

            if end_date < start_date:
                st.error("반납 날짜는 대여 날짜보다 이전일 수 없습니다.")
            else:
                rental_duration = (end_date - start_date).days + 1
                
                st.markdown("---")
                st.subheader("예약자 정보")
                
                if st.session_state['logged_in'] and st.session_state['account_info']:
                    name = st.text_input("이름", value=st.session_state['account_info'].get('account_id', ''))
                    phone = st.text_input("연락처", value=st.session_state['account_info'].get('phone_number', ''), placeholder="예: 010-XXXX-XXXX")
                else:
                    name = st.text_input("이름")
                    phone = st.text_input("연락처", placeholder="예: 010-XXXX-XXXX")

                total_price = rental_duration * selected_car.get('car_rent_price', 0)
                st.info(f"**총 예상 금액:** {rental_duration}일 x {selected_car.get('car_rent_price', 0):,}원 = **{total_price:,}원**")

                if st.button("최종 예약하기"):
                    if name and phone:
                        try:
                            reservation_data = {
                                "account_id": st.session_state['user_id'],
                                "car_number": selected_car['car_number'],
                                "rent_reservation_start_date": str(start_date),
                                "rent_reservation_end_date": str(end_date),
                                "rent_reservation_price": total_price
                            }
                            response = conn.table('reservations').insert(reservation_data).execute()
                            if response.data:
                                st.session_state['reservation_info'] = {
                                    'car_model': selected_car.get('car_model', ''),
                                    'car_series': selected_car.get('car_series', ''),
                                    'rent_reservation_start_date': str(start_date),
                                    'rent_reservation_end_date': str(end_date),
                                    'rental_duration': rental_duration,
                                    'name': name,
                                    'phone': phone,
                                    'rent_reservation_price': total_price
                                }
                                st.session_state['current_page'] = 'confirmation'
                                st.rerun()
                            else:
                                st.error(f"예약 저장 중 오류가 발생했습니다: {response.status_code}")
                        except Exception as e:
                            st.error(f"예약 저장 중 오류 발생: {e}")
                    else:
                        st.warning("이름과 연락처를 모두 입력해 주세요.")
        else:
            st.error("선택한 차량 정보를 찾을 수 없습니다. 다시 시도해 주세요.")

def show_confirmation_page():
    st.balloons()
    st.title("예약 완료 🎉")
    st.markdown("---")
    st.success("🎉 **예약이 성공적으로 완료되었습니다!**")
    
    if st.session_state.get('reservation_info'):
        info = st.session_state['reservation_info']
        st.write("### 예약 상세 정보")
        st.write(f"**차량:** {info['car_model']} ({info['car_series']})")
        st.write(f"**대여 기간:** {info['start_date']} ~ {info['end_date']} ({info['rental_duration']}일)")
        st.write(f"**예약자:** {info['name']}")
        st.write(f"**연락처:** {info['phone']}")
        st.write(f"**최종 금액:** {info['total_price']:,}원")
        st.write("예약 확정 문자를 보내드릴게요. 감사합니다!")
    else:
        st.warning("예약 정보가 없습니다.")
        
    if st.button("메인 페이지로 돌아가기"):
        st.session_state['selected_car_number'] = None
        st.session_state['reservation_info'] = None
        st.session_state['current_page'] = 'main'
        st.rerun()

def show_mypage():
    st.title("마이페이지 👤")
    st.markdown("나의 예약 내역을 확인하세요.")
    st.markdown("---")

    if not st.session_state['logged_in']:
        st.warning("예약 내역을 확인하려면 로그인해 주세요.")
        if st.button("로그인 페이지로 이동"):
            st.session_state['current_page'] = 'login'
            st.rerun()
    else:
        user_id = st.session_state['user_id']
        st.subheader(f"**{user_id}**님의 예약 내역")
        
        reservations = read_user_reservations(user_id)

        st.write("#### 조인된 예약 데이터:")
        # 데이터를 보기 좋게 테이블 형태로 표시
        display_data = []

        for reservation in reservations:
            display_data.append({
                "차량 번호": reservation.get('car_number'),
                "계정 ID": reservation.get('account_id'),
                "예약 시작일": reservation.get('rent_reservation_start_date'),
                "예약 종료일": reservation.get('rent_reservation_end_date'),
                "예약 상태": reservation.get('rent_reservation_state'),
                "예약 가격": reservation.get('rent_reservation_price'),
                "차량 유형": reservation.get('car_type'), 
                "차량 모델": reservation.get('car_model'), 
                "차량 시리즈": reservation.get('car_series'),
                "차량 연식": reservation.get('car_model_year'), 
                "차량 유종": reservation.get('car_oil_type'),
                "차량 색상": reservation.get('car_color')
            })
             
            df = pd.DataFrame(display_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("예약 내역이 없습니다.")
    
    st.markdown("---")
    if st.button("메인 페이지로 돌아가기"):
        st.session_state['current_page'] = 'main'
        st.rerun()

def show_login_page():
    col_left, col_center, col_right = st.columns([1, 4, 1])
    with col_center:
        st.title("로그인 🔑")
        st.markdown("계정 ID와 비밀번호를 입력하여 로그인하세요.")
        with st.form("login_form"):
            account_id = st.text_input("계정 ID")
            password = st.text_input("비밀번호", type="password")
            submitted = st.form_submit_button("로그인")
            if submitted:
                hashed_pw = hash_password(password)
                try:
                    response = conn.table('accounts').select('*').eq('account_id', account_id).execute()
                    user_data = response.data
                    if user_data and user_data[0]['password'] == hashed_pw:
                        st.success(f"환영합니다, {account_id}님!")
                        st.session_state['logged_in'] = True
                        st.session_state['user_id'] = account_id
                        st.session_state['account_info'] = user_data[0]
                        st.session_state['current_page'] = 'main'
                        # JavaScript로 로컬 스토리지에 저장
                        st.markdown(f"<script>saveUserIdToLocalStorage('{account_id}');</script>", unsafe_allow_html=True)
                        st.rerun()
                    else:
                        st.error("계정 ID 또는 비밀번호가 일치하지 않습니다.")
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
    col_left, col_center, col_right = st.columns([1, 4, 1])
    with col_center:
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
                        check_user = conn.table('accounts').select('account_id').eq('account_id', account_id).execute()
                        if check_user.data:
                            st.error("이미 존재하는 계정 ID입니다. 다른 ID를 사용해 주세요.")
                        else:
                            response = conn.table('accounts').insert({"account_id": account_id, "password": hashed_pw, "birth": birth, "phone_number": phone_number}).execute()
                            if response.data:
                                st.success("회원가입이 성공적으로 완료되었습니다! 로그인해 주세요.")
                                st.session_state['current_page'] = 'login'
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
col_auth1, col_auth2, col_auth3, col_auth4 = st.columns([0.7, 0.1, 0.1, 0.1])

with col_auth1:
    if st.session_state['logged_in']:
        st.write(f"환영합니다, **{st.session_state['user_id']}**님!")
    else:
        st.write("")

with col_auth2:
    if st.button("마이페이지", key="mypage_button"):
        st.session_state['current_page'] = 'mypage'
        st.rerun()

with col_auth3:
    if st.session_state['logged_in']:
        if st.button("로그아웃", key="logout_button"):
            st.session_state['logged_in'] = False
            st.session_state['user_id'] = None
            st.session_state['account_info'] = None
            st.session_state['current_page'] = 'main'
            st.markdown("<script>clearUserIdFromLocalStorage();</script>", unsafe_allow_html=True)
            st.rerun()
    else:
        if st.button("로그인", key="login_button"):
            st.session_state['current_page'] = 'login'
            st.rerun()

with col_auth4:
    if not st.session_state['logged_in']:
        if st.button("회원가입", key="signup_button"):
            st.session_state['current_page'] = 'signup'
            st.rerun()

# 현재 페이지 상태에 따라 적절한 함수 호출
if st.session_state['current_page'] == 'main':
    show_main_page()
elif st.session_state['current_page'] == 'login':
    show_login_page()
elif st.session_state['current_page'] == 'signup':
    show_signup_page()
elif st.session_state['current_page'] == 'mypage':
    show_mypage()
elif st.session_state['current_page'] == 'confirmation':
    show_confirmation_page()