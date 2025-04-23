# データ(馬データ)の取得とデータセットの作成
import os
# 自作モジュール
from getData import main
os.chdir(os.path.dirname(os.path.abspath(__file__)))


#############################################################
#  savedir：データセットの保存先ディレクトリのパス
# str_code：出力ファイル(CSV)の文字コード(例：utf-8, shift_jis)
# home_url：ホームページのURL
# race_url：予想したいレースの出馬表ページのURL
#############################################################
savedir = '../dataset'
str_code = 'utf-8'
home_url = 'https://www.jra.go.jp'
race_url = 'https://www.jra.go.jp/JRADB/accessS.html?CNAME=pw01sde1006202503081120250420/B8'


main(savedir, str_code, home_url, race_url)
