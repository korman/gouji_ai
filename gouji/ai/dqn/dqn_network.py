import torch.nn.functional as F
import torch.nn as nn


class DQNNetwork(nn.Module):
    """深度Q网络模型"""

    def __init__(self, input_size, output_size):
        super(DQNNetwork, self).__init__()
        # 定义网络结构
        self.fc1 = nn.Linear(input_size, 512)
        self.fc2 = nn.Linear(512, 256)
        self.fc3 = nn.Linear(256, 128)
        self.fc4 = nn.Linear(128, output_size)

    def forward(self, x):
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = F.relu(self.fc3(x))
        return self.fc4(x)
