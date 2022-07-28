
from .baby_robot_env_v4 import BabyRobotEnv_v4


class BabyRobotEnv_v5( BabyRobotEnv_v4 ):
  
  def __init__(self, **kwargs):
      super().__init__(**kwargs)   
  
  def render(self, mode='human', info=None ):                 
      ''' render as an HTML5 canvas '''
            
      # move baby robot to the current position
      self.robot.move(self.x,self.y) 

      # write the info to the grid side-panel      
      self.level.show_info(info) 

      return self.level.draw()  

  def show_info(self,info):
      ''' display the supplied information on the grid level '''
      self.level.show_info( info )

  def clear_info(self,all_info=False):
      ''' clear any current information of the grid level '''
      self.level.clear(all_info)       