from urllib.parse import urljoin, urlparse, parse_qs
from bs4 import BeautifulSoup
import requests
from datetime import datetime, timedelta

# Npay 증권의 주요 뉴스 url
domain = "https://finance.naver.com/"
main_news = "/news/mainnews.naver"

# 가져올 날짜 범위 정하기
today = datetime.now().date()
# 범위를 오늘로 설정
start_date = datetime.combine(today, datetime.min.time())
end_date = datetime.combine(today, datetime.max.time())

headers = {
    "User-Agent": "Mozilla/5.0"
}

# html 덩어리 가져오기
res = requests.get(domain+main_news, headers=headers)
res.encoding = "euc-kr"
html = res.text

# 가져온 html soup를 통해 파싱하여 해석하기
soup = BeautifulSoup(html, "lxml")

# 맨 밑의 페이지 네비게이션을 통해 몇페이지까지 있는지 확인 후 모두 크롤링 할 준비 하기
last_navi_url = soup.select_one("table.Nnavi td.pgRR a")


# 문자열에서 page= 기준으로 슬라이싱 하여 맨 앞의 숫자 뽑아오기
last_navi_page = 1

if last_navi_url:
    params = parse_qs(urlparse(last_navi_url["href"]).query)
    last_navi_page= int(params.get("page", [1])[0])

print(f"추출 url:[{last_navi_url}]")
print(f"마지막 page:[{last_navi_page}]")


# 오늘자 주요 뉴스 링크 크롤링
# {제목, 링크, 날짜 리스트 준비}
news_meta_list = []
for i in range(last_navi_page):
    # 크롤링 준비비
    page = i+1
    print(f"페이지 링크 추출중... page:[{page}]")
    link = domain + main_news + "?&page=" + str(page)
    # print(f"링크:[{link}]")
    
    # 크롤링링
    res = requests.get(link, headers=headers)
    res.encoding = "euc-kr"

    # 추출
    page_soup = BeautifulSoup(res.text, "lxml")
    news_header_list = page_soup.select("#contentarea_left div.mainNewsList._replaceNewsLink ul.newsList li")
    
    # 하나씩 news_meta_list에 추가하기 {제목, 링크, 날짜}
    for news_header in news_header_list:
        # 뉴스 시간을 통한 필터링
        news_date = news_header.select_one("dd.articleSummary span.wdate").text
        # 뉴스 시각 datetime타입으로 변환
        news_datetime = datetime.strptime(news_date, "%Y-%m-%d %H:%M:%S")
        # 어제 날짜인지 확인하기
        if not (start_date <= news_datetime and news_datetime <= end_date):
            continue

        news_title = news_header.select_one("dd.articleSubject a").text
        news_url = news_header.select_one("dd.articleSubject a[href]")["href"]
        news_meta_list.append({
            "title": news_title,
            "news_url": news_url,
            "news_date": news_date
        })
print("뉴스 목록 크롤링 완료")

news_content_list = []
news_count = len(news_meta_list)
count = 0
print("뉴스 내용 크롤링 시작")
for meta in news_meta_list:
    count += 1
    print(f"크롤링중... ({count}/{news_count})")
    # url합치기
    href = meta.get("news_url")
    # 파라미터 추출
    params = {}
    for p in href.split("?")[1].split("&"):
        key, value = p.split("=")
        params[key] = value
    
    article_id = params["article_id"]
    office_id = params["office_id"]

    locate = f"https://n.news.naver.com/mnews/article/{office_id}/{article_id}"

    res = requests.get(locate, headers=headers)
    res.encoding = "utf-8"

    news_content_title = BeautifulSoup(res.text).select_one("#title_area").text
    # print(f"제목: {news_content_title}")
    news_content_body = BeautifulSoup(res.text).select_one("#dic_area").text
    # print(f"내용:\n{news_content_body}")
    
    news_content_list.append({
        "title": news_content_title,
        "body": news_content_body
    })

# 일단 메모장으로 출력
with open(f"뉴스크롤링 - {today}.txt", "w", encoding="utf-8") as f:
    for news in news_content_list:
        f.write(f"# 제목: {news.get("title")}")
        f.write(f"\n[내용]\n{news.get("body")}\n\n")