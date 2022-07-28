import numpy as np

from .baby_robot_env_v5 import BabyRobotEnv_v5
from .lib.direction import Direction
from .lib.actions import Actions


class BabyRobotEnv_v6( BabyRobotEnv_v5 ):
  
  def __init__(self, **kwargs):
      super().__init__(**kwargs) 

  
  def take_action(self, action):
      ''' apply the supplied action 

          returns:
          - the reward obtained for taking the action
          - a flag to indicate if the target state was reached - if it wasn't this indicates
            that a slip has occurred
      '''      

      # convert the action into a direction bitfield
      direction = Direction.from_action(action) 
        
      # calculate the postion of the next state and the reward for moving there
      next_pos,reward,target_reached = self.level.get_next_state( self.x, self.y, direction )  

      # store the new position
      self.x = next_pos[0]
      self.y = next_pos[1]
  
      # update the available actions for the new position        
      self.set_available_actions()      

      return reward, target_reached  


  def step(self, action): 

      # take the action and update the position
      reward, target_reached = self.take_action(action)      
      obs = np.array([self.x,self.y])      
           
      # set the 'done' flag if we've reached the exit
      done = (self.x == self.end[0]) and (self.y == self.end[1])
        
      info = {'target_reached':target_reached}
      return obs, reward, done, info            