
import numpy as np
from typing import Union


from ipycanvas import hold_canvas
from .arrows import Arrows
from .direction import Direction

from .grid_base import GridBase


''' class to write information to a grid level '''
class GridInfo():
  
  def __init__(self, gridbase: GridBase, **kwargs: dict):
    self.grid = gridbase

  def get_cell_directions(self, x: int, y: int, direction: Direction = None) -> list:
    ''' return the list of available directions for the specified position in the grid 
        returns a list in the form: {'N':True,'E':False,'S':False,'W':True}
    '''
    
    grid = self.grid

    # no actions exist for the terminal state
    if (x == grid.end[0]) and (y == grid.end[1]):
      return {}
    
    # no actions exist off the grid
    for area in grid.base_areas: 
      # test if only the area defn has been supplied
      if type(area[0]).__name__ == 'int':
        ax,ay,aw,ah = grid.get_area_defn(area)
      else:
        ax,ay,aw,ah = grid.get_area_defn(area[0])      
      # if (x >= ax and x < (ax + aw)) and ((y >= ay and y < (ay + ah))):
      #   return {}
      if grid.in_area(x,y,ax,ay,aw,ah):
        return {}

    # test if the level contains a maze
    if grid.maze is not None:        
      cell = grid.maze.cell_at( x, y )  
      
      # if a wall is present then that direction is not possible as an action
      actions = {k: not v for k, v in cell.walls.items()}      
    else:
      # initially start with all actions being possible
      actions = {'N':True,'E':True,'S':True,'W':True}
            
      # remove actions that would move off the edges of the grid
      if x == 0: del actions['W']
      if x == grid.width-1: del actions['E']
      if y == 0: del actions['N']
      if y == grid.height-1: del actions['S']   

    # remove actions that would move to an off-grid cell
    for area in grid.base_areas: 
      # test if only the area defn has been supplied
      if type(area[0]).__name__ == 'int':
        ax,ay,aw,ah = grid.get_area_defn(area)
      else:
        ax,ay,aw,ah = grid.get_area_defn(area[0])      

      if grid.in_area(x+1,y,ax,ay,aw,ah): del actions['E']
      if grid.in_area(x-1,y,ax,ay,aw,ah): del actions['W']
      if grid.in_area(x,y-1,ax,ay,aw,ah): del actions['N']
      if grid.in_area(x,y+1,ax,ay,aw,ah): del actions['S']
    

    if direction is not None:
      # set any allowed actions to false if they dont match the supplied action
      dir_value = direction
      for dir,v in actions.items():        
        if v == True:
          if (dir == 'N') and not (dir_value & Direction.North): actions['N'] = False
          if (dir == 'S') and not (dir_value & Direction.South): actions['S'] = False
          if (dir == 'E') and not (dir_value & Direction.East):  actions['E'] = False
          if (dir == 'W') and not (dir_value & Direction.West):  actions['W'] = False                                    
      
    return actions


  def get_directions( self, x: int = None, y: int = None ) -> Union[Direction,np.ndarray]:
    ''' return the bitfield value representing the possible directions for the specified grid cell '''
    if (x is None) or (y is None):
      return self.get_direction_array()
    else:
      return self.get_direction_value(x,y)


  def get_direction_value( self, x: int, y: int ) -> Direction:
    ''' return the bitfield value representing the possible directions for the specified grid cell '''
    return Direction.get_value( self.get_cell_directions( x, y ) )   


  def get_direction_array(self) -> np.ndarray:
    ''' return a numpy array containing the direction value for all grid cells '''
    height = self.grid.height
    width = self.grid.width
    direction_arr = np.zeros((height,width)).astype(int)
    for y in range(height):
      for x in range(width):
        direction_arr[y][x] = self.get_direction_value(x,y) 
    return direction_arr       