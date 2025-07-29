import streamlit as st
import logging
from playwright.sync_api import sync_playwright # Playwright 동기 API 임포트
import time
import csv
from datetime import datetime

# 로깅 설정: INFO 레벨 이상의 메시지를 출력
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Streamlit 페이지 설정
st.set_page_config(
    page_title="메인 페이지: 작업 실행", # 페이지 제목
    layout="centered" # 페이지 레이아웃을 중앙으로 설정
)

# @st.cache_resource 데코레이터 추가 (Playwright 브라우저 인스턴스를 캐싱하여 앱 재실행 시에도 유지)
@st.cache_resource
def get_playwright_browser():
    """
    Playwright 브라우저 인스턴스를 가져오거나 생성합니다.
    이 함수는 Streamlit 앱이 재실행되어도 브라우저 인스턴스를 재사용합니다.
    """
    try:
        # Playwright 시작 (브라우저 바이너리가 없으면 자동으로 다운로드 시도)
        # Streamlit Community Cloud와 같은 환경에서는 headless=True가 권장됩니다.
        p = sync_playwright().start()
        browser = p.chromium.launch(headless=True) # Chromium 브라우저를 헤드리스 모드로 실행
        return browser
    except Exception as e:
        # 브라우저 실행 실패 시 에러 로깅 및 예외 발생
        logger.error(f"Playwright 브라우저 실행 실패: {e}")
        st.error(f"Playwright 브라우저를 실행할 수 없습니다. Playwright 브라우저가 설치되었는지 확인해주세요. 에러: {e}")
        st.stop() # Streamlit 앱 실행 중지

def crawl_global_it_news(parameter) :
    """네이버 부동산 매물을 크롤링하는 함수"""

    # 입력 파라미터 출력 (디버깅용)
    print(f"유형 옵션: {parameter[0]}") # type_option(직장인, 신혼부부)
    print(f"지역 옵션1 (시): {parameter[1]}") # area_option1(시)
    print(f"지역 옵션2 (구): {parameter[2]}") # area_option2(구)
    print(f"지역 옵션3 (동): {parameter[3]}") # area_option3(동)
    print(f"면적 옵션: {parameter[4]}") # type_option(직장인, 신혼부부)
    print(f"예산: {parameter[5]}")
    print(f"거래 유형: {parameter[6]}")

    # Playwright 브라우저 인스턴스 가져오기
    browser = get_playwright_browser()
    page = browser.new_page() # 각 크롤링 실행마다 새로운 페이지 생성

    for_sale_list = [] # 매물 정보를 저장할 리스트 초기화

    try:
        print("📰 네이버 부동산 메인 페이지 접속 중...")
        page.goto("https://land.naver.com/") # 네이버 부동산 페이지로 이동
        page.wait_for_load_state('networkidle') # 네트워크 활동이 없을 때까지 대기

        # 1-2. 매물 탭 버튼 클릭
        # XPath 셀렉터를 사용하여 "매물" 탭 버튼 클릭
        page.click("xpath=//*[@id='lnb']/div/ul/li[2]/a[contains(@class,'NPI=a:article_beta')]")
        page.wait_for_timeout(1500) # 1.5초 대기
        print("1. 매물 탭 클릭 완료")

        # 2. 매물 조건 클릭 - 지역 필터 클릭
        page.click("(//span[contains(@class, 'area') and contains(@class, 'is-selected')])[1]")
        page.wait_for_timeout(1500)
        print("2. 지역 필터 클릭 완료")

        # 시 선택
        page.click(f'//*[@id="region_filter"]/div/div/div[2]/ul/li[contains(., "{parameter[1]}")]')
        page.wait_for_timeout(1500)
        print(f"3. 시 선택 완료: {parameter[1]}")

        # 구 선택
        page.click(f'//*[@id="region_filter"]/div/div/div[2]/ul/li[contains(., "{parameter[2]}")]')
        page.wait_for_timeout(1500)
        print(f"4. 구 선택 완료: {parameter[2]}")

        # 동 선택
        page.click(f'//*[@id="region_filter"]/div/div/div[2]/ul/li[contains(., "{parameter[3]}")]')
        page.wait_for_timeout(1500)
        print(f"5. 동 선택 완료: {parameter[3]}")

        # 매물 검색 버튼 클릭
        page.click('//*[@id="region_filter"]/div/div/div[4]/a[@class="btn_mapview"]')
        page.wait_for_timeout(2000) # 2초 대기
        print("6. 매물 검색 버튼 클릭 완료")

        # 추가 필터 - 거래 유형 필터 클릭
        if parameter[6] != "전체" :
            page.click('//*[@id="trade_type_filter"]/div/a')
            page.wait_for_timeout(1500)
            print("7. 거래 유형 필터 클릭 완료")

        # 거래 유형 필터 선택
        if parameter[6] != "전체" :
            page.click(f'//*[@id="trade_type_filter"]/div/div[1]/div/ul/li/label[contains(., "{parameter[6]}")]')
            page.wait_for_timeout(1500)
            print(f"8. 거래 유형 선택 완료: {parameter[6]}")

        # 거래가 필터 클릭
        page.click('//*[@id="price_filter"]/div/a')
        page.wait_for_timeout(1500)
        print("9. 거래가 필터 클릭 완료")

        # 거래가 입력 (최대 예산)
        page.fill('//*[@id="price_maximum"]', parameter[5])
        page.wait_for_timeout(1500)
        print(f"10. 예산 입력 완료: {parameter[5]}")

        # 면적 필터 클릭
        page.click('//*[@id="area_filter"]/div/a')
        page.wait_for_timeout(1500)
        print("11. 면적 필터 클릭 완료")

        # 면적 필터 선택
        page.click(f'//*[@id="area_filter"]/div/div[1]/div/div[2]/button[contains(.,"{parameter[4]}")]')
        page.wait_for_timeout(1500)
        print(f"12. 면적 선택 완료: {parameter[4]}")

        # 면적 필터 닫기 버튼 클릭
        page.click('//*[@id="area_filter"]/div/div[1]/div/button[@class="btn_close"]')
        page.wait_for_timeout(1500)
        print("13. 면적 필터 닫기 완료")

        # 지역 확대 버튼 클릭 (맵이 로드되고 매물이 나타날 때까지 충분히 대기)
        page.click('//*[@id="map"]/div[2]/div[3]/div/div[2]/div/button[2]')
        page.wait_for_timeout(10000) # 10초 대기 (중요: 매물 로딩 시간 고려)
        print("14. 지역 확대 버튼 클릭 완료")

        sub_url = page.url # 현재 페이지 URL 저장

        # 4. 매물 데이터 수집
        try :
            # 'marker_complex--apart' 클래스를 포함하는 모든 매물 요소 찾기
            items_locator = page.locator('//a[contains(@class, "marker_complex--apart")]')
            items = items_locator.all() # 모든 요소를 리스트로 가져오기
            print(f'총 {len(items)}개의 매물 마커 발견')

            if not items :  # 부합하는 조건의 매물이 없을 시
                print("❌ 조건에 부합하는 매물이 없습니다.")
                return for_sale_list # 빈 리스트 반환
            else : # 부합하는 조건의 매물 존재 시
                for i, item_element in enumerate(items) :
                    try :
                        # 매물 이름, 가격, 면적 요소 찾기
                        name_element = item_element.locator('.//div/div/div[@class="complex_title"]')
                        price_element = item_element.locator('.//div/div/div/div/span[@class="price_default"]')
                        volumn_element = item_element.locator('.//div/div/dl/dd[@class="complex_size-default"]')

                        # 텍스트 콘텐츠 추출
                        item_name = name_element.text_content().strip() # 매물 이름
                        item_price = price_element.text_content().strip() # 매물 가격

                        # 가격 단위 변환 (억, 만)
                        if '억' in item_price :
                            item_price = float(item_price.replace("억",""))
                            item_price = int(item_price * 10000)
                        elif '만' in item_price :
                            item_price = int(item_price.replace("만",""))

                        item_volumn = volumn_element.text_content().strip() # 매물 면적
                        item_volumn = item_volumn.replace("㎡", "") # '㎡' 제거

                        # 매물 상세 페이지 URL 생성
                        url_id = item_element.get_attribute('id').replace("COMPLEX","")
                        url = sub_url.replace("complexes?",f"complexes/{url_id}?")


                        print(f'({i+1}) 이름: {item_name}')
                        print(f'({i+1}) 가격: {item_price}')
                        print(f'({i+1}) 면적: {item_volumn}')
                        print(f'({i+1}) URL: {url}')

                        # 수집된 데이터를 리스트에 추가
                        for_sale_list.append({
                                'index': i + 1,
                                'type' :parameter[6],
                                'item_name': item_name,
                                'item_price': item_price,
                                'item_volumn' : item_volumn,
                                'url' : url,
                                'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S") # 현재 시간
                        })
                        print(f"📰 현재까지 {len(for_sale_list)}개 매물 수집 완료")
                    except Exception as inner_e :
                        print(f"❌ 개별 매물 정보 처리 실패: {inner_e}")
                        # 특정 매물 처리 실패 시에도 전체 로직은 계속 진행
        except Exception as outer_e:
            print(f"❌ 매물 요소들을 찾는 데 실패하였습니다: {outer_e}")
            return for_sale_list # 실패 시 현재까지 수집된 리스트 반환

    except Exception as e:
        print(f"❌ 크롤링 중 예상치 못한 에러 발생: {e}")
        return [] # 에러 발생 시 빈 리스트 반환
    finally:
        page.close() # 현재 페이지 닫기 (브라우저 인스턴스는 @st.cache_resource에 의해 관리됨)
        # browser.close() # @st.cache_resource를 사용하면 브라우저를 명시적으로 닫을 필요는 없습니다.

        if for_sale_list:
            print(f"\n📊 총 {len(for_sale_list)}개 매물 탐색 완료!")
            save_csv(for_sale_list)  # CSV 파일 생성
            return for_sale_list
        else:
            print("❌ 매물을 가져올 수 없습니다.")
            return [] # 매물이 없을 경우 빈 리스트 반환

def save_csv(for_sale_list):
    """CSV 파일로 데이터를 저장하는 함수"""
    if not for_sale_list:
        print("❌ 저장할 데이터가 없습니다.")
        return

    filename = f"it_news_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

    with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=['index', 'type', 'item_name', 'item_price', 'item_volumn', 'url', 'time'])
        writer.writeheader() # 헤더 작성
        writer.writerows(for_sale_list) # 데이터 행 작성

    print(f"✅ 저장완료: {filename} ({len(for_sale_list)}개)")

# --- st.session_state 초기화 (Streamlit 앱 상태 관리) ---
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
    st.session_state['budget'] = ""
if 'for_sale_data' not in st.session_state:
    st.session_state['for_sale_data'] = []

# 사이드바 숨기기 CSS (기본적으로 숨김)
invisible_sidebar_css = """
<style>
    .stSidebar {
        display: none !important;
    }
</style>
"""

# 사이드바 보이기 CSS
visible_sidebar_css = """
<style>
    .stSidebar {
        display: block !important;
    }
</style>
"""

st.markdown(invisible_sidebar_css, unsafe_allow_html=True) # 초기에는 사이드바 숨김


st.markdown("<h2>직장인/신혼부부 맞춤 부동산 매물 Search</h2>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

for_sale_list = [] # 크롤링 결과를 임시로 저장할 리스트

# 지역 선택 그룹 데이터
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

# Streamlit UI 요소 (Selectbox, Text Input, Button)
type_select = ["1. 유형을 선택하세요.", "직장인", "신혼부부"]
type_option_index = type_select.index(st.session_state['type_option']) if st.session_state['type_option'] in type_select else 0
type_option = st.selectbox("유형 선택", type_select, index=type_option_index, label_visibility="hidden", key="type_option_widget")
st.session_state['type_option'] = type_option

if st.session_state['type_option'] != "1. 유형을 선택하세요." :
    area1_option_index = area1_group.index(st.session_state['area1_option']) if st.session_state['area1_option'] in area1_group else 0
    area1_option = st.selectbox("2. 도시(도/시)를 선택하세요.", area1_group, index=area1_option_index, label_visibility="hidden", key="area1_option_widget")
    st.session_state['area1_option'] = area1_option

    if st.session_state['area1_option'] != "2. 도시(도/시)를 선택하세요." :
        area2_current_group = area2_group[area1_group.index(st.session_state['area1_option'])]
        area2_option_index = area2_current_group.index(st.session_state['area2_option']) if st.session_state['area2_option'] in area2_current_group else 0
        area2_option = st.selectbox("3. 구를 선택하세요.", area2_current_group, index=area2_option_index, label_visibility="hidden", key="area2_option_widget" )
        st.session_state['area2_option'] = area2_option

        if st.session_state['area2_option'] != "3. 구를 선택하세요." :
            area2_index_for_area3 = area1_group.index(st.session_state['area1_option'])
            area3_index_offset = area2_group[area2_index_for_area3].index(st.session_state['area2_option'])

            current_area3_group_index = area2_group[area2_index_for_area3].index(st.session_state['area2_option'])
            if area2_index_for_area3 == 2: # 경기도
                current_area3_group_index += 9 # 경기도 구 목록 이후부터 동 목록 시작
            elif area2_index_for_area3 == 3: # 인천시
                current_area3_group_index += 18 # 인천시 구 목록 이후부터 동 목록 시작
            elif area2_index_for_area3 == 4: # 광주시
                current_area3_group_index += 27 # 광주시 구 목록 이후부터 동 목록 시작

            area3_current_group = area3_group[current_area3_group_index]
            area3_option_index = area3_current_group.index(st.session_state['area3_option']) if st.session_state['area3_option'] in area3_current_group else 0
            area3_option = st.selectbox("4. 동을 선택하세요.", area3_current_group, index=area3_option_index, label_visibility="hidden", key="area3_option_widget" )
            st.session_state['area3_option'] = area3_option

            if st.session_state['area3_option'] != "4. 동을 선택하세요." :
                trade_type_select = ["5. 거래 유형을 선택하세요.", "전체", "매매", "전세", "월세"]
                trade_type_option_index = trade_type_select.index(st.session_state['trade_type_option']) if st.session_state['trade_type_option'] in trade_type_select else 0
                trade_type_option = st.selectbox("5. 거래 유형을 선택하세요.", trade_type_select, index=trade_type_option_index, label_visibility="hidden", key="trade_type_option_widget")
                st.session_state['trade_type_option'] = trade_type_option

                if st.session_state['trade_type_option'] != "5. 거래 유형을 선택하세요." :
                    volumn_select = ["6. 면적(평)을 선택하세요.", "10평", "20평", "30평", "40평", "50평", "60평"]
                    volumn_option_index = volumn_select.index(st.session_state['volumn_option']) if st.session_state['volumn_option'] in volumn_select else 0
                    volumn_option = st.selectbox("6. 면적(평)을 선택하세요.", volumn_select, index=volumn_option_index, label_visibility="hidden", key="volumn_option_widget" )
                    st.session_state['volumn_option'] = volumn_option

                    if st.session_state['volumn_option'] != "6. 면적(평)을 선택하세요." :
                        budget = st.text_input("7. 예산을 입력하세요(단위:만원)", value=st.session_state['budget'], key="budget_widget")
                        st.session_state['budget'] = budget

                        budget_int = 0
                        try :
                            if budget:
                                budget_int = int(budget)
                        except Exception as e :
                            st.markdown("<p> 숫자를 입력해주세요 </p>", unsafe_allow_html=True)

                        if budget and len(str(budget_int)) > 8 :
                            st.write(f"입력한 예산: {float(budget_int)/100000000}조")
                        elif budget and len(str(budget_int)) > 4 :
                            st.write(f"입력한 예산: {float(budget_int)/10000}억")
                        elif budget:
                            st.write(f"입력한 예산: {budget_int}만원")

                        if budget:
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

# 크롤링 결과가 있으면 세션 상태에 저장
if for_sale_list:
    st.session_state['for_sale_data'] = for_sale_list

# 세션 상태에 매물 데이터가 있으면 성공 메시지 표시 및 리포트 페이지로 이동 버튼 활성화
if st.session_state.get('for_sale_data') != [] :
    st.success("매물 찾기 성공!")
    st.markdown(visible_sidebar_css, unsafe_allow_html=True) # 사이드바 보이게 설정
    if st.button("리포트 페이지") :
        # Streamlit의 페이지 전환 기능 (pages/report.py 파일이 존재해야 함)
        st.switch_page("pages/report.py")