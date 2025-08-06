from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
import time
import csv
from datetime import datetime
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC



def crawl_real_estate_listings():
    """네이버 부동산 매물 크롤링"""
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--log-level=3")

    driver = webdriver.Chrome(options=options)

    try:
        print("📰 네이버 부동산 페이지 접속 중...")
        driver.get("https://new.land.naver.com/complexes?ms=37.3327729,127.1067075,15&a=APT:ABYG:JGC:PRE&e=RETAIL")

        WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "complex_title"))
    )


        # 지역 필터 선택
        area_1 = driver.find_element(By.XPATH, "(//span[contains(@class, 'area') and contains(@class, 'is-selected')])[1]")
        area_1.click()
        time.sleep(3)

        driver.find_element(By.XPATH, '//*[@id="region_filter"]/div/div/div[2]/ul/li[contains(., "서울시")]').click()
        time.sleep(2)
        driver.find_element(By.XPATH, '//*[@id="region_filter"]/div/div/div[2]/ul/li[contains(., "강남구")]').click()
        time.sleep(2)
        driver.find_element(By.XPATH, '//*[@id="region_filter"]/div/div/div[2]/ul/li[contains(., "역삼동")]').click()
        time.sleep(2)

        driver.find_element(By.XPATH, '//*[@id="region_filter"]/div/div/div[4]/a[@class="btn_mapview"]').click()
        time.sleep(3)

        # 거래유형 선택
        driver.find_element(By.XPATH, '//*[@id="trade_type_filter"]/div/a').click()
        time.sleep(3)
        driver.find_element(By.XPATH, '//*[@id="trade_type_filter"]/div/div[1]/div/ul/li[2]/label').click()
        time.sleep(3)

        # 가격 필터
        driver.find_element(By.XPATH, '//*[@id="price_filter"]/div/a').click()
        time.sleep(3)
        price_input = driver.find_element(By.XPATH, '//*[@id="price_maximum"]')
        ActionChains(driver).double_click(price_input).perform()
        time.sleep(3)
        price_input.send_keys(100000)
        time.sleep(3)

        # 면적 필터
        driver.find_element(By.XPATH, '//*[@id="area_filter"]/div/a').click()
        time.sleep(3)
        driver.find_element(By.XPATH, '//*[@id="area_filter"]/div/div[1]/div/div[2]/button[contains(., "30평")]').click()
        time.sleep(3)

        # 매물 정보 수집
        for_sale_list = []

        name_elements = driver.find_elements(By.XPATH, '//div[@class="complex_title"]')
        if not name_elements :
            print("⚠️ 매물 리스트를 찾지 못했습니다.")
        price_elements = driver.find_elements(By.XPATH, '//span[@class="price_default"]')
        if not price_elements :
            print("⚠️ 매물 리스트를 찾지 못했습니다.")
        households_elements = driver.find_elements(By.XPATH, '//div[@class="is-feature_default"]')
        if not name_elements :
            print("⚠️ 매물 리스트를 찾지 못했습니다.")
        volume_elements = driver.find_elements(By.XPATH, '//dd[@class="complex_size-default"]')
        if not volume_elements :
            print("⚠️ 매물 리스트를 찾지 못했습니다.")
        count = min(len(name_elements), len(price_elements), len(households_elements), len(volume_elements))
        merged = zip(name_elements[:count], price_elements[:count], households_elements[:count], volume_elements[:count])

        for i, (name_el, price_el, households_el, volume_el) in enumerate(merged):
            try:
                item = {
                    'index': i + 1,
                    'item_name': name_el.text.strip(),
                    'item_price': price_el.text.strip(),
                    'item_number_households': households_el.text.strip(),
                    'item_volumn': volume_el.text.strip(),
                    'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }

                print(f"({i+1}) {item['item_name']} / {item['item_price']} / {item['item_number_households']} / {item['item_volumn']}")
                for_sale_list.append(item)

            except Exception as e:
                print(f"❗ 오류 발생 ({i+1}번): {e}")
                continue

        return for_sale_list

    except Exception as e:
        print(f"❌ 크롤링 중 오류 발생: {e}")
        return []

    finally:
        driver.quit()


def save_csv(for_sale_list):
    if not for_sale_list:
        print("❌ 저장할 데이터가 없습니다.")
        return

    filename = f"real_estate_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"

    with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=['index', 'item_name', 'item_price', 'item_number_households', 'item_volumn', 'time'])
        writer.writeheader()
        writer.writerows(for_sale_list)

    print(f"✅ CSV 저장 완료: {filename} ({len(for_sale_list)}건)")


def main():
    for_sale_list = crawl_real_estate_listings()
    if for_sale_list:
        print(f"\n📊 총 {len(for_sale_list)}건 매물 수집 완료!")
        save_csv(for_sale_list)
    else:
        print("❌ 매물을 가져올 수 없습니다.")


if __name__ == "__main__":
    main()