import requests
import pandas as pd
from bs4 import BeautifulSoup
from tqdm.notebook import tqdm
from datetime import datetime, timedelta

# 시작일과 종료일을 문자열 형태로 입력받습니다.
def date_producer(start_date_str,end_date_str):
    # 문자열 형태의 날짜를 datetime 객체로 변환합니다.
    start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
    end_date = datetime.strptime(end_date_str, "%Y-%m-%d")

    # 시작일부터 종료일까지의 모든 날짜들을 저장할 리스트를 생성합니다.
    date_list = []

    # 시작일부터 종료일까지 하루씩 증가시키며 날짜 리스트에 추가합니다.
    delta = timedelta(days=1)
    while start_date <= end_date:
        date_list.append(start_date.strftime("%Y%m%d"))
        start_date += delta
    return date_list

# https://news.naver.com/main/list.naver?mode=LS2D&sid2=268&mid=shm&sid1=100&date=20230830&page=7
SID1 = 100
def ex_tag(sid1, sid2, page, date):
    url = f"https://news.naver.com/main/list.naver?mode=LS2D&sid2={sid2}&mid=shm&sid1={sid1}&date={date}&page={page}"
    html = requests.get(url, headers={"User-Agent": "Mozilla/5.0"\
    "(Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "\
    "Chrome/110.0.0.0 Safari/537.36"})
    soup = BeautifulSoup(html.text, "lxml")
    a_tag = soup.find_all("a")
    tag_lst = []
    for a in a_tag:
        if "href" in a.attrs:  # href가 있는것만 고르는 것
            if (f"sid=100" in a["href"]) and ("article" in a["href"]):
                tag_lst.append(a["href"])
    return tag_lst

def re_tag(sid1, sid2, pages, date_list):
    re_lst = []
    for date in date_list:
        for i in range(pages):
            lst = ex_tag(sid1, sid2, i+1, date)
            re_lst.extend(lst)
    return list(set(re_lst))


def make_hrefs(sids, pages, date_list):
    hrefs = {}
    for sid2 in sids:
        hrefs[sid2] = re_tag(SID1, sid2, pages, date_list)
    return hrefs

# print(make_hrefs([268],10))

def art_crawl(hrefs, sid, index):
    art_dic = {}
    title_selector = "#title_area > span"
    date_selector = "#ct > div.media_end_head.go_trans > div.media_end_head_info.nv_notrans"\
    "> div.media_end_head_info_datestamp > div:nth-child(1) > span"
    main_selector = "#dic_area"  
    author_selector = ".media_end_head_journalist_name"
    url = hrefs[sid][index]
    html = requests.get(url, headers = {"User-Agent": "Mozilla/5.0 "\
    "(Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"\
    "Chrome/110.0.0.0 Safari/537.36"})
    soup = BeautifulSoup(html.text, "lxml")
    title = soup.select(title_selector)
    title_lst = [t.text for t in title]
    title_str = "".join(title_lst)

    date = soup.select(date_selector)
    date_lst = [d.text for d in date]
    date_str = "".join(date_lst)

    author = soup.select(author_selector)
    author_lst = [a.text for a in author]
    author_str = "".join(author_lst)
    
    main = soup.select(main_selector)
    main_lst = []
    for m in main:
        m_text = m.text
        m_text = m_text.strip()
        main_lst.append(m_text)
    main_str = "".join(main_lst)
    art_dic["title"] = title_str
    art_dic["date"] = date_str
    art_dic["main"] = main_str
    art_dic["author"] = author_str
    return art_dic


def solution(sids, pages, date_list):
    hrefs = make_hrefs(sids, pages, date_list)
    artdic_lst = []
    for section in sids:
        for i in range(len(hrefs[section])):
            art_dic = art_crawl(hrefs, section, i)
            art_dic["section"] = section
            art_dic["url"] = hrefs[section][i]
            artdic_lst.append(art_dic)
    return artdic_lst


def to_csv(artdic_lst):
    art_df = pd.DataFrame(artdic_lst)
    art_df.to_csv("article_df.csv")

category_ls= []
#1 = 대통령실 2 = 북한 3 = 국방/외교
politic_category = {1:264, 2:268, 3:267}
while True:
    # Ask for user input
    user_input = input("원하는 정치기사의 종류를 입력하시오 (중복 선택 가능). 입력을 마쳤으면 'ENTER'키를 누르세요 \n1.대통령실\n2.북한\n3.국방/외교\n")

    # If the user input is empty, break the loop
    if user_input == "":
        break
    try:
        # Try to convert the input to an integer
        user_input = int(user_input)
        # If the integer is not already in the list, append it
        if user_input not in category_ls:
            category_ls.append(politic_category[user_input])
    except ValueError:
        print("유효한 정수가 아닙니다. 다시 시도해주세요.")
    # If the user input is not already in the list, append it
print(category_ls)
start_date_str = input("데이터 크롤링을 시작할 뉴스의 날짜를 YYYY-MM-DD 식으로 입려하시오. 예:2023-07-31\n")
end_date_str = input("데이터 크롤링을 끝낼 뉴스의 날짜를 YYYY-MM-DD 식으로 입려하시오. 예:2023-07-31\n")
date_list = date_producer(start_date_str, end_date_str)

ls = solution(category_ls, 1, date_list)
