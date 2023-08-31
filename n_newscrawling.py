import requests
import pandas as pd
from bs4 import BeautifulSoup

def make_urllist(page_num, code, date): 
  urllist= []
  for i in range(1, page_num + 1):
    url = 'https://news.naver.com/main/list.nhn?mode=LSD&mid=sec&sid1='+str(code)+'&date='+str(date)+'&page='+str(i)
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.90 Safari/537.36'}
    news = requests.get(url, headers=headers)

    soup = BeautifulSoup(news.content, 'html.parser')

    news_list = soup.select('.newsflash_body .type06_headline li dl')
    news_list.extend(soup.select('.newsflash_body .type06 li dl'))
        
    for line in news_list:
        urllist.append(line.a.get('href'))
  return urllist
url_list = make_urllist(2, 101, 20200506)
print(url_list[:10])

from newspaper import Article

#- 데이터프레임을 생성하는 함수입니다.
def make_data(urllist, code):
  text_list = []
  for url in urllist:
    article = Article(url, language='ko')
    article.download()
    article.parse()
    text_list.append(article.text)

  #- 데이터프레임의 'news' 키 아래 파싱한 텍스트를 밸류로 붙여줍니다.
  df = pd.DataFrame({'news': text_list})

  #- 데이터프레임의 'code' 키 아래 한글 카테고리명을 붙여줍니다.
  #- df['code'] = idx2word[str(code)]
  return df
data = make_data(url_list, 101)
print(data[:10])
