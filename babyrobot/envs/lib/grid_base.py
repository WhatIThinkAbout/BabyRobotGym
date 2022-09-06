
import os
from enum import IntEnum
from .maze import Maze
import numpy as np
from typing import Union


class Puddle(IntEnum):
    Dry, Small, Large = range(3)   


class GridBase():
 
  maze = None                # instance of maze if defined  
  puddles = None             # set of tiles where puddles exist
  base_areas = []            # any areas that exist on the base 
  grid_areas = []            # and areas that exist on the grid
  
  debug_maze = False         # write the maze to a svg file  

  grid_rewards = []          # the rewards calculated for the whole grid

  
  def __init__( self, working_directory: str = ".", **kwargs: dict ):
    
    self.working_directory = working_directory
        
    # test if a special drawing mode should be used
    # - currently required to run on Google Colab
    # - try to automatically detect if running in Colab using environ
    self.drawmode = kwargs.get('drawmode', 'colab' if 'COLAB_GPU' in os.environ else "" )

    self.width = kwargs.get('width',3)
    self.height = kwargs.get('height',3)    
    
    # the start and end positions in the grid
    # - by default these are the top-left and bottom-right respectively
    self.start = kwargs.get('start',[0,0])       
    self.end = kwargs.get('end',[self.width-1,self.height-1])    

    # setup any puddles    
    self.puddles = kwargs.get('puddles',None)     

    # setup up any properties defined for the puddles
    puddle_props = kwargs.get('puddle_props',{})
    self.large_puddle_reward = puddle_props.get('large_reward',-4)
    self.small_puddle_reward = puddle_props.get('small_reward',-2)
    self.large_puddle_probability = puddle_props.get('large_prob',0.4)
    self.small_puddle_probability = puddle_props.get('small_prob',0.6)    

    # setup any base-level areas    
    self.base_areas = kwargs.get('base_areas',[])     

    # setup any grid-level areas    
    self.grid_areas = kwargs.get('grid_areas',[])       

    # setup any maze and walls
    self.add_maze = kwargs.get('add_maze',False)
    self.maze_seed = kwargs.get('maze_seed',0)
    self.make_maze()
    self.toggle_walls( kwargs.get('walls',[]) )

    # calculate the rewards for each cell in the grid
    self.grid_rewards = self.get_reward()
    

  '''
      Maze and Walls
  '''

  def make_maze(self):
    if self.add_maze:
      if self.maze is None:
        self.maze = Maze(self.width, self.height, self.start[0], self.start[1], seed = self.maze_seed)
        self.maze.make_maze()        
      if self.debug_maze: 
        self.maze.write_svg(os.path.join(self.working_directory, "maze.svg"))


  def toggle_walls(self, walls):
    ''' add or remove the specified walls from the grid '''

    # if a maze isnt already defined begin with a maze with no walls
    if self.maze is None:
      self.maze = Maze(self.width, self.height, self.start[0], self.start[1], no_walls = True)
      self.add_maze = True # we now have a maze to add to the canvas

    for (loc), direction in walls:
      x = loc[0]
      y = loc[1]
      num_cells = loc[2] if len(loc) == 3 else 1

      for n in range(num_cells):

        if x >= self.width or y >= self.height:
          break         

        current_cell = self.maze.cell_at(x,y)
        if   direction == 'E': next_cell = self.maze.cell_at(x+1,y)
        elif direction == 'W': next_cell = self.maze.cell_at(x-1,y)
        elif direction == 'N': next_cell = self.maze.cell_at(x,y-1)
        elif direction == 'S': next_cell = self.maze.cell_at(x,y+1)
      
        # add a new wall if none already otherwise remove
        current_cell.toggle_wall(next_cell, direction)           

        # move to the next cell for wall repeated across multiple cells
        if direction == 'E' or direction == 'W': y += 1
        else: x += 1                  


  '''
      Puddles
  '''        

  def get_puddle_size( self, x, y ):
    ''' get the size of the puddle at the supplied location '''
    if self.puddles is not None:
      if isinstance(self.puddles[0],list):
        return Puddle(self.puddles[y][x])
      else:
        for (px,py),puddle_size in self.puddles:
          if x==px and y==py:         
            return Puddle(puddle_size) 

    return Puddle.Dry    


  def get_transition_probability( self, x, y ):
    ''' get the probability of moving to the target state when starting in the state at (x,y) '''
    puddle_size = self.get_puddle_size( x, y )         

    if puddle_size == Puddle.Large: return self.large_puddle_probability
    if puddle_size == Puddle.Small: return self.small_puddle_probability
    
    # if no puddle then guaranteed to reach target
    return 1.     


  def get_reward( self, x: int = None, y: int = None ) -> Union[int,np.ndarray]:
    ''' return the reward for the specified grid cell '''
    if (x is None) or (y is None):
      return self.get_reward_array()
    else:
      return self.get_reward_value(x,y)


  def get_reward_array(self) -> np.ndarray:
    ''' return a numpy array containing the reward value for all grid cells '''

    if len(self.grid_rewards) == 0:       
      height = self.height
      width = self.width
      reward_arr = np.zeros((height,width)).astype(int)
      for y in range(height):
        for x in range(width):
          reward_arr[y][x] = self.get_reward_value(x,y) 
      return reward_arr      

    # grid rewards already calculated
    return self.grid_rewards


  def test_for_base_area( self, x, y ):
    ''' test if the specified cell is in a base area '''
    for area in self.base_areas: 
      # test if only the area defn has been supplied
      if type(area[0]).__name__ == 'int':
        ax,ay,aw,ah = self.get_area_defn(area)
      else:
        ax,ay,aw,ah = self.get_area_defn(area[0])      
      return self.in_area(x,y,ax,ay,aw,ah)
        

  def get_reward_value( self, x, y ):
    ''' return the reward obtained for moving to the specified state 

        The amount of reward is a function of the puddle size:
        - no puddle = -1
        - small puddle = -2
        - large puddle = -4

        Actions taken in the terminal state have a reward of zero (although once the terminal 
        state is reached the episode terminates, so no actions will occur)
        - however, moving to the terminal state still requires some energy to be used, so
        the reward for taking an action that ends up in the terminal state is also given a 
        reward of -1.

        This represents the amount of time required to move through the puddle (and therefore
        the amount of energy used by BabyRobot)
    '''

    if len(self.grid_rewards) > 0: 
      # use the pre-calculated rewards
      # - note this holds the rewards as row,col so must swap x and y   
      return self.grid_rewards[y,x]

    puddle_size = self.get_puddle_size( x, y )
    if   puddle_size == Puddle.Large: return self.large_puddle_reward
    elif puddle_size == Puddle.Small: return self.small_puddle_reward  

    # no rewards exist off the grid
    if self.test_for_base_area(x,y):      
      return 0

    # if any grid areas exist these can set different rewards
    # - the most recently defined area is the one whose reward will be taken
    # for a cell
    cell_reward = -1
    for area in self.grid_areas:      
      if len(area) > 2:   
        try:     
          ax,ay,aw,ah = self.get_area_defn(area[0]) 
          if self.in_area( x,y,ax,ay,aw,ah ):
            cell_reward = area[2]        
        except:
          pass

    return cell_reward    

  '''
     Areas
  '''

  def get_area_defn( self, area):
    ''' extract the area properties from the supplied area tuple '''
    x,y,*args = area
    wd,ht = args if args else (1,1) # default to unit-square if no values specified
    return x,y,wd,ht


  def in_area(self,x,y,ax,ay,aw,ah):
    if (x >= ax and x < (ax + aw)) and ((y >= ay and y < (ay + ah))):
      return True
    return False    