# PPO Reinforcement Learning agent for strategy optimization

import os
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
from collections import deque
import random

class PPOAgent:
    def __init__(self, state_size=3, action_size=3, gamma=0.99, lr=0.001):
        self.state_size = state_size
        self.action_size = action_size
        self.gamma = gamma
        self.lr = lr
        self.policy_net = self.build_model()
        self.optimizer = optim.Adam(self.policy_net.parameters(), lr=self.lr)
        self.memory = []

    def build_model(self):
        return nn.Sequential(
            nn.Linear(self.state_size, 64),
            nn.ReLU(),
            nn.Linear(64, self.action_size),
            nn.Softmax(dim=-1)
        )

    def remember(self, state, action, reward):
        self.memory.append((state, action, reward))

    def act(self, state):
        state = torch.FloatTensor(state).unsqueeze(0)
        probs = self.policy_net(state).detach().numpy()[0]
        action = np.random.choice(self.action_size, p=probs)
        return action

    def train(self):
        if not self.memory:
            return
        states, actions, rewards = zip(*self.memory)
        G = 0
        returns = []
        for r in reversed(rewards):
            G = r + self.gamma * G
            returns.insert(0, G)
        returns = torch.FloatTensor(returns)
        for i in range(len(states)):
            state = torch.FloatTensor(states[i]).unsqueeze(0)
            probs = self.policy_net(state)
            dist = torch.distributions.Categorical(probs)
            loss = -dist.log_prob(torch.tensor(actions[i])) * returns[i]
            self.optimizer.zero_grad()
            loss.backward()
            self.optimizer.step()
        self.memory = []

    def save(self, path="ppo_agent.pth"):
        torch.save(self.policy_net.state_dict(), path)

    def load(self, path="ppo_agent.pth"):
        if os.path.exists(path):
            self.policy_net.load_state_dict(torch.load(path))