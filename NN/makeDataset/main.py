# データ(馬データ)の取得とデータセットの作成
import os
from tqdm import tqdm
# 自作モジュール
from getData import GetData
os.chdir(os.path.dirname(os.path.abspath(__file__)))


#############################################################
#  savedir：データセットの保存先ディレクトリのパス
# str_code：出力ファイル(CSV)の文字コード(例：utf-8, shift_jis)
# home_url：ホームページのURL
# race_url：正解データのレースの出馬表ページのURL
#############################################################
savedir = '../dataset'
str_code = 'utf-8'
home_url = 'https://www.jra.go.jp'
race_list = './raceList/dataList_18.txt'

with open(race_list, 'r', encoding=str_code) as f:
    race_url_list = f.read().splitlines()

for race_url in tqdm(race_url_list):
    getData = GetData(savedir, str_code, home_url, race_url)
    getData.main()
