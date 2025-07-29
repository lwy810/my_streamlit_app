from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
import time
import csv
from datetime import datetime
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

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
    
    # Chrome 설정
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--log-level=3")  # 로그 레벨 최소화


    # ChromeService 객체를 생성하여 ChromeDriver를 자동으로 관리
    service = ChromeService(executable_path=ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)

    try:
        # print("🚀 네이버 뉴스 크롤링 시작...")
        
        # 1. 네이버 뉴스 메인 페이지 접속
        print("📰 네이버 메인 페이지 접속 중...")
        driver.maximize_window()
        driver.get("https://land.naver.com/")
        wait = WebDriverWait(driver, 60) # 대기 시간 늘림 (네트워크 상황 고려)
        
        # 1-2. 매물 탭 버튼 클릭
        tab_button = driver.find_element(By.XPATH, "//*[@id='lnb']/div/ul/li[2]/a[@class='NPI=a:article_beta']")
        tab_button.click()
        time.sleep(1.5)

        # 2. 매물 조건 클릭
        # 지역 필터 클릭
        area_1 = driver.find_element(By.XPATH, "(//span[contains(@class, 'area') and contains(@class, 'is-selected')])[1]")
        area_1.click()
        time.sleep(1.5)
        print("1")

        # 시 선택
        area_1_parameter = driver.find_element(By.XPATH, f'//*[@id="region_filter"]/div/div/div[2]/ul/li[contains(., "{parameter[1]}")]')
        area_1_parameter.click()
        time.sleep(1.5)
        print("2")

        # 구 선택
        area_2_parameter = driver.find_element(By.XPATH, f'//*[@id="region_filter"]/div/div/div[2]/ul/li[contains(., "{parameter[2]}")]')
        area_2_parameter.click()
        time.sleep(1.5)
        print("3")

        # 동 선택
        area_3_parameter = driver.find_element(By.XPATH, f'//*[@id="region_filter"]/div/div/div[2]/ul/li[contains(., "{parameter[3]}")]')
        area_3_parameter.click()
        time.sleep(1.5)
        print("4")
        
        # 매물 검색
        search_button = driver.find_element(By.XPATH, '//*[@id="region_filter"]/div/div/div[4]/a[@class="btn_mapview"]')
        search_button.click()
        time.sleep(2)
        print("5")

        # 추가 필터
        # 거래 유형 필터 클릭
        if parameter[6] != "전체" :
            item_type_search = driver.find_element(By.XPATH, '//*[@id="trade_type_filter"]/div/a')
            item_type_search.click()
            time.sleep(1.5)
            print("6")

        # 거래 유형 필터 선택
        if parameter[6] != "전체" :
            item_type_select = driver.find_element(By.XPATH, f'//*[@id="trade_type_filter"]/div/div[1]/div/ul/li/label[contains(., "{parameter[6]}")]')
            item_type_select.click()
            time.sleep(1.5)
            print("7")

        # 거래가 필터 클릭
        price_search = driver.find_element(By.XPATH, '//*[@id="price_filter"]/div/a')
        price_search.click()
        time.sleep(1.5)
        print("8")

        # 거래가 입력
        price_input = driver.find_element(By.XPATH, '//*[@id="price_maximum"]')
        actions = ActionChains(driver) # 더블 클릭 액션
        actions.double_click(price_input).perform()
        time.sleep(1.5)
        print("9")

        price_input.send_keys(parameter[5]) # 거래가 입력
        time.sleep(1.5)
        print("10")

        # 면적 필터 클릭
        volumn_search = driver.find_element(By.XPATH, '//*[@id="area_filter"]/div/a')
        volumn_search.click()
        time.sleep(1.5)
        print("11")

        # 면적 필터 선택
        volumn_input = driver.find_element(By.XPATH, f'//*[@id="area_filter"]/div/div[1]/div/div[2]/button[contains(.,"{parameter[4]}")]')
        volumn_input.click()
        time.sleep(1.5)
        print("12")
     
        volumn_search_quit = driver.find_element(By.XPATH, '//*[@id="area_filter"]/div/div[1]/div/button[@class="btn_close"]')
        volumn_search_quit.click()
        time.sleep(1.5)
        print("13")

        # 지역 확대 버튼 클릭
        map_downsize_button = driver.find_element(By.XPATH, '//*[@id="map"]/div[2]/div[3]/div/div[2]/div/button[2]')
        map_downsize_button.click()
        time.sleep(10)
        print("14")

        sub_url = driver.current_url

        # 4. 매물 데이터 수집
        for_sale_list = []
        # try :
        #     name = wait.until(EC.presence_of_all_elements_located((By.XPATH, '//a[contains(@id, "COMPLEX")]/div/div/div[@class="complex_title"]')))
        #     print(f'15 {len(name)}')
        #     price = wait.until(EC.presence_of_all_elements_located((By.XPATH, '//a[contains(@id, "COMPLEX")]/div/div/div/div/span[@class="price_default"]')))
        #     print(f'16 {len(price)}')
        #     number_households =  wait.until(EC.presence_of_all_elements_located((By.XPATH, '//a[contains(@id, "COMPLEX")]/div/div[@class="complex_feature is-feature_default"]')))
        #     print(f'17 {len(number_households)}')
        #     volumn = wait.until(EC.presence_of_all_elements_located((By.XPATH, '//a[contains(@id, "COMPLEX")]/div/div/dl/dd[@class="complex_size-default"]')))
        #     print(f'18 {len(volumn)}')
        # except TimeoutException :
        #     print("매물이 검색되지 않았습니다.")
        #     return for_sale_list

        try :
            items = wait.until(EC.presence_of_all_elements_located((By.XPATH, '//a[contains(@class, "marker_complex--apart")]')))
            print(f'20 {len(items)}')

            if not items :  # 부합하는 조건의 매물이 없을 시
                print("❌ 조건에 부합하는 매물이 없습니다.")
                return for_sale_list
            else : # 부합하는 조건의 매물 존재 시
                for i, items in enumerate(items) :
                    try :
                        # 세부 정보를 보이게 하기 위해 호버를 시뮬레이션합니다 (필요한 경우).
                        # 더 현실적인 호버 시뮬레이션을 위해 ActionChains를 사용합니다.

                        name = items.find_element(By.XPATH, './/div/div/div[@class="complex_title"]')  # 매물 이름 찾기
                        price = items.find_element(By.XPATH, './/div/div/div/div/span[@class="price_default"]')  # 매물 가격 찾기
                        volumn = items.find_element(By.XPATH, './/div/div/dl/dd[@class="complex_size-default"]')  # 매물 면적 찾기
                        url_id = str(items.get_attribute('id').replace("COMPLEX",""))
                        print(url_id)
                        url = sub_url.replace("complexes?",f"complexes/{url_id}?")
                        print(url)

                        driver.execute_script("arguments[0].style.display = 'block';", name)
                        time.sleep(1.5)
                        item_name = name.get_attribute('innerText').strip() # 매물 이름 추출
                        # print("21")
                        item_price = price.get_attribute('innerText').strip()  # 매물 가격 추출
                        if item_price.find('억') >= 0 :
                            print(item_price.find('억'))
                            print(type(item_price))
                            item_price = float(item_price.replace("억",""))
                            print(item_price)
                            item_price = int(item_price * 10000)
                        elif item_price.find('만') >= 0 :
                            item_price.replace("만","")

                        # print("22")
                        # print("23")
                        item_volumn = volumn.get_attribute('innerText').strip()  # 매물 면적 추출
                        item_volumn = item_volumn.replace("㎡", "")
                        # print("24")

                        print(f'({i+1}) {item_name}')
                        print(f'({i+1}) {item_price}')
                        print(f'({i+1}) {item_volumn}')

                        # if len(item_name) and len(item_price) and len(item_number_households) and len(item_volumn) > 0 :
                        # 매물 리스트 생성
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
                    except Exception :
                        print("❌ 매물 리스트 생성에 실패하였습니다.")
        except:
            return for_sale_list
    
    except Exception as e:
        print(f"❌ 에러: {e}")
        return []
    finally:
        driver.quit()

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


# def main():
#     # 크롤링 실행
#     for_sale_list = crawl_global_it_news()
    
#     # 결과 출력
#     if for_sale_list:
#         print(f"\n📊 총 {len(for_sale_list)}개 뉴스 수집완료!")
#         save_csv(for_sale_list)
#     else:
#         print("❌ 뉴스를 가져올 수 없습니다.")

# # if __name__ == "__main__":
# #     main()