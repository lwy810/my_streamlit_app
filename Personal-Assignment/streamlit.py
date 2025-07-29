import streamlit as st
import logging
# from selenium import webdriver # 제거
# from selenium.webdriver.common.by import By # 제거
# from selenium.webdriver.chrome.options import Options # 제거
# from selenium.webdriver.chrome.service import Service as ChromeService # 제거
# from webdriver_manager.chrome import ChromeDriverManager # 제거
from playwright.sync_api import sync_playwright # 추가

import time
import csv
from datetime import datetime
# from selenium.webdriver.common.action_chains import ActionChains # 제거
# from selenium.webdriver.support.ui import WebDriverWait # 제거
# from selenium.webdriver.support import expected_conditions as EC # 제거
# from selenium.common.exceptions import TimeoutException # 제거


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

st.set_page_config(
    page_title="메인 페이지: 작업 실행",
    layout="centered"
)

# @st.cache_resource 데코레이터 추가 (Playwright 브라우저 캐싱)
@st.cache_resource
def get_playwright_browser():
    # Playwright는 시작 시 필요한 브라우저 바이너리를 자동으로 다운로드합니다.
    # Streamlit Community Cloud 환경에서 headless=True로 설정된 Chromium은 잘 작동합니다.
    p = sync_playwright().start()
    browser = p.chromium.launch(headless=True)
    return browser

def crawl_global_it_news(parameter) :
    """네이버 뉴스 크롤링"""

    parameter = parameter
    print(parameter[0]) # type_option(직장인, 신혼부부)
    print(parameter[1]) # area_option1(시)
    print(parameter[2]) # area_option2(구)
    print(parameter[3]) # area_option3(동)
    print(parameter[4]) # type_option(직장인, 신혼부부)
    print(parameter[5])
    print(parameter[6])

    # Playwright 브라우저 인스턴스 가져오기
    browser = get_playwright_browser()
    page = browser.new_page() # 각 실행마다 새로운 페이지 생성

    try:
        print("📰 네이버 메인 페이지 접속 중...")
        page.goto("https://land.naver.com/")
        page.wait_for_load_state('networkidle') # 네트워크 활동이 없을 때까지 대기

        # 1-2. 매물 탭 버튼 클릭
        # Playwright는 셀렉터가 더 강력합니다. XPath도 지원하지만 CSS 셀렉터가 권장됩니다.
        # wait_for_selector를 사용하여 요소가 나타날 때까지 기다립니다.
        page.click("xpath=//*[@id='lnb']/div/ul/li[2]/a[contains(@class,'NPI=a:article_beta')]")
        page.wait_for_timeout(1500) # time.sleep 대신 Playwright의 wait_for_timeout 사용

        # 2. 매물 조건 클릭
        # 지역 필터 클릭
        page.click("(//span[contains(@class, 'area') and contains(@class, 'is-selected')])[1]")
        page.wait_for_timeout(1500)
        print("1")

        # 시 선택
        page.click(f'//*[@id="region_filter"]/div/div/div[2]/ul/li[contains(., "{parameter[1]}")]')
        page.wait_for_timeout(1500)
        print("2")

        # 구 선택
        page.click(f'//*[@id="region_filter"]/div/div/div[2]/ul/li[contains(., "{parameter[2]}")]')
        page.wait_for_timeout(1500)
        print("3")

        # 동 선택
        page.click(f'//*[@id="region_filter"]/div/div/div[2]/ul/li[contains(., "{parameter[3]}")]')
        page.wait_for_timeout(1500)
        print("4")

        # 매물 검색
        page.click('//*[@id="region_filter"]/div/div/div[4]/a[@class="btn_mapview"]')
        page.wait_for_timeout(2000)
        print("5")

        # 추가 필터
        # 거래 유형 필터 클릭
        if parameter[6] != "전체" :
            page.click('//*[@id="trade_type_filter"]/div/a')
            page.wait_for_timeout(1500)
            print("6")

        # 거래 유형 필터 선택
        if parameter[6] != "전체" :
            page.click(f'//*[@id="trade_type_filter"]/div/div[1]/div/ul/li/label[contains(., "{parameter[6]}")]')
            page.wait_for_timeout(1500)
            print("7")

        # 거래가 필터 클릭
        page.click('//*[@id="price_filter"]/div/a')
        page.wait_for_timeout(1500)
        print("8")

        # 거래가 입력
        # Playwright에서는 fill() 메서드를 사용하여 바로 값을 채울 수 있습니다.
        page.fill('//*[@id="price_maximum"]', parameter[5])
        page.wait_for_timeout(1500)
        print("10")

        # 면적 필터 클릭
        page.click('//*[@id="area_filter"]/div/a')
        page.wait_for_timeout(1500)
        print("11")

        # 면적 필터 선택
        page.click(f'//*[@id="area_filter"]/div/div[1]/div/div[2]/button[contains(.,"{parameter[4]}")]')
        page.wait_for_timeout(1500)
        print("12")

        page.click('//*[@id="area_filter"]/div/div[1]/div/button[@class="btn_close"]')
        page.wait_for_timeout(1500)
        print("13")

        # 지역 확대 버튼 클릭
        page.click('//*[@id="map"]/div[2]/div[3]/div/div[2]/div/button[2]')
        page.wait_for_timeout(10000) # 대기 시간 유지
        print("14")

        sub_url = page.url

        # 4. 매물 데이터 수집
        for_sale_list = []
        try :
            # Playwright의 locator를 사용하여 요소 찾기
            items_locator = page.locator('//a[contains(@class, "marker_complex--apart")]')
            items = items_locator.all() # 모든 요소 가져오기
            print(f'20 {len(items)}')

            if not items :  # 부합하는 조건의 매물이 없을 시
                print("❌ 조건에 부합하는 매물이 없습니다.")
                return for_sale_list
            else : # 부합하는 조건의 매물 존재 시
                for i, item_element in enumerate(items) :
                    try :
                        # Playwright의 locator에서 직접 텍스트나 속성을 추출합니다.
                        # Selenium의 execute_script를 사용하지 않아도 됩니다.
                        name_element = item_element.locator('.//div/div/div[@class="complex_title"]')
                        price_element = item_element.locator('.//div/div/div/div/span[@class="price_default"]')
                        volumn_element = item_element.locator('.//div/div/dl/dd[@class="complex_size-default"]')

                        # 요소가 화면에 보이도록 스크롤하고, 텍스트를 가져오기 전에 대기할 수 있습니다.
                        # name_element.scroll_into_view_if_needed() 
                        # page.wait_for_timeout(500) # 필요시 짧은 대기

                        item_name = name_element.text_content().strip() # 매물 이름 추출
                        item_price = price_element.text_content().strip()  # 매물 가격 추출
                        if '억' in item_price :
                            item_price = float(item_price.replace("억",""))
                            item_price = int(item_price * 10000)
                        elif '만' in item_price :
                            item_price = int(item_price.replace("만",""))

                        item_volumn = volumn_element.text_content().strip()  # 매물 면적 추출
                        item_volumn = item_volumn.replace("㎡", "")

                        url_id = item_element.get_attribute('id').replace("COMPLEX","")
                        url = sub_url.replace("complexes?",f"complexes/{url_id}?")


                        print(f'({i+1}) {item_name}')
                        print(f'({i+1}) {item_price}')
                        print(f'({i+1}) {item_volumn}')
                        print(f'({i+1}) {url}')


                        for_sale_list.append({
                                'index': i + 1,
                                'type' :parameter[6],
                                'item_name': item_name,
                                'item_price': item_price,
                                'item_volumn' : item_volumn,
                                'url' : url,
                                'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        })
                        print("25")
                        print(f"📰 [{len(for_sale_list)}개]")
                    except Exception as inner_e :
                        print(f"❌ 매물 리스트 생성에 실패하였습니다: {inner_e}")
                        # 특정 매물 처리 실패 시에도 전체 로직은 계속 진행
        except Exception as outer_e:
            print(f"❌ 매물 요소들을 찾는 데 실패하였습니다: {outer_e}")
            return for_sale_list

    except Exception as e:
        print(f"❌ 에러: {e}")
        return []
    finally:
        page.close() # 현재 페이지 닫기 (브라우저 인스턴스는 @st.cache_resource에 의해 관리)
        # browser.close() # @st.cache_resource를 사용하면 명시적으로 닫을 필요는 없습니다.

        if for_sale_list:
            print(f"\n📊 총 {len(for_sale_list)}개 매물 탐색 완료!")
            save_csv(for_sale_list)  # CSV 생성 시작
            return for_sale_list

        else:
            print("❌ 매물를 가져올 수 없습니다.")

def save_csv(for_sale_list):
    """CSV 파일 저장"""
    if not for_sale_list:
        print("❌ 저장할 데이터가 없습니다.")
        return

    filename = f"it_news_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

    with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=['index', 'type', 'item_name', 'item_price', 'item_volumn', 'url', 'time'])
        writer.writeheader()
        writer.writerows(for_sale_list)


    print(f"✅ 저장완료: {filename} ({len(for_sale_list)}개)")

# --- st.session_state 초기화 (이전과 동일) ---
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


st.markdown("<h2>직장인/신혼부부 맞춤 부동산 매물 Search</h2>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

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

if for_sale_list:
    st.session_state['for_sale_data'] = for_sale_list

if st.session_state.get('for_sale_data') != [] :
    st.success("매물 찾기 성공!")
    st.markdown(visible_sidebar_css, unsafe_allow_html=True)
    if st.button("리포트 페이지") :
        st.switch_page("pages/report.py")