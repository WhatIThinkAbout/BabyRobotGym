import numpy as np
import os 
from typing import Union

from .direction import Direction
from .grid_base import GridBase
from .grid_info import GridInfo
from .draw_grid import DrawGrid
from .draw_info import DrawInfo



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
    self.draw_grid = DrawGrid( self.grid_base, **kwargs )    
    self.draw_info = DrawInfo( self.draw_grid, self.grid_info, **kwargs )


  '''
      Query Functions
  '''    

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


  def get_next_state( self, x, y, direction ):
    ''' return the next state and reward for moving 
        - (x,y) = current state
        - direction = direction moved from current state
    '''    
    
    assert direction >= Direction.Stay and direction <= Direction.West    
        
    # check that some actions are possible in this state
    possible_actions = self.grid_info.get_cell_directions(x,y,direction)
    if not possible_actions: 
      # stay in same position, reward = -1 for trying to move
      # - target only reached if choosing to stay in same state
      return [x,y],-1,(direction==Direction.Stay) 

    # a deterministic policy should only have one possible action
    chosen_action = [key for (key, value) in possible_actions.items() if value]
    if len(chosen_action) != 1:
      # stay in same position, reward = -1 for trying to move
      return [x,y],-1,False

    # get the list of all other possible states
    all_actions = self.grid_info.get_cell_directions(x,y)     
    all_actions.pop(chosen_action[0], None)
    other_states = [key for (key, value) in all_actions.items() if value]

    # get the probability of moving to the intended target
    transition_probability = self.grid_base.get_transition_probability( x, y )
 
    # if the probability is less than the transition probability then move to the target        
    # of if the target state is the only allowed state
    target_state_reached = True
    if (np.random.random() < transition_probability) or (len(other_states) == 0):
      direction = chosen_action[0]
    else:
      # choose one of the other possible states
      direction = np.random.choice(other_states)

      # set the flag to indicate the target state wasn't reached
      target_state_reached = False

    # calculate the postion of the next state
    next_pos = self.get_next_state_position( x, y, direction )   

    # get the reward for taking this action
    reward = self.grid_base.get_reward( next_pos[0], next_pos[1] )

    # for equal probability of taking an action its just the mean of all actions
    return next_pos, reward, target_state_reached  


  def get_next_state_position( self, x, y, direction ):
    ''' given the current state position and direction calculate the postion of the next state '''
    next_pos = []    
    if direction == 'N': next_pos = [x,y-1]
    if direction == 'S': next_pos = [x,y+1]
    if direction == 'E': next_pos = [x+1,y]
    if direction == 'W': next_pos = [x-1,y] 
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
        