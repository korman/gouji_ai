import torch.nn.functional as F  # 导入PyTorch的函数式接口，提供激活函数等操作
import torch.nn as nn  # 导入PyTorch的神经网络模块，用于构建深度学习模型


class DQNNetwork(nn.Module):
    """深度Q网络模型，用于强化学习中的Q值估计"""

    def __init__(self, input_size, output_size):
        """
        初始化DQN网络模型。

        参数:
            input_size (int): 输入特征的维度
            output_size (int): 输出动作空间的维度，对应可选动作的数量
        """
        super(DQNNetwork, self).__init__()
        # 定义网络结构
        self._fc1 = nn.Linear(
            input_size, 512
        )  # 第一层全连接层，从输入维度到512个神经元
        self._fc2 = nn.Linear(512, 256)  # 第二层全连接层，从512降维到256个神经元
        self._fc3 = nn.Linear(256, 128)  # 第三层全连接层，从256降维到128个神经元
        self._fc4 = nn.Linear(128, output_size)  # 输出层，从128映射到动作空间的维度

    def forward(self, x):
        """
        前向传播函数，定义了数据通过网络的流程。

        参数:
            x (torch.Tensor): 输入的状态张量

        返回:
            torch.Tensor: 各个动作的Q值估计
        """
        x = F.relu(self._fc1(x))  # 第一层后接ReLU激活函数
        x = F.relu(self._fc2(x))  # 第二层后接ReLU激活函数
        x = F.relu(self._fc3(x))  # 第三层后接ReLU激活函数
        return self._fc4(x)  # 输出层不使用激活函数，直接输出Q值
