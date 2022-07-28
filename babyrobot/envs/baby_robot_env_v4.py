import numpy as np

import gym
from gym.spaces import Discrete

from .baby_robot_env_v3 import BabyRobotEnv_v3
from .lib.direction import Direction
from .lib.actions import Actions


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



class BabyRobotEnv_v4( BabyRobotEnv_v3 ):
  
  def __init__(self, **kwargs):
      super().__init__(**kwargs)              
      
      # initially no actions are available      
      self.dynamic_action_space = Dynamic() 

      # by default use a dynamic action space 
      if kwargs.get('action_space','dynamic') == 'dynamic':
        self.action_space = self.dynamic_action_space              
      else:
        # use discrete action space 
        # - required for Stable Baselines environment checker which cant yet
        #   recognise dynamic spaces
        # - all actions are available in each state
        # - there are 5 possible actions: move N,E,S,W or stay in same state
        self.action_space = Discrete(5)         

      # set the initial position and available actions
      self.reset() 

   
  def get_available_actions( self ):
      ''' test which actions are allowed at the specified grid state '''      

      # get the available actions from the grid level
      direction_value = self.level.get_directions(self.x,self.y) 

      # convert the grid directions into environment actions
      action_list = []       
      if direction_value & Direction.North: action_list.append( Actions.North )
      if direction_value & Direction.South: action_list.append( Actions.South )
      if direction_value & Direction.East:  action_list.append( Actions.East ) 
      if direction_value & Direction.West:  action_list.append( Actions.West )                
      return action_list     

            
  def set_available_actions( self ):
      ' set the list of available actions into the action space '
      action_list = self.get_available_actions()   
      self.dynamic_action_space.set_actions( action_list )      


  def show_available_actions( self ):
      ''' print the set of avaiable actions for current state '''
      available_actions = str(self.dynamic_action_space.get_available_actions()).replace("'","")
      print(f"({self.x},{self.y}) {available_actions:29}",end="")             
      

  def take_action(self, action):
      ''' apply the supplied action '''

      # call the parent class to take the action and update the position
      super().take_action( action )   
        
      # set the available actions for the new state
      self.set_available_actions()         
      
      
  def reset(self):
      # reset Baby Robot's position in the grid
      result = super().reset()
      self.set_available_actions()
      return result      