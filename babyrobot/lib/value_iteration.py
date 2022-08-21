# Copyright (c) Steve Roberts
# Distributed under the terms of the Modified BSD License.


import numpy as np
from numpy import inf

from babyrobot.envs import BabyRobotInterface
from babyrobot.envs.lib.direction import Direction


class ValueIteration():

  def __init__(self, env: BabyRobotInterface, discount_factor=0.9):
    self.level = env
    self.values = np.zeros((env.height,env.width))
    self.discount_factor = discount_factor


  def get_state_value(self,pos):
    ''' get the currently calculated value of the specified position in the grid '''
    x = pos[0]
    y = pos[1]
    if (x < 0 or x >= self.level.width) or (y < 0 or y >= self.level.height): 
      return 0
    return self.values[y,x]


  def calculate_max_action_value(self,x,y):
    ''' 
        calculate the values of all actions in the specified cell and return the largest of these
        - the next state value is given by:  v(s) = max[r + γv(s')]       
    '''    
    # get the probability of moving to the intended target from this state
    transition_probability = self.level.get_transition_probability( x, y )

    # get the list of all possible actions in this state
    all_actions = self.level.get_available_actions(x,y)

    # when an action is taken will either end in target state or one of the other possible states
    # - count the number of states other than the target state
    num_alternative_states = len(all_actions) - 1 

    # calculate the value of each action in the state and save the largest
    max_value = float('-inf')
    for chosen_action in all_actions:

      # sum the values of the possible next states
      value = 0  
      for action in all_actions:

        if action == chosen_action:
          # the chosen action is taken with the cell's transition probability
          probability = transition_probability
        else:
          # the probability of ending up in another state is divided by the total number of other possible states
          probability = (1-transition_probability)/num_alternative_states

        # get the reward for moving from the current cell in this direction
        reward, next_pos = self.level.get_reward( x, y, Direction.from_action(action) )   

        # combine the reward with discounted value of the next state and 
        # sum over each of the transition probabilities p(s'|s,a)
        value += probability * (reward + (self.discount_factor * self.get_state_value( next_pos ))) 

      # save the largest value
      if value > max_value:
        max_value = value              
    
    # return the value of the largest action-value in this state
    return max_value


  def state_sweep(self):
    ''' calculate the value of all states except the exit '''
    
    new_values = np.zeros((self.level.height,self.level.width))
    end = self.level.end
    for y in range(self.level.height):
      for x in range(self.level.width):
        if (x != end[0]) or (y != end[1]):          
          new_values[y,x] = self.calculate_max_action_value(x,y)    

    # calculate the largest difference in the state values between the start and end of the sweep    
    delta = np.max(np.abs(new_values - self.values))           
    
    # update the state values with the newly calculated values 
    # (set any -inf to NaN for states where no value calculated)
    new_values[new_values == -inf] = np.nan
    self.values = new_values

    # return the largest state value difference 
    return delta


  def run_to_convergence(self, max_iterations = 100, threshold = 1e-3):
    ''' run multiple state sweeps until the maximum change in the state value falls
        below the supplied threshold or the maximum number of iterations is reached
    '''    
    for n in range(max_iterations):
      
      # calculate the maximum action value in each state and get the largest state value difference
      delta = self.state_sweep()        
      
      # test if the difference is less than the defined convergence threshold
      if delta < threshold:
        break
    
    # return the number of iterations taken to converge
    return n