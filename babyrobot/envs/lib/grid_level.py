import numpy as np
import os
from typing import Union

from .direction import Direction
from .grid_base import GridBase
from .grid_info import GridInfo
from .actions import Actions


class GridLevel():
  '''
    Class to manage a grid level.
    This performs all drawing and querying of the level
    (to see which moves are possible within a given grid cell)
  '''

  def __init__( self, **kwargs: dict ):

    # get the directory where this file is running
    dir_path = os.path.dirname(os.path.realpath(__file__))

    self.grid_base = GridBase( dir_path, **kwargs )
    self.grid_info = GridInfo( self.grid_base, **kwargs )

  '''
      Query Functions
  '''

  def is_grid_state( self, x, y ):
    ''' test if the specified state is a valid state
        i.e. it lies on the grid level
    '''
    if (x < 0) or (x >= self.grid_base.width) or \
       (y < 0) or (y >= self.grid_base.height) or \
       self.grid_base.test_for_base_area( x, y ):
      return False

    # the terminal state doesn't count as a valid grid state
    if (x == self.grid_base.end[0]) and (y== self.grid_base.end[1]):
      return False

    return True



  def get_directions( self, x: int = None, y: int = None ) -> Union[Direction,np.ndarray]:
    ''' return the possible directions for the specified grid cell
        - if a grid cell is not specified then return an array of possible
        directions for all grid cells
    '''
    return self.grid_info.get_directions( x, y )


  def get_rewards( self, x: int = None, y: int = None ) -> Union[Direction,np.ndarray]:
    ''' return the reward for the specified grid cell
        - if a grid cell is not specified then return an array of rewards for all grid cells
    '''
    return self.grid_base.get_reward( x, y )


  def get_action_probabilities( self, x, y, action: Actions ):

    direction = Direction.from_action( action )
    assert direction >= Direction.Stay and direction <= Direction.West

    # check that some actions are possible in this state
    possible_directions = self.grid_info.get_cell_directions(x,y,direction)

    if not possible_directions or direction==Direction.Stay:
      # stay in same position, reward is the same as if trying to move into this state
      # - target only reached if choosing to stay in same state
      reward = self.grid_base.get_reward( x, y )
      return [[1.0,[x,y],reward]]

    # get the probability of moving to the intended target
    transition_probability, barrier = self.grid_base.get_transition_probability( x, y, direction )

    action_list = []

    # find the details of where we end up if action succeeds
    if transition_probability > 0.0:
      next_pos = self.get_next_state_position( x, y, direction )
      reward = self.grid_base.get_reward( next_pos[0], next_pos[1] )
      action_list.append([transition_probability,next_pos,reward])

    # if the transition probability is 1 then definitely reach target
    if transition_probability == 1.0:
      return action_list

    #
    # transition_probability < 1.0
    # - more than one next_state for current action
    #

    # get the list of all other possible states
    all_actions = self.grid_info.get_cell_directions(x,y)
    all_actions.pop(direction.get_direction_char(), None)
    other_directions = [key for (key, value) in all_actions.items() if value]

    # if there are no other states to go to, stay in the current state
    if len(other_directions) == 0:
      reward = self.grid_base.get_reward( x, y )
      action_list.append([(1.0 - transition_probability),[x,y],reward])
      return action_list

    if barrier:
      # an extra penalty of -1 is given for running into a wall
      reward = -1

      # if a barrier existed in the target direction then Baby Robot will end up taking
      # the opposite action if this exists (i.e. he bounces off the barrier)
      # - this happens with probability (1-transition_probability)
      direction = Direction.get_opposite(direction).get_direction_char()

      # check that the opposite direction is possible
      if direction not in other_directions:
        # opposite direction not possible - stay in current state
        reward += self.grid_base.get_reward( x, y )
        action_list.append([(1.0 - transition_probability),next_pos,reward])
        return action_list

      next_pos = self.get_next_state_position( x, y, direction )
      reward += self.grid_base.get_reward( next_pos[0], next_pos[1] )
      action_list.append([(1.0 - transition_probability),next_pos,reward])
      return action_list

    # divide the remaining probability over the other possible directions
    probability = (1.0-transition_probability)/len(other_directions)
    for other_direction in other_directions:
      # calculate the postion of the next state
      next_pos = self.get_next_state_position( x, y, other_direction )
      reward = self.grid_base.get_reward( next_pos[0], next_pos[1] )
      action_list.append([probability,next_pos,reward])

    return action_list


  def get_next_state( self, x, y, direction ):
    ''' return the next state and reward for moving
        - (x,y) = current state
        - direction = direction moved from current state
    '''

    assert direction >= Direction.Stay and direction <= Direction.West

    # check that some actions are possible in this state
    possible_actions = self.grid_info.get_cell_directions(x,y,direction)
    if not possible_actions or direction==Direction.Stay:
      # stay in same position, reward is the same as if trying to move into this state
      # - target only reached if choosing to stay in same state
      reward = self.grid_base.get_reward( x, y )
      return [x,y],reward,(direction==Direction.Stay)

    # a deterministic policy should only have one possible action
    chosen_action = [key for (key, value) in possible_actions.items() if value]
    if len(chosen_action) != 1:
      # stay in same position, reward is the same as if trying to move into this state
      reward = self.grid_base.get_reward( x, y )
      return [x,y],reward,False

    # get the list of all other possible states
    all_actions = self.grid_info.get_cell_directions(x,y)
    all_actions.pop(chosen_action[0], None)
    other_states = [key for (key, value) in all_actions.items() if value]

    # get the probability of moving to the intended target
    transition_probability, barrier = self.grid_base.get_transition_probability( x, y, chosen_action[0] )

    # if the probability is less than the transition probability then move to the target
    # of if the target state is the only allowed state
    target_state_reached = True
    # if (np.random.random() < transition_probability) or (len(other_states) == 0):
    if (np.random.random() < transition_probability):
      direction = chosen_action[0]
    else:
      # the action did not succeed

      # set the flag to indicate the target state wasn't reached
      target_state_reached = False

      # if there are no other states to go to, stay in the current state
      if len(other_states) == 0:
        direction = Direction.Stay
      else:
        if barrier:
          # if a barrier existed in the target direction then Baby Robot will end up taking
          # the opposite action if this exists (i.e. he bounces off the barrier)
          direction = Direction.get_opposite(chosen_action[0])

          # check that the opposite direction is possible
          if direction not in other_states:
            return [x,y],-1,False

        else:
          # choose one of the other possible states
          direction = np.random.choice(other_states)

    # calculate the postion of the next state
    next_pos = self.get_next_state_position( x, y, direction )

    # get the reward for taking this action
    reward = self.grid_base.get_reward( next_pos[0], next_pos[1] )

    # if we bounced off a barrier incur an extra time penalty of -1
    if barrier:
      reward += -1

    # for equal probability of taking an action its just the mean of all actions
    return next_pos, reward, target_state_reached


  def get_next_state_position( self, x, y, direction ):
    ''' given the current state position and direction calculate the postion of the next state '''
    next_pos = []
    if direction==Direction.North or direction == 'N': next_pos = [x,y-1]
    elif direction==Direction.South or direction == 'S': next_pos = [x,y+1]
    elif direction==Direction.East or direction == 'E': next_pos = [x+1,y]
    elif direction==Direction.West or direction == 'W': next_pos = [x-1,y]
    else: next_pos = [x,y] # stay in the current state
    return next_pos


  def get_reward( self, x, y, direction = None ):
    ''' get the reward for moving to the cell at (x,y) or, if a direction is specified,
        the reward for moving from the cell at (x,y) to the cell in the specified direction
    '''
    if direction:

      # if the direction is given as an enum convert to char
      if type(direction) != str:
        direction = Direction.get_direction_char(direction)

      # calculate the postion of the next state
      nx,ny = self.get_next_state_position( x, y, direction )
      return self.grid_base.get_reward(nx,ny),[nx,ny]

    # get the reward for taking this action
    return self.grid_base.get_reward(x,y)


  '''
      Graphical Functions
  '''

  def draw( self ):
    ''' render the grid canvases '''
    return self.draw_grid.canvases

  def clear( self, all_info=False ):
    ''' clear anything currently in the info panels '''
    self.draw_grid.clear(all_info)

  def show_info( self, info: dict ):
    ''' add the supplied information to the grid '''
    self.draw_info.draw( info )

  def save( self, filename ):
    ''' render the grid canvases '''
    canvases = self.get_canvases()
    # save and restore to complete any canvas drawing
    canvases[3].save()
    canvases[3].restore()
    return canvases.to_file(filename)

  def get_canvases(self):
    ''' get the grid levels multi-canvas '''
    return self.draw_grid.canvases

  def get_canvas_dimensions( self ):
    ''' get the total size of the grid canvas in pixels '''
    return [self.draw_grid.total_width, self.draw_grid.total_height]
