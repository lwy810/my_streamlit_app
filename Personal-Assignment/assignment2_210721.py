# ex08.py
# https://www.hankyung.com/globalmarket/news-globalmarket
# 한경글로벌 마켓의 뉴스 기사 타이틀 10개 / image url을 출력하시오.

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import csv
from datetime import datetime
from selenium.webdriver.common.action_chains import ActionChains

def crawl_global_it_news():
    """네이버 뉴스 크롤링"""
    
    # Chrome 설정
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(options=options)
    
    try:
        print("🚀 네이버 뉴스 크롤링 시작...")
        
        # 1. 네이버 뉴스 메인 페이지 접속
        print("📰 네이버 메인 페이지 접속 중...")
        driver.get("https://new.land.naver.com/complexes?ms=37.3327729,127.1067075,15&a=APT:ABYG:JGC:PRE&e=RETAIL")
        time.sleep(3)

        # 2. 뉴스 링크 수집
        news_list = []                           
        # HTML 문서에서 모든 <a> 태그를 선택함
        # news_1 = driver.find_elements(By.XPATH, "//a[contains(@class, '_cds_link') and contains(., '치킨')]")
        # news_2 = driver.find_elements(By.XPATH, "//a[contains(@class, '_cds_link') and contains(., 'AI')]")
        # news_3 = driver.find_elements(By.XPATH, "//a[contains(@class, '_cds_link') and contains(., '경제')]")

        # news_groups = [
        #     (news_1, "치킨"),
        #     (news_2, "AI"),
        #     (news_3, "경제")
        # ]


        news = driver.find_elements(By.XPATH, "//a[contains(@id,'COMPLEX')]/div/div/div/div/span[@class='price_default']")
        for i, news in enumerate(news):
                try:
                    title = news.text.strip()
                    # url = news.get_attribute('href')
                    print(f'({i+1}) {title}')
                    # print(f'({i+1}) {url}')
                    # print(f'({i+1}) {len(title)}')

                  
                    news_list.append({
                            'index': i + 1,
                            'title': title,
                            # 'link': url,
                            # 'keyword' : keyword,
                            'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })
                    print(f"📰 [{len(news_list)}] {title[:50]}...")
                except:
                    continue
    
        return news_list




        # for news_group, keyword in news_groups :
        #     for i, news in enumerate(news_group):
        #         try:
        #             title = news.text.strip()
        #             url = news.get_attribute('href')
        #             print(f'({i+1}) {title}')
        #             # print(f'({i+1}) {url}')
        #             # print(f'({i+1}) {len(title)}')

        #             if title and url and len(title) > 10:  # 유효한 제목만
        #                 news_list.append({
        #                         'index': i + 1,
        #                         'title': title,
        #                         # 'link': url,
        #                         # 'keyword' : keyword,
        #                         'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        #             })
        #             print(f"📰 [{len(news_list)}] {title[:50]}...")
        #         except:
        #             continue
    
        # return news_list
        
    except Exception as e:
        print(f"❌ 에러: {e}")
        return []
    finally:
        driver.quit()

def save_csv(news_list):
    """CSV 파일 저장"""
    if not news_list:
        print("❌ 저장할 데이터가 없습니다.")
        return
    
    filename = f"it_news_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
    
    with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
        # writer = csv.DictWriter(f, fieldnames=['index', 'keyword', 'title', 'link', 'time'])
        writer = csv.DictWriter(f, fieldnames=['index', 'title', 'time'])
        writer.writeheader()
        writer.writerows(news_list)
    
    print(f"✅ 저장완료: {filename} ({len(news_list)}개)")

def main():
    # 크롤링 실행
    news = crawl_global_it_news()
    
    # 결과 출력
    if news:
        print(f"\n📊 총 {len(news)}개 뉴스 수집완료!")
        save_csv(news)
    else:
        print("❌ 뉴스를 가져올 수 없습니다.")

if __name__ == "__main__":
    main()