import torch
import random
import numpy as np
from collections import deque


class ReplayBuffer:
    """经验回放缓冲区

    用于存储和采样智能体与环境交互产生的经验(state, action, reward, next_state, done)。
    经验回放可以打破样本间的时序相关性，提高训练稳定性，并允许经验的多次使用。

    属性:
        _buffer (deque): 有限容量的双端队列，用于存储经验元组
    """

    def __init__(self, capacity=10000):
        """初始化经验回放缓冲区

        参数:
            capacity (int): 缓冲区最大容量，超过此容量时最早的经验会被移除
        """
        self._buffer = deque(maxlen=capacity)  # 创建固定容量的双端队列

    def add(self, state, action, reward, next_state, done):
        """向缓冲区添加一条经验

        参数:
            state: 当前状态
            action: 执行的动作
            reward: 获得的奖励
            next_state: 转移到的下一个状态
            done: 回合是否结束的标志
        """
        self._buffer.append(
            (state, action, reward, next_state, done)
        )  # 将经验元组添加到缓冲区

    def sample(self, batch_size):
        """从缓冲区随机采样一批经验用于训练

        参数:
            batch_size (int): 采样的批次大小

        返回:
            tuple: 包含批量states, actions, rewards, next_states, dones的元组
                  每个元素都是相应数据类型的列表
        """
        batch = random.sample(self._buffer, batch_size)  # 随机采样指定数量的经验
        states, actions, rewards, next_states, dones = zip(*batch)  # 解包批次数据
        return states, actions, rewards, next_states, dones  # 返回分组后的数据

    def __len__(self):
        """返回缓冲区中当前存储的经验数量

        返回:
            int: 缓冲区中的经验数量
        """
        return len(self._buffer)  # 返回当前缓冲区长度
