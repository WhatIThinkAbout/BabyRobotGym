# Copyright (c) Steve Roberts
# Distributed under the terms of the Modified BSD License.

import math
import numpy as np
from babyrobot.envs import BabyRobotInterface
from babyrobot.envs.lib.direction import Direction
from babyrobot.envs.lib.actions import Actions

class Policy():

  def __init__(self, level: BabyRobotInterface, directions: np.array = None):
    self.level = level
    if directions is None:
      # if no directions are supplied create a policy where all actions are equally likely
      self.directions = np.full((level.height,level.width), Direction.All)
    else:
      self.directions = directions

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
          directions[y,x] = self.calculate_cell_directions(x,y,values)
    return directions


  def calculate_cell_directions(self,x,y,values):
    actions = self.level.get_available_actions(x,y)
    directions = 0
    dir_value = 0
    best_value = -np.inf
    for action in actions:
      # calculate the postion of the next state
      if action == Actions.North: value = values[y-1,x]; dir_value = Direction.North
      if action == Actions.South: value = values[y+1,x]; dir_value = Direction.South
      if action == Actions.East:  value = values[y,x+1]; dir_value = Direction.East
      if action == Actions.West:  value = values[y,x-1]; dir_value = Direction.West

      # if a best action has already been selected and the new action has a value
      # very close to this, then add this action to the set of greedy actions
      if directions > 0 and math.isclose( value, best_value, rel_tol=1e-6):
        directions += dir_value
      elif value > best_value:
        directions = dir_value
        best_value = value

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

    equal_probability = 1 / len(actions)
    return { action:equal_probability for action in actions }