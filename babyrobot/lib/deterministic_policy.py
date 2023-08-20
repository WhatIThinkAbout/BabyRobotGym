from typing import List
from ..envs import BabyRobotInterface
from ..envs.lib.actions import Actions
from .policy import Policy


class DeterministicPolicy(Policy):
  ''' a really simple deterministic policy class
      - given a list of actions it will simply return the next action when the state changes
  '''
        
  def __init__(self, level: BabyRobotInterface, actions: List[Actions]):    
    super().__init__( level )    
    self.actions = actions
    self.action_index = -1
    self.last_x = -1
    self.last_y = -1
        
  def get_action(self,x:int,y:int) -> Actions:  
    if x != self.last_x or y != self.last_y:
        self.action_index += 1
        if self.action_index > len(self.actions): self.action_index = 0
        self.last_x = x
        self.last_y = y
    return self.actions[self.action_index]