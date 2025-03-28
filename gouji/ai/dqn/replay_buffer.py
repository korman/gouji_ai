import torch
import random
import numpy as np
from collections import deque


class ReplayBuffer:
    """经验回放缓冲区"""

    def __init__(self, capacity=10000):
        self._buffer = deque(maxlen=capacity)

    def add(self, state, action, reward, next_state, done):
        self._buffer.append((state, action, reward, next_state, done))

    def sample(self, batch_size):
        batch = random.sample(self._buffer, batch_size)
        states, actions, rewards, next_states, dones = zip(*batch)
        return states, actions, rewards, next_states, dones

    def __len__(self):
        return len(self._buffer)
