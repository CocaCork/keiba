import numpy as np
import os
import pandas as pd
import statistics
import torch
import torchvision
from PIL import Image
from torch import nn
from tqdm import tqdm
# 自作モジュール
from network import CNN
from load import LoadDataset, LoadData
from util import evaluate, plot, output_env


# ロスの計算
class MyLoss():
    def __init__(self):
        self.CE_loss = nn.CrossEntropyLoss()

    def loss(self, x, y):
        return self.CE_loss(x, y)


class Train():
    def __init__(self, savedir, epochs, batch_size):
        # Adam設定(default: lr=0.001, betas=(0.9, 0.999), weight_decay=0) 
        self.opt_para = {'lr': 0.001, 'betas': (0.9, 0.999), 'weight_decay': 0}

        self.width = 10     # 使用する特徴量の種類数
        self.height = 7     # 参照する過去レースの数
        self.channel = 18   # 1レースの頭数

        self.classes = 18
        self.train_races = 7

        self.savedir = savedir
        self.epochs = epochs
        self.batch_size = batch_size

    def main(self):
        myloss = MyLoss()

        # 保存先のファイルを作成
        if os.path.exists(self.savedir):
            num = 1
            while 1:
                if os.path.exists('{}({})'.format(self.savedir, num)):
                    num += 1
                else:
                    self.savedir = '{}({})'.format(self.savedir, num)
                    break
        os.makedirs(self.savedir, exist_ok=True)
        os.makedirs('{}/model'.format(self.savedir), exist_ok=True)
        os.makedirs('{}/loss'.format(self.savedir), exist_ok=True)

        # モデルの読み込み
        model = CNN(self.width, self.height, self.channel, self.classes)
        model = nn.DataParallel(model)
        # model = model.to(device)

        # 最適化アルゴリズムの設定
        para = torch.optim.Adam(model.parameters(), lr=self.opt_para['lr'], betas=self.opt_para['betas'], weight_decay=self.opt_para['weight_decay'])

        # ロスの推移を保存するためのリストを確保
        result = []

        ld = LoadData('../dataset', self.classes, self.train_races)
        dt, label = ld.load()

        custom_dataset = LoadDataset(dt, label)
        train_loader = torch.utils.data.DataLoader(dataset=custom_dataset, batch_size=self.batch_size, shuffle=True)

        # パラメータ設定，ネットワーク構造などの環境をテキストファイルで保存．
        output_env('{}/env.txt'.format(self.savedir), self.batch_size, self.opt_para, model)

        for epoch in range(self.epochs):
            print('#################### epoch: {}/{} ####################'.format(epoch+1, self.epochs))

            log_loss = []

            for data, label in tqdm(train_loader):
                # 画像とラベルをGPU用変数に設定
                # img = img.to(device)
                # label = label.to(device)

                # モデルにデータを入力
                output = model(data)

                # ロスを計算
                loss = myloss.loss(output, label)
                log_loss.append(loss.item())

                # 微分計算，重み更新
                para.zero_grad()
                loss.backward()
                para.step()

            # ロスのログを保存し，各エポック終わりにロスを表示．
            result.append(statistics.mean(log_loss))
            print('loss = {}'.format(result[-1]))

            # ロスのログを保存
            with open('{}/loss/log.txt'.format(self.savedir), mode='a') as f:
                f.write('Epoch {:03}: {}\n'.format(epoch+1, result[-1]))
            
            # 定めた保存周期ごとにモデル，ロスを保存．
            if (epoch+1)%10 == 0:
                # モデルの保存
                torch.save(model.module.state_dict(), '{}/model/model_{}.pth'.format(self.savedir, epoch+1))

            if (epoch+1)%50 == 0:
                # ロス（画像）の保存
                x = np.linspace(1, epoch+1, epoch+1, dtype='int')
                plot(result, x, self.savedir)

            # 各エポック終わりに，テストデータに対する精度を計算．
            # evaluate(model, test_loader)

        # 最後のエポックが保存周期でない場合に，保存．
        if epoch+1 == self.epochs and (epoch+1)%10 != 0:
            torch.save(model.module.state_dict(), '{}/model/model_{}.pth'.format(self.savedir, epoch+1))

            x = np.linspace(1, epoch+1, epoch+1, dtype='int')
            plot(result, x, self.savedir)
    

if __name__ == '__main__':
    tr = Train('../progress/tmp', 50, 1)
    tr.main()
