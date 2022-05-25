
import os
from enum import IntEnum
from .maze import Maze


class Puddle(IntEnum):
    Dry, Small, Large = range(3)   


class GridBase():
 
  maze = None                # instance of maze if defined  
  puddles = None             # set of tiles where puddles exist
  
  debug_maze = False         # write the maze to a svg file  

  
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

    # setup any maze and walls
    self.add_maze = kwargs.get('add_maze',False)
    self.maze_seed = kwargs.get('maze_seed',0)
    self.make_maze()
    self.toggle_walls( kwargs.get('walls',[]) )    


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

    for (x, y), direction in walls:
        current_cell = self.maze.cell_at(x,y)
        if   direction == 'E': next_cell = self.maze.cell_at(x+1,y)
        elif direction == 'W': next_cell = self.maze.cell_at(x-1,y)
        elif direction == 'N': next_cell = self.maze.cell_at(x,y-1)
        elif direction == 'S': next_cell = self.maze.cell_at(x,y+1)
        
        # add a new wall if none already otherwise remove
        current_cell.toggle_wall(next_cell, direction)       


  '''
      Puddles
  '''        

  def get_puddle_size( self, x, y ):
    ''' get the size of the puddle at the supplied location '''
    if self.puddles is not None:
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
     

  def get_reward( self, x, y ):
    ''' return the reward obtained for moving to the specified state 

        The amount of reward is a function of the puddle size:
        - no puddle = -1
        - small puddle = -2
        - large puddle = -4

        This represents the amount of time required to move through the puddle
    '''
    puddle_size = self.get_puddle_size( x, y )
    if   puddle_size == Puddle.Large: return self.large_puddle_reward
    elif puddle_size == Puddle.Small: return self.small_puddle_reward    
    return -1    