# その他いろいろ
import matplotlib.pyplot as plt
import datetime
import os
import re
import torch


# 年月日を比較する関数
def compDate(a, b):
    aa = datetime.date(int(re.search(r'[0-9]+(?=年)', a).group()), int(re.search(r'(?<=年)[0-9]+(?=月)', a).group()), int(re.search(r'(?<=月)[0-9]+(?=日)', a).group()))
    bb = datetime.date(int(re.search(r'[0-9]+(?=年)', b).group()), int(re.search(r'(?<=年)[0-9]+(?=月)', b).group()), int(re.search(r'(?<=月)[0-9]+(?=日)', b).group()))

    if aa < bb:
        return True
    else:
        return False
    

# テストデータに対する精度を計算
def evaluate(model, test_loader):
    device = 'cuda'

    model.eval()    # 推論モードへ切り替え（Dropoutなどの挙動に影響）
    
    # メモリ節約のためパラメータの保存は止める（テスト時にパラメータの保存は不要）
    with torch.no_grad():
        correct = 0

        for img, label in test_loader:
            img = img.to(device)

            output = model(img)
            pred = output.data.max(1, keepdim=False)[1]
            for i, l in enumerate(label):
                if l == pred[i]:
                    correct += 1

        data_num = len(test_loader.dataset)  # データの総数
        acc = correct / data_num * 100 # 精度

        print('Accuracy for test dataset: {}/{} ({:.2f}%)'.format(correct, data_num, acc))

    model.train()


# ロスの履歴をプロット
def plot(loss, epochs, dirname):
    fig = plt.figure(figsize=(4.8, 4.8))

    ax = fig.add_subplot(1, 1, 1)
    ax.plot(epochs, loss)
    ax.set_title('Loss')
    ax.set_xlabel('epoch')
    ax.set_ylabel('loss')
        
    os.makedirs(dirname, exist_ok=True)
    fig.savefig('{}/loss/loss_{}.png'.format(dirname, len(epochs)))

    plt.close()


# 環境をアウトプットしてテキストファイルで保存
def output_env(filepath, batch_size, opt_para, model):
    text_set = '##### Setting #####\nMinibatch size: {}\n\n'.format(batch_size)
    text_optimizer = '##### Optimizer Parameter #####\nlr: {}, betas: {}, weight_decay: {}\n\n'.format(opt_para['lr'], opt_para['betas'], opt_para['weight_decay'])
    text_model = '##### Model #####\n{}\n'.format(model)
    with open(filepath, mode='w') as f:
        f.write(text_set)
        f.write(text_optimizer)
        f.write(text_model)
