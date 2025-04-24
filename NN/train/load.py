import csv
import datetime
import glob
import numpy as np
import os
import torch
import torchvision
from util import compDate


class LoadDataset(torch.utils.data.Dataset):
    def __init__(self, datas, labels):
        self.datas = datas.transpose(0, 3, 2, 1)
        self.labels = labels
    
    def __len__(self):
        return len(self.datas)
    
    def __getitem__(self, i):
        trans = torchvision.transforms.ToTensor()
        data = trans(self.datas[i])
        label = self.labels[i]
        return data, label


class LoadData():
    def __init__(self, data_path, classes, max_race_num):
        self.data_path = data_path
        self.classes = classes
        self.max_race_num = max_race_num

    def transData(self, data):
        for n, dt in enumerate(data):
            if dt == 'None' or dt == '除外' or dt == '取消' or dt == '中止' or dt == '計不':
                data[n] = 0
        data.pop(0)     # レース日 削除
        data.pop(1)     # レース名 削除
        data.pop(6)     # 騎手名 削除
        data.pop(9)     # レーティング 削除
        data.pop(9)     # 1着馬 削除
        # コースタイプと距離を分離する
        if data[1] == 0:
            data.insert(1, 0)
        else:
            data.insert(1, data[1][0])
            data[2] = data[2][1:]

        # 予想レースと同じ競馬場であれば1異なれば0
        if data[0] == self.race_place:
            data[0] = 1
        else:
            data[0] = 0

        # 予想レースと同じコースタイプ(芝・ダート)であれば1異なれば0
        if data[1] == self.race_type:
            data[1] = 1
        else:
            data[1] = 0

        # 予想レースとの距離の差分をとる
        data[2] = abs(int(data[2]) - int(self.race_length))

        # 予想レースと同じ馬場状態であれば1異なれば0
        if data[3] == self.race_status:
            data[3] = 1
        else:
            data[3] = 0

        # タイムは単位を秒に変換
        if ':' in str(data[9]):
            t = datetime.datetime.strptime(data[9], '%M:%S.%f')
            data[9] = float('{}.{}'.format(datetime.timedelta(seconds=t.second, microseconds=t.microsecond, minutes=t.minute).seconds,
                                           datetime.timedelta(seconds=t.second, microseconds=t.microsecond, minutes=t.minute).microseconds))
            
        data = [float(i) for i in data]

        return data


    def load(self):
        dir_list = []

        for f in os.listdir(self.data_path):
            path = os.path.join(self.data_path, f)
            if os.path.isdir(path):
                dir_list.append(path)

        dataset = []
        labels = []

        for d in dir_list:
            one_race_dataset = []
            file_list = glob.glob('{}/*csv'.format(d))

            with open('{}/info.txt'.format(d), mode='r', encoding='utf-8', newline='') as f:
                line_list = f.read().splitlines()
                race_date =  line_list[0]
                self.race_place = line_list[1]
                self.race_type = line_list[2]
                self.race_length = line_list[3]
                self.race_status = line_list[4]

            with open('{}/label.txt'.format(d), mode='r', encoding='utf-8', newline='') as f:
                lb = int(f.readline())
            label = [0] * self.classes
            label[lb-1] = 1
            labels.append(label)

            for filepath in file_list:
                one_horse_dataset = []
                count = 0
                with open(filepath, mode='r', encoding='utf-8', newline='') as f:
                    header = next(csv.reader(f))
                    reader = csv.reader(f)
                    for row in reader:
                        if compDate(row[0], race_date) == True:
                            one_horse_dataset.append(self.transData(row))
                            count += 1
                            if count == self.max_race_num:
                                break
                if count < self.max_race_num:
                    num = self.max_race_num - count
                    for _ in range(num):
                        one_horse_dataset.append([0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
        
                one_race_dataset.append(one_horse_dataset)

            dataset.append(one_race_dataset)

        dataset = np.array(dataset, dtype='float32')
        labels = np.array(labels, dtype='float32')

        return dataset, labels


# if __name__ == '__main__':
#     ld = LoadData('../dataset', 7)
#     ld.load()
