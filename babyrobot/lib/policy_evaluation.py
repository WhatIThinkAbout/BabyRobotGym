# Copyright (c) Steve Roberts
# Distributed under the terms of the Modified BSD License.

import numpy as np
from babyrobot.envs import BabyRobotInterface
from babyrobot.envs.lib.direction import Direction
from babyrobot.lib import Policy


''' evaluate a policy '''
class PolicyEvaluation():

  iterations = 0
  policy = None
  discount_factor = 1.0  
  threshold = 1e-3

  def __init__(self, env: BabyRobotInterface, policy: Policy, discount_factor=1.0):
    self.level = env

    # check that a policy has been given to evaluate
    assert policy is not None, "A Policy must be supplied to PolicyEvaluation." 

    self.policy = policy
    self.discount_factor = discount_factor
    self.reset()


  def reset(self):
    self.iterations = 0
    self.reset_start_values()
    self.reset_end_values()


  def reset_start_values(self):
    self.start_values = np.zeros((self.level.height,self.level.width))    


  def reset_end_values(self):
    self.end_values = np.zeros((self.level.height,self.level.width))  


  def get_state_value(self,pos):
    ''' get the currently calculated value of the specified position in the grid '''
    x = pos[0]
    y = pos[1]
    if (x < 0 or x >= self.level.width) or (y < 0 or y >= self.level.height): 
      return 0
    return self.start_values[y,x]


  def calculate_action_value(self,x,y,chosen_action,all_actions):

    # get the probability of moving to the intended target from this state
    transition_probability = self.level.get_transition_probability( x, y )    

    # the number of other states where baby robot can end up if he doesnt reach the target state
    num_alternative_states = len(all_actions) - 1 

    # sum the values of the possible next states
    action_value = 0
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
      action_value += probability * (reward + (self.discount_factor * self.get_state_value( next_pos )))

    return action_value 


  def calculate_cell_value(self,x,y):
    ''' calculate the state value when all actions are equally possible '''

    # get the list of all possible actions in this state
    all_actions = self.level.get_available_actions(x,y)

    # when an action is taken it will either end in target state or one of the other possible states
    # - count the number of states other than the target state
    num_actions = len(all_actions)
    if num_actions > 0:
            
      # calculate the total value for all possible actions in this state
      value = 0
      for chosen_action in all_actions:
        action_value = self.calculate_action_value(x,y,chosen_action,all_actions)       

        # add the action value to the total state value        
        value += action_value        

      # for equal probability of taking an action its just the mean of all actions
      return value/num_actions
    
    # no possible actions
    return 0


  def calculate_policy_cell_value(self,x,y):
    ''' calculate the state value for a policy '''             

    # get the dictionary of possible actions and their probabilities in this state   
    actions = self.policy.get_action_probabilities(x,y)   
    all_actions = list(actions.keys())
    probabilities = list(actions.values())     

    # when an action is taken it will either end in target state or one of the other possible states
    # - count the number of states other than the target state
    num_actions = len(all_actions)
    if num_actions > 0:                 
            
      # calculate the total value for all possible actions in this state
      value = 0
      for chosen_action,probability in zip(all_actions,probabilities):
        action_value = self.calculate_action_value(x,y,chosen_action,all_actions)       

        # add the action value, multiplied by the probability of taking that action, to the total state value        
        value += (probability * action_value)
      
      return value
    
    # no possible actions
    return 0  


  def standard_sweep(self):
    ''' calculate the state value for all states '''                
    # calculate the value of all states except the exit
    end = self.level.end
    for y in range(self.level.height):
      for x in range(self.level.width):
        if (x != end[0]) or (y != end[1]):          
          if self.policy is None:
            # use stochastic policy
            self.end_values[y,x] = self.calculate_cell_value(x,y)   
          else:
            # calculate value under deterministic policy
            self.end_values[y,x] = self.calculate_policy_cell_value(x,y)  


  def do_iteration(self):        
    self.start_values = self.end_values   # copy the end values into the start values            
    self.reset_end_values()               # reset the end values        
    self.standard_sweep()                 # sweep all states    
    self.iterations += 1                  # increment the iteration count


  def run_to_convergence(self, max_iterations = 100, threshold = 1e-3):
    ''' run until the values stop changing '''
    for n in range(max_iterations):
      self.do_iteration()
      
      # calculate the largest difference in the state values from the start to end of the iteration
      delta = np.max(np.abs(self.end_values - self.start_values))            
      
      # test if the difference is less than the defined convergence threshold
      if delta < threshold:
        break
    
    # return the number of iterations taken to converge
    return n


  def set_policy(self, policy: Policy):
    ''' set the policy to be evaluated '''
    self.policy = policy
    
    # reset the iterations required to run to convergence on the policy
    self.iterations = 0
    

  def set_discount_factor(self, discount_factor):
    ''' set the discount factor to apply to the future rewards '''
    self.discount_factor = discount_factor


  def get_iterations(self):
    ''' return the number of iterations of policy evalutation that have been performed '''
    return self.iterations