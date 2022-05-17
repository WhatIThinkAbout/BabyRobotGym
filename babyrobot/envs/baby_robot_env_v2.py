
import numpy as np
from .baby_robot_env_v1 import BabyRobotEnv_v1
from enum import IntEnum


''' simple helper class to enumerate actions in the grid levels '''
class Actions(IntEnum):      
    North = 0
    East = 1
    South = 2
    West = 3

    # get the enum name without the class
    def __str__(self): return self.name  



class BabyRobotEnv_v2( BabyRobotEnv_v1 ):

  metadata = {'render_modes': ['human']}
  
  def __init__(self, **kwargs):
      super().__init__()
      
      # the start and end positions in the grid
      # - by default these are the top-left and bottom-right respectively
      self.start = kwargs.get('start',[0,0])       
      self.end = kwargs.get('end',[self.max_x,self.max_y])        
      
      # Baby Robot's initial position
      # - by default this is the grid start 
      self.initial_pos = kwargs.get('initial_pos',self.start)  
      
      
  def take_action(self, action):
      ''' apply the supplied action '''
      
      # move in the direction of the specified action
      if   action == Actions.North: self.y -= 1
      elif action == Actions.South: self.y += 1
      elif action == Actions.West:  self.x -= 1
      elif action == Actions.East:  self.x += 1    
      
      # make sure the move stays on the grid
      if self.x < 0: self.x = 0
      if self.y < 0: self.y = 0
      if self.x > self.max_x: self.x = self.max_x
      if self.y > self.max_y: self.y = self.max_y        

        
  def step(self, action): 

      # take the action and update the position
      self.take_action(action)
      obs = {"x": np.array([self.x]).astype(np.int32), "y": np.array([self.y]).astype(np.int32)}
      
      # set the 'done' flag if we've reached the exit
      done = (self.x == self.end[0]) and (self.y == self.end[1])
      
      # get -1 reward for each step
      # - except at the terminal state which has zero reward
      reward = 0 if done else -1
        
      info = {}
      return obs, reward, done, info     


  def render(self, mode='human', action=0, reward=0 ):
      if mode == 'human':
        print(f"{Actions(action): <5}: ({self.x},{self.y}) reward = {reward}") 
      else:
        super().render(mode=mode) # just raise an exception      