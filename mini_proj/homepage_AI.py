import streamlit as st
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
from supabase import create_client, Client
import hashlib # 비밀번호 해싱을 위한 라이브러리
import pandas as pd # 데이터 처리를 위해 pandas 추가

# 페이지 기본 설정
st.set_page_config(
    page_title="간편한 렌터카 예약",
    layout="wide", # 전체 앱은 넓은 레이아웃 유지
    initial_sidebar_state="expanded"
)

load_dotenv()

# Supabase 환경 변수 로드
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

# Supabase 클라이언트 생성
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# 비밀번호 해싱 함수 (Supabase 계정 비밀번호 저장 시 사용)
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# 페이지 상태 초기화 (이 부분은 JavaScript 주입 전에 있어야 로그인 상태를 제대로 반영할 수 있음)
if 'current_page' not in st.session_state:
    st.session_state['current_page'] = 'main'
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'user_id' not in st.session_state:
    st.session_state['user_id'] = None
if 'account_info' not in st.session_state:
    st.session_state['account_info'] = None
if 'selected_car_vin' not in st.session_state:
    st.session_state['selected_car_vin'] = None

# Python의 로그인 상태를 JavaScript로 전달
is_logged_in_for_js = 'true' if st.session_state['logged_in'] else 'false'


# JavaScript 함수 주입 (localStorage 제어) 및 Custom CSS 스타일
st.markdown(
    f"""
    <script>
    const IS_LOGGED_IN = {is_logged_in_for_js};

    function saveUserIdToLocalStorage(userId) {{
        if (window.localStorage) {{ // Check if localStorage is available
            localStorage.setItem('rentcar_user_id', userId);
            const url = new URL(window.location.href);
            url.searchParams.set('persisted_user_id', userId);
            window.history.replaceState({{}}, '', url.toString());
        }} else {{
            console.warn("localStorage is not available. Cannot save user ID.");
        }}
    }}

    function clearUserIdFromLocalStorage() {{
        if (window.localStorage) {{ // Check if localStorage is available
            localStorage.removeItem('rentcar_user_id');
            const url = new URL(window.location.href);
            url.searchParams.delete('persisted_user_id');
            window.history.replaceState({{}}, '', url.toString());
        }} else {{
            console.warn("localStorage is not available. Cannot clear user ID.");
        }}
    }}

    // 페이지 로드 시 localStorage에서 사용자 ID를 확인하고 Streamlit에 전달
    if (!window.streamlit_persisted_check_done) {{
        window.streamlit_persisted_check_done = true;
        let persistedUserId = null;
        if (window.localStorage) {{ // Check if localStorage is available
            persistedUserId = localStorage.getItem('rentcar_user_id');
        }} else {{
            console.warn("localStorage is not available on initial load.");
        }}
        
        const url = new URL(window.location.href);
        const urlParams = url.searchParams;

        if (persistedUserId && urlParams.get('persisted_user_id') !== persistedUserId) {{
            urlParams.set('persisted_user_id', persistedUserId);
            window.location.href = url.toString(); // 강제 새로고침
        }} else if (!persistedUserId && urlParams.has('persisted_user_id')) {{
            urlParams.delete('persisted_user_id');
            window.history.replaceState({{}}, '', url.toString());
        }}
    }}

    // 차량 선택 버튼 클릭 시 Streamlit에 VIN 전달 및 새로고침
    function selectCarAndRerun(vin) {{
        if (!IS_LOGGED_IN) {{
            alert('예약을 진행하려면 로그인해 주세요.');
            return; // 로그인하지 않았으면 여기서 함수 종료
        }}
        const url = new URL(window.location.href);
        url.searchParams.set('selected_car_vin_trigger', vin);
        window.location.href = url.toString(); // 강제 새로고침
    }}
    </script>

    <style>
    /* 전체 페이지 배경색 */
    body {{
        background-color: #f0f2f6; /* Streamlit 기본 배경색과 유사하게 설정 */
    }}

    /* 메인 콘텐츠 영역 너비 고정 및 중앙 정렬 */
    div.stAppViewContainer .main .block-container {{
        max-width: 1200px !important;
        margin-left: auto !important;
        margin-right: auto !important;
        padding-top: 2rem !important; /* 상단 패딩 유지 */
        padding-bottom: 2rem !important; /* 하단 패딩 유지 */
        padding-left: 1rem !important; /* 좌측 패딩 유지 */
        padding-right: 1rem !important; /* 우측 패딩 유지 */
    }}

    /* Styling for the custom "예약하기" button within the card */
    .book-now-button {{
        background-color: #007bff !important; /* 기본 파란색 */
        color: white !important;
        border-radius: 8px !important; /* 둥근 모서리 */
        padding: 10px 20px !important;
        font-size: 16px !important;
        border: none !important;
        cursor: pointer !important;
        transition: background-color 0.3s ease, transform 0.1s ease, box-shadow 0.3s ease !important; /* 부드러운 전환 효과 */
        box-shadow: 2px 2px 5px rgba(0,0,0,0.2) !important; /* 은은한 그림자 */
        width: calc(100% - 40px) !important; /* 카드 패딩 고려하여 너비 조정 */
        margin: 0 20px 20px 20px !important; /* 카드 내부 여백 조정 */
    }}

    .book-now-button:hover {{
        background-color: #0056b3 !important; /* 마우스 오버 시 더 진한 파란색 */
        transform: translateY(-2px) !important; /* 살짝 위로 뜨는 효과 */
        box-shadow: 3px 3px 8px rgba(0,0,0,0.3) !important; /* 그림자 강조 */
    }}

    /* Styling for other Streamlit buttons (e.g., "다른 차량 선택", "최종 예약하기", "로그인", "회원가입", "로그아웃") */
    div[data-testid="stButton"] button {{
        border-radius: 8px !important;
        padding: 10px 20px !important;
        font-size: 16px !important;
        transition: background-color 0.3s ease, transform 0.1s ease !important;
    }}
    div[data-testid="stButton"] button:hover {{
        transform: translateY(-1px) !important;
    }}

    /* Black border for each car information block */
    .car-card-container {{
        border: 2px solid #333 !important; /* Thicker, darker border */
        padding: 0 !important; /* 내부 패딩은 각 요소에서 조절 */
        margin-bottom: 25px !important; /* 카드 사이의 간격 */
        border-radius: 12px !important; /* 더 둥근 모서리 */
        box-shadow: 0 6px 12px rgba(0,0,0,0.2) !important; /* Stronger shadow */
        background-color: #ffffff !important; /* 카드 배경색 */
        display: flex !important;
        flex-direction: column !important; /* 세로 정렬: 내용 + 버튼 */
        align-items: flex-start !important;
        position: relative !important; /* 버튼 위치 조정을 위해 */
        height: auto !important; /* st.button 사용 시 높이 자동 조절 */
    }}

    .car-content-wrapper {{
        display: flex !important;
        align-items: center !important;
        width: 100% !important;
        padding: 20px !important; /* 이미지와 텍스트 컨텐츠의 패딩 */
        gap: 20px !important; /* 이미지와 텍스트 사이 간격 */
    }}

    .car-image-wrapper {{
        flex-shrink: 0 !important;
        width: 150px !important;
        height: 100px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        overflow: hidden !important;
        border-radius: 8px !important;
    }}

    /* st.image()가 렌더링하는 img 태그에 적용 */
    .car-image-wrapper img {{
        width: 100% !important;
        height: 100% !important;
        object-fit: cover !important;
    }}

    .car-details-text {{
        flex-grow: 1 !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: center !important;
    }}

    .car-details-text h3 {{
        margin-top: 0 !important;
        margin-bottom: 5px !important;
        font-size: 1.5em !important;
        color: #333 !important;
    }}

    .price-info {{
        display: flex !important;
        align-items: baseline !important;
        margin-bottom: 5px !important;
    }}

    .price-info .discounted-price {{
        color: red !important;
        font-size: 1.8em !important;
        font-weight: bold !important;
    }}

    .price-info .original-price {{
        font-size: 0.9em !important;
        color: #888 !important;
        text-decoration: line-through !important;
        margin-left: 10px !important;
    }}

    .price-info .discount-badge {{
        background-color: #FFEBEE !important;
        color: red !important;
        padding: 3px 8px !important;
        border-radius: 5px !important;
        font-size: 0.8em !important;
        margin-left: 10px !important;
        white-space: nowrap !important;
    }}

    .detail-text {{
        font-size: 0.9em !important;
        color: #555 !important;
        margin-top: 5px !important;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# --- JavaScript를 통해 전달된 차량 선택 트리거 처리 ---
if 'selected_car_vin_trigger' in st.query_params and st.query_params['selected_car_vin_trigger'] is not None:
    # 이 부분은 JavaScript에서 이미 로그인 여부를 확인했으므로,
    # 여기서는 단순히 selected_car_vin을 설정하고 페이지를 새로고침합니다.
    st.session_state['selected_car_vin'] = st.query_params['selected_car_vin_trigger']
    st.experimental_set_query_params(selected_car_vin_trigger=None) # 쿼리 파라미터 제거
    st.session_state['current_page'] = 'main' # 메인 페이지로 이동하여 예약 폼 표시
    st.rerun() # 변경된 세션 상태를 반영하기 위해 새로고침


# 차량 데이터 조회 함수
def read_all_car():
    """예약 가능 차량 조회 (READ)"""
    try:
        result = supabase.table('cars').select('*').eq('reservation_state', '이용 가능').execute()
        return result.data
    except Exception as e:
        st.error(f"차량 정보 조회 중 오류 발생: {e}")
        return []

# 사용자 예약 내역 조회 함수
def read_user_reservations(account_id):
    """사용자 ID에 해당하는 예약 내역 조회"""
    try:
        # 'reservations' 테이블에서 account_id가 일치하는 모든 예약 조회
        # car_vin을 통해 'cars' 테이블과 조인하여 차량 상세 정보도 함께 가져옴
        result = supabase.table('reservations').select('*, cars(car_model, car_series, car_oil_type, car_type, car_rent_price)').eq('account_id', account_id).execute()
        return result.data
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

    # 유종 필터
    oil_types = sorted(list(set([car['car_oil_type'] for car in all_cars if car['car_oil_type']])))
    selected_oil_type = st.sidebar.selectbox("유종", ["전체"] + oil_types)

    # 차종 필터
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
    if not st.session_state['selected_car_vin']:
        st.subheader("이용 가능한 차량")
        if filtered_cars:
            cols_outer = st.columns(2)
            for i, car in enumerate(filtered_cars):
                with cols_outer[i % 2]:
                    # 각 차량 정보 블록을 st.container로 감싸고 CSS 클래스 적용
                    with st.container():
                        st.markdown('<div class="car-card-container">', unsafe_allow_html=True)
                        
                        image_src_path = car.get("car_image_path", "https://placehold.co/150x100?text=No+Image")
                        car_detail_url = f"/car_details?vin={car.get('car_vin', '')}"
                        original_price = car.get('car_rent_price', 0)
                        discount_rate = 0.05
                        discounted_price = int(original_price * (1 - discount_rate))

                        # 이미지와 텍스트를 위한 내부 컬럼
                        col_img, col_details = st.columns([1, 2])
                        
                        with col_img:
                            # st.image() 사용 (use_container_width=True로 수정)
                            st.image(image_src_path, width=150, caption="", use_container_width=True)
                            st.markdown(
                                """
                                <style>
                                    /* st.image가 렌더링하는 div의 margin-bottom 제거 */
                                    div[data-testid="stImage"] {
                                        margin-bottom: 0px !important;
                                    }
                                </style>
                                """, unsafe_allow_html=True
                            )
                            
                        with col_details:
                            st.markdown(
                                f'<h3>'
                                f'<a href="{car_detail_url}" style="text-decoration: none; color: inherit;">'
                                f'{car.get("car_model", "모델명 없음")} ({car.get("car_series", "시리즈 없음")})'
                                f'</a>'
                                f'</h3>',
                                unsafe_allow_html=True
                            )
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
                            st.markdown(
                                f"""
                                <p class="detail-text">
                                    {car.get('car_model_year', 'N/A')}년식 | {car.get('car_oil_type', 'N/A')} | {car.get('car_type', 'N/A')}
                                </p>
                                """,
                                unsafe_allow_html=True
                            )
                        
                        # 예약하기 버튼 (JavaScript 함수 호출)
                        st.markdown(f"""
                            <button class="book-now-button" onclick="selectCarAndRerun('{car['car_vin']}')">예약하기</button>
                        """, unsafe_allow_html=True)
                            
                        st.markdown('</div>', unsafe_allow_html=True) # car-card-container 닫기
        else:
            st.info("선택된 필터에 해당하는 차량 데이터가 없습니다.")

    # 선택된 차량이 있을 때만 예약 폼을 표시
    if st.session_state['selected_car_vin']:
        st.markdown("---")
        st.header("예약 정보 입력")
        selected_car = next((car for car in all_cars if car['car_vin'] == st.session_state['selected_car_vin']), None)
        
        if selected_car:
            st.success(f"**{selected_car.get('car_model', '')} ({selected_car.get('car_series', '')})**을(를) 선택하셨습니다.")
            
            # 다른 차량 선택 버튼 (이 버튼은 Streamlit 기본 버튼 사용)
            if st.button("다른 차량 선택"):
                st.session_state['selected_car_vin'] = None
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
                st.subheader("예약 정보")
                
                if st.session_state['logged_in'] and st.session_state['account_info']:
                    name = st.text_input("이름", value=st.session_state['account_info'].get('account_id', ''))
                    phone = st.text_input("연락처", value=st.session_state['account_info'].get('phone_number', ''), placeholder="예: 010-XXXX-XXXX")
                else:
                    name = st.text_input("이름")
                    phone = st.text_input("연락처", placeholder="예: 010-XXXX-XXXX")

                total_price = rental_duration * selected_car.get('car_rent_price', 0)
                st.info(f"**총 예상 금액:** {rental_duration}일 x {selected_car.get('car_rent_price', 0):,}원 = **{total_price:,}원**")

                # 최종 예약하기 버튼 (이 버튼은 Streamlit 기본 버튼 사용)
                if st.button("최종 예약하기"):
                    if name and phone:
                        # Supabase에 예약 정보 저장 (가정: reservations 테이블 존재)
                        try:
                            reservation_data = {
                                "account_id": st.session_state['user_id'], # 로그인된 사용자 ID 사용
                                "car_vin": selected_car['car_vin'],
                                "start_date": str(start_date),
                                "end_date": str(end_date),
                                "total_price": total_price,
                                "reservation_date": str(datetime.now().date())
                            }
                            response = supabase.table('reservations').insert(reservation_data).execute()
                            if response.data:
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
                                # 예약 완료 후 선택된 차량 초기화
                                st.session_state['selected_car_vin'] = None
                                # st.rerun() # 예약 완료 메시지 확인을 위해 새로고침은 하지 않음
                            else:
                                st.error(f"예약 저장 중 오류가 발생했습니다: {response.status_code}")
                        except Exception as e:
                            st.error(f"예약 저장 중 오류 발생: {e}")
                    else:
                        st.warning("이름과 연락처를 모두 입력해 주세요.")
        else:
            st.error("선택한 차량 정보를 찾을 수 없습니다. 다시 시도해 주세요.")

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

        if reservations:
            # Pandas DataFrame으로 변환하여 보기 좋게 표시
            # 'cars'는 Supabase 조인 결과로 중첩된 딕셔너리 형태이므로, 이를 평탄화해야 합니다.
            processed_reservations = []
            for res in reservations:
                car_info = res.get('cars', {})
                processed_reservations.append({
                    "예약 ID": res.get('reservation_id', 'N/A'),
                    "차량 모델": car_info.get('car_model', 'N/A'),
                    "차량 시리즈": car_info.get('car_series', 'N/A'),
                    "유종": car_info.get('car_oil_type', 'N/A'),
                    "차종": car_info.get('car_type', 'N/A'),
                    "대여 날짜": res.get('start_date', 'N/A'),
                    "반납 날짜": res.get('end_date', 'N/A'),
                    "총 금액": f"{res.get('total_price', 0):,}원",
                    "예약일": res.get('reservation_date', 'N/A')
                })
            df = pd.DataFrame(processed_reservations)
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
                    response = supabase.table('accounts').select('*').eq('account_id', account_id).execute()
                    user_data = response.data
                    if user_data and user_data[0]['password'] == hashed_pw:
                        st.success(f"환영합니다, {account_id}님!")
                        st.session_state['logged_in'] = True
                        st.session_state['user_id'] = account_id
                        st.session_state['account_info'] = user_data[0]
                        st.session_state['current_page'] = 'main'
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
                        check_user = supabase.table('accounts').select('account_id').eq('account_id', account_id).execute()
                        if check_user.data:
                            st.error("이미 존재하는 계정 ID입니다. 다른 ID를 사용해 주세요.")
                        else:
                            response = supabase.table('accounts').insert({"account_id": account_id, "password": hashed_pw, "birth": birth, "phone_number": phone_number}).execute()
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
col_auth1, col_auth2, col_auth3, col_auth4 = st.columns([0.7, 0.1, 0.1, 0.1]) # 마이페이지 버튼을 위한 컬럼 추가

with col_auth1:
    if st.session_state['logged_in']:
        st.write(f"환영합니다, **{st.session_state['user_id']}**님!")
    else:
        st.write("") # 로그인 전에는 빈 공간

with col_auth2:
    # 마이페이지 버튼
    if st.button("마이페이지"):
        st.session_state['current_page'] = 'mypage'
        st.rerun()

with col_auth3:
    if st.session_state['logged_in']:
        if st.button("로그아웃"):
            st.session_state['logged_in'] = False
            st.session_state['user_id'] = None
            st.session_state['account_info'] = None
            st.session_state['current_page'] = 'main'
            st.markdown("<script>clearUserIdFromLocalStorage();</script>", unsafe_allow_html=True)
            st.rerun()
    else:
        if st.button("로그인"):
            st.session_state['current_page'] = 'login'
            st.rerun()

with col_auth4:
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
elif st.session_state['current_page'] == 'mypage':
    show_mypage()