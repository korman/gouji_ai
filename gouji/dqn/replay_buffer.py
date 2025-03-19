import torch
import random
import numpy as np
from collections import deque


class ReplayBuffer:
    """经验回放缓冲区"""

    def __init__(self, capacity=10000):
        self.buffer = deque(maxlen=capacity)

    def add(self, state, action, reward, next_state, done, valid_actions_mask):
        self.buffer.append(
            (state, action, reward, next_state, done, valid_actions_mask))

    def sample(self, batch_size):
        batch = random.sample(self.buffer, min(len(self.buffer), batch_size))
        states, actions, rewards, next_states, dones, valid_actions_masks = zip(
            *batch)

        return (
            torch.FloatTensor(np.array(states)),
            torch.LongTensor(np.array(actions)),
            torch.FloatTensor(np.array(rewards)),
            torch.FloatTensor(np.array(next_states)),
            torch.FloatTensor(np.array(dones)),
            torch.FloatTensor(np.array(valid_actions_masks))
        )

    def __len__(self):
        return len(self.buffer)
