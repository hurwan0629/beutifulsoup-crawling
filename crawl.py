from bs4 import BeautifulSoup
import requests

# Npay 증권의 주요 뉴스 url
domain = "https://finance.naver.com/"
main_news = "/news/mainnews.naver"

headers = {
    "User-Agent": "Monzilla/5.0"
}

# html 덩어리 가져오기
res = requests.get(domain+main_news, headers=headers)
res.encoding = "euc-kr"
html = res.text

# 가져온 html soup를 통해 파싱하여 해석하기
soup = BeautifulSoup(html, "lxml")

# 맨 밑의 페이지 네비게이션을 통해 몇페이지까지 있는지 확인 후 모두 크롤링 할 준비 하기
last_navi_url = soup.select("table.Nnavi td.pgRR a[href]")[0]["href"]
# 문자열에서 page= 기준으로 슬라이싱 하여 맨 앞의 숫자 뽑아오기
last_navi_page = int(last_navi_url.split("page=")[-1].split("&")[0])
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
    print(f"링크:[{link}]")
    
    # 크롤링링
    res = requests.get(link, headers)
    res.encoding = "euc-kr"

    # 추출
    page_soup = BeautifulSoup(res.text, "lxml")
    news_header_list = page_soup.select("#contentarea_left div.mainNewsList._replaceNewsLink ul.newsList li")
    
    # 하나씩 news_meta_list에 추가하기 {제목, 링크, 날짜}
    for news_header in news_header_list:
        news_title = news_header.select_one("dd.articleSubject a").text
        news_url = news_header.select_one("dd.articleSubject a[href]")["href"]
        news_date = news_header.select_one("dd.articleSummary span.wdate").text
        news_meta_list.append({
            "title": news_title,
            "news_url": news_url,
            "news_date": news_date
        })
for meta in news_meta_list:
    print(meta)