import torch.nn as nn


class PokerDQN(nn.Module):
    """深度Q网络架构"""

    def __init__(self, state_size, action_size, hidden_size=256):
        super(PokerDQN, self).__init__()

        # 特征提取层
        self.feature_network = nn.Sequential(
            nn.Linear(state_size, hidden_size),
            nn.ReLU(),
            nn.Linear(hidden_size, hidden_size),
            nn.ReLU(),
        )

        # 优势流和价值流 (Dueling DQN架构)
        self.advantage_stream = nn.Linear(hidden_size, action_size)
        self.value_stream = nn.Linear(hidden_size, 1)

    def forward(self, x):
        features = self.feature_network(x)

        advantage = self.advantage_stream(features)
        value = self.value_stream(features)

        # 合并优势和价值 (Q = V + A - mean(A))
        q_values = value + (advantage - advantage.mean(dim=1, keepdim=True))

        return q_values
