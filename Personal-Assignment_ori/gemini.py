from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
import time # 최소한으로 사용
import csv
from datetime import datetime
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, StaleElementReferenceException

def crawl_real_estate_listings():
    """네이버 부동산 매물 크롤링"""
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--log-level=3")
    # headless 모드 추가 (옵션)
    # options.add_argument("--headless") # 필요에 따라 주석 해제

    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 40) # 대기 시간 늘림 (네트워크 상황 고려)

    try:
        print("📰 네이버 부동산 페이지 접속 중...")
        driver.get("https://new.land.naver.com/complexes?ms=37.3327729,127.1067075,15&a=APT:ABYG:JGC:PRE&e=RETAIL")
        
        # 페이지 로딩 및 주요 요소 확인
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".header_area"))) # 헤더 영역으로 초기 로딩 확인
        print("✅ 네이버 부동산 페이지 로드 완료.")

        # 최초 로딩 후 매물 리스트가 나타날 때까지 대기
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "complex_title")))


        # 지역 필터 선택
        print("📍 지역 필터 설정 중...")
        # 더 안정적인 XPath 사용 (필터 버튼 자체를 클릭)
        # area_1 = driver.find_element(By.XPATH, "(//span[contains(@class, 'area') and contains(@class, 'is-selected')])[1]") # 이 요소는 필터 내부의 선택된 영역을 나타낼 가능성이 높음
        # 대신, 필터 드롭다운 버튼 자체를 클릭하는 것이 더 안정적
        wait.until(EC.element_to_be_clickable((By.ID, "region_filter"))).click()
        time.sleep(1) # 필터 드롭다운 열리는 시간 대기

        wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="region_filter"]/div/div/div[2]/ul/li[contains(., "서울시")]'))).click()
        wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="region_filter"]/div/div/div[2]/ul/li[contains(., "강남구")]'))).click()
        wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="region_filter"]/div/div/div[2]/ul/li[contains(., "역삼동")]'))).click()
        
        # 지도 보기 버튼 클릭
        wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="region_filter"]/div/div/div[4]/a[@class="btn_mapview"]'))).click()
        print("✅ 지역 필터 설정 완료.")
        wait.until(EC.invisibility_of_element_located((By.ID, "region_filter"))) # 필터 창이 닫힐 때까지 대기
        time.sleep(2) # 지도 이동 및 데이터 로딩을 위한 추가 대기 (필요시)

        # 거래유형 선택
        print("💲 거래유형 필터 설정 중...")
        wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="trade_type_filter"]/div/a'))).click()
        wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="trade_type_filter"]/div/div[1]/div/ul/li[2]/label'))).click() # 2번째 라벨 (전세/월세일 수 있음)
        print("✅ 거래유형 필터 설정 완료.")
        wait.until(EC.invisibility_of_element_located((By.ID, "trade_type_filter"))) # 필터 창이 닫힐 때까지 대기
        time.sleep(2) # 데이터 로딩을 위한 추가 대기

        # 가격 필터
        print("💰 가격 필터 설정 중...")
        wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="price_filter"]/div/a'))).click()
        
        price_input = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="price_maximum"]')))
        ActionChains(driver).double_click(price_input).perform()
        price_input.send_keys("100000") # 문자열로 보내는 것이 더 안전
        print("✅ 가격 필터 설정 완료.")
        # 가격 필터 적용 버튼이 있다면 클릭, 없다면 다음 필터로 진행 (자동 적용되는 경우도 있음)
        # 예시: wait.until(EC.element_to_be_clickable((By.XPATH, '가격 필터의 적용/확인 버튼 XPath'))).click()
        time.sleep(2) # 데이터 로딩을 위한 추가 대기

        # 면적 필터
        print("📏 면적 필터 설정 중...")
        wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="area_filter"]/div/a'))).click()
        # "30평" 버튼 클릭
        wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="area_filter"]/div/div[1]/div/div[2]/button[contains(., "30평")]'))).click()
        print("✅ 면적 필터 설정 완료.")
        wait.until(EC.invisibility_of_element_located((By.ID, "area_filter"))) # 필터 창이 닫힐 때까지 대기
        time.sleep(3) # 모든 필터 적용 후 데이터가 완전히 로드될 때까지 충분히 대기

        # 매물 정보 수집
        for_sale_list = []
        print("🔍 매물 정보 수집 중...")

        # 필터 적용 후 새로운 매물 목록이 로드될 때까지 대기
        # 이전에 찾았던 요소들이 stale 해질 수 있으므로 다시 찾아야 함
        try:
            # 매물 목록 컨테이너가 로드될 때까지 기다리는 것이 더 안정적
            # ex) wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".list_view_area")))
            
            name_elements = wait.until(EC.presence_of_all_elements_located((By.XPATH, '//div[@class="complex_title"]')))
            price_elements = wait.until(EC.presence_of_all_elements_located((By.XPATH, '//span[@class="price_default"]')))
            households_elements = wait.until(EC.presence_of_all_elements_located((By.XPATH, '//div[contains(@class, "complex_feature") and contains(@class, "is-feature_default")]'))) # class 속성으로 찾기
            volume_elements = wait.until(EC.presence_of_all_elements_located((By.XPATH, '//dd[@class="complex_size-default"]')))
            
            print(f"✅ 총 {len(name_elements)}개의 매물 요소를 찾았습니다.")

            count = min(len(name_elements), len(price_elements), len(households_elements), len(volume_elements))
            
            if count == 0:
                print("⚠️ 필터링된 조건에 해당하는 매물이 없습니다.")
                return []

            for i in range(count):
                try:
                    item = {
                        'index': i + 1,
                        'item_name': name_elements[i].text.strip(),
                        'item_price': price_elements[i].text.strip(),
                        'item_number_households': households_elements[i].text.strip(),
                        'item_volumn': volume_elements[i].text.strip(),
                        'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }

                    print(f"({i+1}) {item['item_name']} / {item['item_price']} / {item['item_number_households']} / {item['item_volumn']}")
                    for_sale_list.append(item)

                except StaleElementReferenceException:
                    print(f"❗ 오류 발생 ({i+1}번): StaleElementReferenceException - 요소가 변경되었습니다. 재시도.")
                    # 이 경우, for 루프를 다시 시작하거나, 요소를 다시 찾아야 할 수 있습니다.
                    # 여기서는 간단히 건너뛰고 다음 요소로 진행합니다.
                    continue
                except Exception as e:
                    print(f"❗ 오류 발생 ({i+1}번): {e}")
                    continue
        except TimeoutException:
            print("❗ 매물 목록 요소들을 찾는 데 시간 초과 오류가 발생했습니다.")
            return []
        except NoSuchElementException:
            print("❗ 매물 목록 요소들을 찾을 수 없습니다.")
            return []

        return for_sale_list

    except TimeoutException as e:
        print(f"❌ 초기 로딩 또는 필수 요소 대기 중 시간 초과 오류 발생: {e}")
        return []
    except NoSuchElementException as e:
        print(f"❌ 필수 요소를 찾을 수 없습니다: {e}")
        return []
    except Exception as e:
        print(f"❌ 크롤링 중 예상치 못한 오류 발생: {e}")
        return []

    finally:
        print("👋 브라우저를 종료합니다.")
        driver.quit()


def save_csv(for_sale_list):
    if not for_sale_list:
        print("❌ 저장할 데이터가 없습니다.")
        return

    filename = f"real_estate_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv" # 초 단위까지 추가하여 파일명 충돌 방지

    # fieldnames가 CSV 파일의 헤더와 순서를 정의합니다.
    fieldnames = ['index', 'item_name', 'item_price', 'item_number_households', 'item_volumn', 'time']

    try:
        with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(for_sale_list)

        print(f"✅ CSV 저장 완료: {filename} ({len(for_sale_list)}건)")
    except Exception as e:
        print(f"❌ CSV 저장 중 오류 발생: {e}")


def main():
    for_sale_list = crawl_real_estate_listings()
    if for_sale_list:
        print(f"\n📊 총 {len(for_sale_list)}건 매물 수집 완료!")
        save_csv(for_sale_list)
    else:
        print("❌ 매물을 가져올 수 없습니다.")


if __name__ == "__main__":
    main()