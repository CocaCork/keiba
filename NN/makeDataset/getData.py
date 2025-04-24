import csv
import os
import re
import requests
from bs4 import BeautifulSoup


class GetData():
    def __init__(self, savedir, str_code, home_url, race_url):
        self.savedir = savedir
        self.str_code = str_code
        self.home_url = home_url
        self.race_url = race_url
        self.horse_url = {}

    def urlToSoup(self, url):
        req = requests.get(url)
        return BeautifulSoup(req.content, 'html.parser')

    # 各馬の過去情報があるページへのリンク取得
    def getHorsePageLink(self):
        soup = self.urlToSoup(self.race_url)
        td_list_num = soup.find('tbody').find_all('td', class_='num')
        td_list_name = soup.find_all('td', class_='horse')
        for i, j in zip(td_list_num, td_list_name):
            num = str(i.string)
            name = str(j.find('a').string)
            horse_page = self.home_url + j.find('a').get('href')
            self.horse_url['{}_{}'.format(num, name)] = horse_page
        
        # ついでに使用する情報を取得
        self.winner = str(soup.find('tbody').find(class_='num').string)
        self.race_date = re.search(r'[0-9]+年[0-9]+月[0-9]+日', soup.find('div', class_='cell date').string).group()
        self.race_place = re.search(r'(?<=回).+(?=[0-9]+日)', soup.find('div', class_='cell date').string).group()
        self.race_type = str(soup.find('li', class_='turf').find('span', class_='cap').string)
        self.race_status = str(soup.find('li', class_='turf').find('span', class_='txt').string)
        self.race_length = re.search(r'([0-9]|,)+(?=<span class="unit">)', str(soup.find('div', class_='cell course'))).group().replace(',', '')

    def getHorseData(self, horse_page):
        self.csv_header = []
        self.csv_body = []

        soup = self.urlToSoup(horse_page)

        thead = soup.find('table', class_='basic narrow-xy striped').find_all('th')
        tbody = soup.find('table', class_='basic narrow-xy striped').find('tbody').find_all('tr')

        for th in thead:
            self.csv_header.append(str(th.string))

        for tr in tbody:
            data = []
            for n, td in enumerate(tr.find_all('td')):
                if n == 2:  # 3番目のカラムはレース名であり、タグの関係で特別な取得方法をする必要があるため場合分け
                    if td.find('a'):
                        data.append(str(td.find('a').string))
                    else:
                        data.append(re.sub(r'<[^>]*>', '', str(td)))
                else:
                    data.append(str(td.string))
            self.csv_body.append(data)

    def main(self):
        race_id = re.search(r'(?<=CNAME=).*', self.race_url).group().replace('/', '_')
        savefolder = '{}/{}'.format(self.savedir, race_id)
        os.makedirs(savefolder, exist_ok=True)

        self.getHorsePageLink()
        for horse_name, horse_page in self.horse_url.items():
            self.getHorseData(horse_page)

            with open('{}/{}.csv'.format(savefolder, horse_name), 'w', encoding=self.str_code, newline='') as f:
                writer = csv.writer(f)
                writer.writerow(self.csv_header)
                writer.writerows(self.csv_body)

        with open('{}/label.txt'.format(savefolder), 'w', encoding=self.str_code, newline='') as f:
            f.write(self.winner)

        with open('{}/info.txt'.format(savefolder), 'w', encoding=self.str_code, newline='') as f:
            f.write(self.race_date + '\n')
            f.write(self.race_place + '\n')
            f.write(self.race_type + '\n')
            f.write(self.race_length + '\n')
            f.write(self.race_status)
