# Copyright (c) Steve Roberts
# Distributed under the terms of the Modified BSD License.

import math
import numpy as np
from ..envs import BabyRobotInterface
from ..envs.lib.direction import Direction
from ..envs.lib.actions import Actions

class Policy():

  def __init__(self, level: BabyRobotInterface, directions: np.array = None, seed = None):
    self.level = level
    if directions is None:
      # if no directions are supplied create a policy where all actions are equally likely
      self.directions = np.full((level.height,level.width), Direction.All)
    else:
      self.directions = directions

    # no directions are possible in the terminal state
    self.directions[level.end[1],level.end[0]] = 0

    # set the seed used to choose random actions for a stochastic policy
    np.random.seed(seed=seed)

  def set_policy(self,directions):
    ''' set the policy (i.e. the action to take in each state) '''
    self.directions = directions

  def get_policy(self):
    return self.directions

  def get_directions(self,values = None):
    if values is not None:
      self.directions = self.calculate_greedy_directions(values)
    return self.directions

  def update_policy(self,values):
    ''' act greedily wrt to the supplied state values to get a new set of actions
      - if the new greedy policy specifies more than one action for a state select
        the action that was in previous policy
    '''
    greedy_directions = self.calculate_greedy_directions(values)

    for row in range(self.directions.shape[0]):
      for col in range(self.directions.shape[1]):
        # if a single direction is specified the value will be a power of 2
        n = greedy_directions[row,col]
        power_of_two = (n & (n-1) == 0) and n != 0
        if not power_of_two:
          # more than one direction so use direction from last policy
          greedy_directions[row,col] = self.directions[row,col]

    # update the policy
    self.directions = greedy_directions
    return self.directions

  def calculate_greedy_directions(self,values):
    ''' given a set of state values calculate the directions by acting greedily
        i.e. move in the direction of greatest state value
    '''
    # calculate the directions of all states except the exit
    directions = np.zeros((self.level.height,self.level.width),dtype=int)
    end = self.level.end
    for y in range(self.level.height):
      for x in range(self.level.width):
        if (x != end[0]) or (y != end[1]):
          if len(values.shape) == 2:
            directions[y,x] = self.calculate_cell_directions(x,y,values)
          else:
            directions[y,x] = self.get_greedy_direction(values[y][x])
    return directions


  def get_greedy_direction( self, arr ):
    ''' return the direction(s) with the maximum action value '''
    directions = 0
    best_value = -np.inf
    for action in range(len(Actions)):
      dir_value = Direction.from_action(action) 
      action_value = arr[action]
      if directions > 0 and math.isclose( action_value, best_value, rel_tol=1e-6):
        directions += dir_value
      elif action_value != 0 and action_value > best_value:
        directions = dir_value
        best_value = action_value 
    return directions 


  def calculate_cell_directions(self,x,y,values):
    ''' select the action with the highest value
        = argmax[ sum(p(s',r|s,a)[r + γV(s')]) ]
    '''
    actions = self.level.get_available_actions(x,y)

    directions = 0
    dir_value = 0
    best_value = -np.inf
    for action in actions:
      # get the possible probabilities, next_states and rewards for this action
      action_probabilities = self.level.get_action_probabilities( x, y, action )

      action_value = 0
      for probability,next_state,reward in action_probabilities:
        # convert the x,y position into row,col
        action_value += probability * (reward + values[next_state[1],next_state[0]])

      dir_value = Direction.from_action(action)

      # if a best action has already been selected and the new action has a value
      # very close to this, then add this action to the set of greedy actions
      if directions > 0 and math.isclose( action_value, best_value, rel_tol=1e-6):
        directions += dir_value
      elif action_value > best_value:
        directions = dir_value
        best_value = action_value

    return int(directions)


  def get_state_directions(self,x,y):
    ''' return the direction bitfield for the specified state
      - this combines the directions allowed by the grid with those specified by the policy
    '''
    # get the list of all possible actions in this state
    cell_actions = self.level.get_available_actions(x,y)

    # convert the actions to a direction bitfield
    cell_directions = Direction.from_actions( cell_actions )

    # do a bitfield combination of the cell's allowed directions with the policy
    #  to get the available directions
    return (cell_directions & self.directions[y,x])


  def get_direction_list(self,x,y):
    ''' return a list of the allowed directions for the specified state
      - this combines the directions allowed by the grid with those specified by the policy
    '''
    return Direction.get_list( self.get_state_directions(x,y) )


  def get_actions(self,x,y):
    ''' return a list of the actions specified by the policy for the specified state
      - this takes the actions specified by the policy and removes any that are invalid
      (i.e. any that aren't possible in the environment)
    '''
    direction_value = self.get_state_directions(x,y)
    action_list = []
    if direction_value & Direction.North: action_list.append( Actions.North )
    if direction_value & Direction.South: action_list.append( Actions.South )
    if direction_value & Direction.East:  action_list.append( Actions.East )
    if direction_value & Direction.West:  action_list.append( Actions.West )
    return action_list


  def get_action(self,x,y):
    ''' return a single action for the specified state
        - if no action exists for this state then one will be chosen at random from the
        available directions
        - if more than one action exists then one will be chosen from these at random
    '''
    actions = self.get_actions(x,y)
    if len(actions) == 0:
      # choose a random action (stochastic policy with all actions possible)
      return self.level.action_space.sample()

    # choose one of the policies possible actions
    return np.random.choice(actions)


  def get_action_probabilities(self,x,y):
    ''' return a dictionary with the allowed actions for a state along with the
        probability of taking each of these actions
    '''
    # get the allowed actions in the state
    actions = self.get_actions(x,y)

    if len(actions) == 0:
      return {}
    else:
      equal_probability = 1 / len(actions)
      return { action:equal_probability for action in actions }