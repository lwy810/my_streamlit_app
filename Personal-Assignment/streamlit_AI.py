import streamlit as st
from assignment1 import crawl_global_it_news
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

st.set_page_config(
    page_title="메인 페이지: 작업 실행",
    layout="centered"
)

# --- st.session_state 초기화 ---
# 앱이 처음 시작될 때만 실행됩니다.
if 'type_option' not in st.session_state:
    st.session_state['type_option'] = "1. 유형을 선택하세요."
if 'area1_option' not in st.session_state:
    st.session_state['area1_option'] = "2. 도시(도/시)를 선택하세요."
if 'area2_option' not in st.session_state:
    st.session_state['area2_option'] = "3. 구를 선택하세요."
if 'area3_option' not in st.session_state:
    st.session_state['area3_option'] = "4. 동을 선택하세요."
if 'trade_type_option' not in st.session_state:
    st.session_state['trade_type_option'] = "5. 거래 유형을 선택하세요."
if 'volumn_option' not in st.session_state:
    st.session_state['volumn_option'] = "6. 면적(평)을 선택하세요."
if 'budget' not in st.session_state:
    st.session_state['budget'] = "" # 예산 초기값은 빈 문자열
if 'for_sale_data' not in st.session_state:
    st.session_state['for_sale_data'] = [] # 검색 결과 데이터 초기화

invisible_sidebar_css = """
<style>
    .stSidebar {
        display: none !important;
    }
</style>
"""

visible_sidebar_css = """
<style>
    .stSidebar {
        display: block !important;
    }
</style>
"""

st.markdown(invisible_sidebar_css, unsafe_allow_html=True)


# 제목 설정
st.markdown("<h2>직장인/신혼부부 맞춤 부동산 매물 Search</h2>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# 초기값 설정 (사용자 선택 값 또는 기본값)
# 주의: 이 전역 변수들은 session_state에서 값을 가져오는 임시 저장소 역할입니다.
# 실제 위젯의 상태는 session_state를 통해 관리됩니다.
for_sale_list = []

area1_group = ["2. 도시(도/시)를 선택하세요.", "서울시", "경기도", "인천시", "광주시"]

area2_group = [
    ["3. 구를 선택하세요."],
    ["3. 구를 선택하세요.", "강남구", "강동구", "강북구", "강서구", "관악구", "광진구", "서초구", "송파구", "양천구"],
    ["3. 구를 선택하세요.", "수원시 장안구", "수원시 권선구", "수원시 팔달구", "수원시 영통구", "용인시 처인구", "용인시 수지구", "용인시 기흥구", "성남시 분당구", "성남시 수정구"],
    ["3. 구를 선택하세요.", "남동구", "부평구", "계양구", "연수구", "중구", "동구", "미추홀구", "서구"],
    ["3. 구를 선택하세요.", "광산구", "남구", "동구", "북구", "서구"]
]

area3_group = [
    ["4. 동을 선택하세요."],
    ["4. 동을 선택하세요.", "역삼동", "삼성동", "청담동", "신사동", "논현동", "도곡동", "압구정동", "수서동", "대치동", "세곡동"],
    ["4. 동을 선택하세요.", "둔촌동", "성내동", "암사동", "천호동"],
    ["4. 동을 선택하세요.", "미아동", "번동", "수유동", "우이동"],
    ["4. 동을 선택하세요.", "화곡동", "가양동", "등촌동", "염창동"],
    ["4. 동을 선택하세요.", "봉천동", "신림동", "남현동"],
    ["4. 동을 선택하세요.", "광진동", "중곡동", "군자동"],
    ["4. 동을 선택하세요.", "서초동", "방배동", "양재동"],
    ["4. 동을 선택하세요.", "잠실동", "송파동", "가락동"],
    ["4. 동을 선택하세요.", "목동", "신월동", "염창동"],
    ["4. 동을 선택하세요.", "매탄동", "영통동", "권선동"],
    ["4. 동을 선택하세요.", "세류동", "권선동"],
    ["4. 동을 선택하세요.", "매교동", "인계동"],
    ["4. 동을 선택하세요.", "영통동", "원천동"],
    ["4. 동을 선택하세요.", "김량장동", "역북동", "삼가동", "모현읍", "남사면", "포곡읍"],
    ["4. 동을 선택하세요.", "풍덕천동", "상현동"],
    ["4. 동을 선택하세요.", "기흥동", "구갈동"],
    ["4. 동을 선택하세요.", "정자동", "서현동"],
    ["4. 동을 선택하세요.", "신흥동", "수진동"],
    ["4. 동을 선택하세요.", "간석동", "논현동", "구월동"],
    ["4. 동을 선택하세요.", "부평동", "산곡동"],
    ["4. 동을 선택하세요.", "계산동", "작전동"],
    ["4. 동을 선택하세요.", "연수동", "옥련동"],
    ["4. 동을 선택하세요.", "중앙동", "신포동"],
    ["4. 동을 선택하세요.", "화평동", "송림동"],
    ["4. 동을 선택하세요.", "학익동", "용현동"],
    ["4. 동을 선택하세요.", "가좌동", "검암동"],
    ["4. 동을 선택하세요.", "신창동", "첨단동"],
    ["4. 동을 선택하세요.", "월산동", "봉선동"],
    ["4. 동을 선택하세요.", "운남동", "지원동"],
    ["4. 동을 선택하세요.", "두암동", "동림동"],
    ["4. 동을 선택하세요.", "농성동", "화정동"]
]

# --- 위젯 초기값을 st.session_state에서 가져오도록 수정 ---

# 유형
type_select = ["1. 유형을 선택하세요.", "직장인", "신혼부부"]
# 현재 session_state에 저장된 값의 인덱스를 찾아 index로 설정
type_option_index = type_select.index(st.session_state['type_option']) if st.session_state['type_option'] in type_select else 0
type_option = st.selectbox("유형 선택", type_select, index=type_option_index, label_visibility="hidden", key="type_option_widget")
st.session_state['type_option'] = type_option # 선택된 값을 session_state에 다시 저장

# 도시(도/시) 입력
if st.session_state['type_option'] != "1. 유형을 선택하세요." :
    area1_option_index = area1_group.index(st.session_state['area1_option']) if st.session_state['area1_option'] in area1_group else 0
    area1_option = st.selectbox("2. 도시(도/시)를 선택하세요.", area1_group, index=area1_option_index, label_visibility="hidden", key="area1_option_widget")
    st.session_state['area1_option'] = area1_option

# 구 입력
    if st.session_state['area1_option'] != "2. 도시(도/시)를 선택하세요." :
        area2_current_group = area2_group[area1_group.index(st.session_state['area1_option'])]
        area2_option_index = area2_current_group.index(st.session_state['area2_option']) if st.session_state['area2_option'] in area2_current_group else 0
        area2_option = st.selectbox("3. 구를 선택하세요.", area2_current_group, index=area2_option_index, label_visibility="hidden", key="area2_option_widget" )
        st.session_state['area2_option'] = area2_option

# 동 입력
        if st.session_state['area2_option'] != "3. 구를 선택하세요." :
            area2_index_for_area3 = area1_group.index(st.session_state['area1_option'])
            area3_index_offset = area2_group[area2_index_for_area3].index(st.session_state['area2_option'])
            
            # area3_group 인덱스 계산 로직 유지
            current_area3_group_index = area2_group[area2_index_for_area3].index(st.session_state['area2_option'])
            if area2_index_for_area3 == 2:
                current_area3_group_index += 9
            elif area2_index_for_area3 == 3:
                current_area3_group_index += 18
            elif area2_index_for_area3 == 4:
                current_area3_group_index += 27
            
            area3_current_group = area3_group[current_area3_group_index]
            area3_option_index = area3_current_group.index(st.session_state['area3_option']) if st.session_state['area3_option'] in area3_current_group else 0
            area3_option = st.selectbox("4. 동을 선택하세요.", area3_current_group, index=area3_option_index, label_visibility="hidden", key="area3_option_widget" )
            st.session_state['area3_option'] = area3_option

# 거래 유형 입력
            if st.session_state['area3_option'] != "4. 동을 선택하세요." :
                trade_type_select = ["5. 거래 유형을 선택하세요.", "전체", "매매", "전세", "월세"]
                trade_type_option_index = trade_type_select.index(st.session_state['trade_type_option']) if st.session_state['trade_type_option'] in trade_type_select else 0
                trade_type_option = st.selectbox("5. 거래 유형을 선택하세요.", trade_type_select, index=trade_type_option_index, label_visibility="hidden", key="trade_type_option_widget")
                st.session_state['trade_type_option'] = trade_type_option

# 면적 입력
                if st.session_state['trade_type_option'] != "5. 거래 유형을 선택하세요." :
                    volumn_select = ["6. 면적(평)을 선택하세요.", "10평", "20평", "30평", "40평", "50평", "60평"]
                    volumn_option_index = volumn_select.index(st.session_state['volumn_option']) if st.session_state['volumn_option'] in volumn_select else 0
                    volumn_option = st.selectbox("6. 면적(평)을 선택하세요.", volumn_select, index=volumn_option_index, label_visibility="hidden", key="volumn_option_widget" )
                    st.session_state['volumn_option'] = volumn_option

# 예산 입력
                    if st.session_state['volumn_option'] != "6. 면적(평)을 선택하세요." :
                        # st.text_input에 value 파라미터를 사용하여 session_state 값 설정
                        budget = st.text_input("7. 예산을 입력하세요(단위:만원)", value=st.session_state['budget'], key="budget_widget")
                        st.session_state['budget'] = budget # 입력된 값을 session_state에 저장

                        budget_int = 0
                        try : 
                            if budget: # budget이 비어있지 않을 때만 변환 시도
                                budget_int = int(budget)
                        except Exception as e :
                            st.markdown("<p> 숫자를 입력해주세요 </p>", unsafe_allow_html=True)
                        
                        if budget and len(str(budget_int)) > 8 : # 조 단위
                            st.write(f"입력한 예산: {float(budget_int)/100000000}조")
                        elif budget and len(str(budget_int)) > 4 : # 억 단위
                            st.write(f"입력한 예산: {float(budget_int)/10000}억")
                        elif budget: # 만원 단위
                            st.write(f"입력한 예산: {budget_int}만원")


                        if budget: # budget이 입력되었을 때만 검색 버튼 표시
                            if st.button("매물 검색"):
                                parameter = [st.session_state['type_option'], st.session_state['area1_option'], 
                                             st.session_state['area2_option'], st.session_state['area3_option'], 
                                             st.session_state['volumn_option'], st.session_state['budget'], 
                                             st.session_state['trade_type_option']]
                                try:
                                    for_sale_list = crawl_global_it_news(parameter)
                                    st.success("크롤링 검색 중!")
                                    
                                    if for_sale_list == [] :
                                        st.info("검색된 매물이 없습니다. 조건을 다시 확인해주세요.")

                                except Exception as e:
                                    st.error("죄송합니다. 오류 체크 중입니다.")
                                    st.text(f"에러 내용: {e}")


if for_sale_list: # 데이터가 실제로 있다면
    st.session_state['for_sale_data'] = for_sale_list # 데이터를 세션 상태에 저장
    
if st.session_state.get('for_sale_data') != [] :
    st.success("매물 찾기 성공!")
    st.markdown(visible_sidebar_css, unsafe_allow_html=True)
    if st.button("리포트 페이지") :
        st.switch_page("pages/report.py")