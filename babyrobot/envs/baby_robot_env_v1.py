import numpy as np
import gym
from gym.spaces import Discrete,Box,Dict


class BabyRobotEnv_v1(gym.Env):
  
    def __init__(self, **kwargs):
        super().__init__()

        # dimensions of the grid
        self.width = kwargs.get('width',3)
        self.height = kwargs.get('height',3)      
      
        # define the maximum x and y values
        self.max_x = self.width - 1
        self.max_y = self.height - 1

        # there are 5 possible actions: move N,E,S,W or stay in same state
        self.action_space = Discrete(5)          

        # the observation will be the coordinates of Baby Robot
        # - by using a dictionary we can define the limits in each direction  
        x_space = Box(low=0, high=self.max_x, shape=(1,), dtype=np.int32)
        y_space = Box(low=0, high=self.max_y, shape=(1,), dtype=np.int32)       
        self.observation_space = Dict({"x": x_space, "y": y_space})
        
        # Baby Robot's position in the grid
        self.x = 0
        self.y = 0

    def step(self, action):        
        obs = {"x": np.array([self.x]).astype(np.int32), "y": np.array([self.y]).astype(np.int32)}
        reward = -1            
        done = True
        info = {}
        return obs, reward, done, info

    def reset(self):
        # reset Baby Robot's position in the grid
        self.x = 0
        self.y = 0        
        return {"x": np.array([self.x]).astype(np.int32), "y": np.array([self.y]).astype(np.int32)}
  
    def render(self):
        pass