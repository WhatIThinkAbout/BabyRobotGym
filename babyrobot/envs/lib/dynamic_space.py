import gym
import numpy as np

class Dynamic(gym.Space):

  def __init__(self, action_list = []):
      ' set the list of initially available actions '      
      self.set_actions(action_list)
      
  def sample(self):
      ' select a random action from the set of available actions '
      return np.random.choice(self.available_actions)    
    
  def set_actions(self,actions):
      self.available_actions = actions
      self.n = len(actions)    
      
  def get_available_actions(self):
      return [str(action) for action in self.available_actions] 