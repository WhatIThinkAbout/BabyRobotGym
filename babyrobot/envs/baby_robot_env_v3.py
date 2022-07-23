import numpy as np

from .baby_robot_env_v2 import BabyRobotEnv_v2

from .lib.grid_level import GridLevel
from .lib.robot_draw import RobotDraw
from .lib.actions import Actions


''' the first graphical environment '''
class BabyRobotEnv_v3( BabyRobotEnv_v2 ):    
  
  def __init__(self, **kwargs):
      super().__init__(**kwargs)
      
      # graphical creation of the level
      self.level = GridLevel( **kwargs )  
      
      # add baby robot
      self.robot = RobotDraw(self.level,**kwargs)   
      self.robot.draw()        
      
  def reset(self):
      # reset Baby Robot's position in the grid
      self.robot.set_cell_position(self.initial_pos)      
      self.robot.reset()               
      self.x = self.initial_pos[0]
      self.y = self.initial_pos[1]        
      return np.array([self.x,self.y])      
      
  def render(self, mode='human', action=0, reward=0 ):                
      ''' render as an HTML5 canvas '''
      print(f"{Actions(action): <5}: ({self.x},{self.y}) reward = {reward}")    
      
      # move baby robot to the current position
      self.robot.move(self.x,self.y) 
      return self.level.draw() 