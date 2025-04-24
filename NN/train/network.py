# CNNのネットワーク構造
from torch import nn


# CNNの構造
class CNN(nn.Module):
    Conv_C = 32
    FC1_C = 128
    FC2_C = 18

    def __init__(self, width, height, channel, classes):
        W = width // 2
        H = height // 2
        inFC_C = W * H * self.Conv_C

        super().__init__()
        
        self.main = nn.Sequential(
            nn.Conv2d(in_channels=channel, out_channels=self.Conv_C, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(self.Conv_C),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2, padding=0),

            nn.Flatten(),
            nn.Linear(in_features=inFC_C, out_features=self.FC1_C),
            nn.ReLU(inplace=True),

            nn.Linear(in_features=self.FC1_C, out_features=classes)
        )
    
    def forward(self, x):
        return self.main(x)
