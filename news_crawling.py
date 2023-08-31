import requests
import pandas as pd
from bs4 import BeautifulSoup
from tqdm.notebook import tqdm

# def ex_tag2(sid, page):
#     url = f"https://news.naver.com/main/main.naver?mode=LSD&mid=shm&sid1={sid}"\
#     "#&date=%2000:00:00&page={page}"
#     html = requests.get(url, headers={"User-Agent": "Mozilla/5.0"\
#     "(Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "\
#     "Chrome/110.0.0.0 Safari/537.36"})
#     soup = BeautifulSoup(html.text, "lxml")
#     a_tag = soup.find_all("a")
    
#     tag_lst = []
#     for a in a_tag:
#         if "href" in a.attrs:  # href가 있는것만 고르는 것
#             if (f"sid={sid}" in a["href"]) and ("article" in a["href"]):
#                 tag_lst.append(a["href"])
#     return tag_lst
# # https://news.naver.com/main/list.naver?mode=LS2D&mid=shm&sid1=100&sid2=268
def ex_tag(sid, page):
    url = f"https://news.naver.com/main/list.naver?mode=LS2D&mid=shm&sid1=100&sid2=268"
    html = requests.get(url, headers={"User-Agent": "Mozilla/5.0"\
    "(Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "\
    "Chrome/110.0.0.0 Safari/537.36"})
    soup = BeautifulSoup(html.text, "lxml")
    a_tag = soup.find_all("a")
    tag_lst = []
    for a in a_tag:
        if "href" in a.attrs:  # href가 있는것만 고르는 것
            if (f"sid={sid}" in a["href"]) and ("article" in a["href"]):
                tag_lst.append(a["href"])
    return tag_lst
# print(ex_tag(268,2))

def re_tag(sid, pages):
    re_lst = []
    for i in range(pages):
        lst = ex_tag(sid, i+1)
        re_lst.extend(lst)
    return list(set(re_lst))


def make_hrefs(sids, pages):
    hrefs = {}
    for sid in sids:
        hrefs[sid] = re_tag(sid, pages)
    return hrefs


def art_crawl(hrefs, sid, index):
    art_dic = {}
    title_selector = "#title_area > span"
    date_selector = "#ct > div.media_end_head.go_trans > div.media_end_head_info.nv_notrans"\
    "> div.media_end_head_info_datestamp > div:nth-child(1) > span"
    main_selector = "#dic_area"  
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
    return art_dic


def solution(sids, pages):
    hrefs = make_hrefs(sids, pages)
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

ls = solution([101],2)
print(ls[:10])