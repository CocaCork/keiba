import csv
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm


horse_url = {}


def urlToSoup(url):
    req = requests.get(url)
    return BeautifulSoup(req.content, 'html.parser')


# 各馬の過去情報があるページへのリンク取得
def getHorsePageLink(home_url, url):
    soup = urlToSoup(url)
    td_list = soup.find_all('td', class_='horse')
    for t in td_list:
        horse_name = str(t.find('a').string)
        horse_page = home_url + t.find('a').get('href')
        horse_url[horse_name] = horse_page


def getHorseData(horse_name, horse_page, savefile):
    csv_header = []
    csv_body = []

    soup = urlToSoup(horse_page)

    thead = soup.find('table', class_='basic narrow-xy striped').find_all('th')
    tbody = soup.find('table', class_='basic narrow-xy striped').find('tbody').find_all('tr')

    for th in thead:
        csv_header.append(str(th.string))

    for tr in tbody:
        data = []
        for n, td in enumerate(tr.find_all('td')):
            if n == 2:  # 3番目のカラムはレース名であり、aタグのラベルを取得する必要があるため場合分け
                data.append(str(td.find('a').string))
            else:
                data.append(str(td.string))
        csv_body.append(data)

    with open('{}/{}.csv'.format(savefile, horse_name), 'w') as f:
        writer = csv.writer(f)
        writer.writerow(csv_header)
        writer.writerows(csv_body)


def main(savefile, home_url, url):
    getHorsePageLink(home_url, url)
    for horse_name, horse_page in tqdm(horse_url.items()):
        getHorseData(horse_name, horse_page, savefile)


if __name__ == '__main__':
    main('../dataset', 'https://www.jra.go.jp', 'https://www.jra.go.jp/JRADB/accessS.html?CNAME=pw01sde1006202503081120250420/B8')
