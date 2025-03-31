import torch.nn as nn  # 导入PyTorch的神经网络模块，用于构建深度学习模型


class PokerDQN(nn.Module):
    """
    深度Q网络架构，使用Dueling DQN结构实现扑克牌游戏的AI决策模型

    Dueling DQN将Q值分解为状态价值函数V(s)和优势函数A(s,a)，有助于更好地评估状态价值
    """

    def __init__(self, state_size, action_size, hidden_size=256):
        """
        初始化Dueling DQN网络模型

        参数:
            state_size (int): 输入状态向量的维度
            action_size (int): 动作空间的大小，即可选动作的数量
            hidden_size (int): 隐藏层的神经元数量，默认为256
        """
        super(PokerDQN, self).__init__()

        # 特征提取层 - 共享网络部分
        self._feature_network = nn.Sequential(
            nn.Linear(
                state_size, hidden_size
            ),  # 第一层全连接层，将状态映射到隐藏层大小
            nn.ReLU(),  # ReLU激活函数引入非线性
            nn.Linear(hidden_size, hidden_size),  # 第二层全连接层，保持隐藏层大小不变
            nn.ReLU(),  # ReLU激活函数
        )

        # 优势流和价值流 (Dueling DQN架构)
        self._advantage_stream = nn.Linear(
            hidden_size, action_size
        )  # 优势函数A(s,a)，计算每个动作的相对优势
        self._value_stream = nn.Linear(
            hidden_size, 1
        )  # 状态价值函数V(s)，估计当前状态的基础价值

    def forward(self, x):
        """
        前向传播函数，定义网络的计算流程

        参数:
            x (torch.Tensor): 输入的游戏状态张量

        返回:
            torch.Tensor: 每个可能动作的Q值估计
        """
        features = self._feature_network(x)  # 通过共享网络提取状态特征

        advantage = self._advantage_stream(features)  # 计算每个动作的优势值
        value = self._value_stream(features)  # 计算状态的基础价值

        # 合并优势和价值 (Q = V + A - mean(A))
        # 这种方式确保了优势函数的均值为0，使训练更加稳定
        q_values = value + (advantage - advantage.mean(dim=1, keepdim=True))

        return q_values  # 返回每个动作的Q值估计
