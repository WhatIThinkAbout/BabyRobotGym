
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


    
  # arrow_color = '#00008b'    # color of any information arrows

  # text_bg_color = 'rgba(40,40,40,0.7)' # text background shading
  # text_fg_color = '#fff'               # text foreground color


  # def __init__(self, parent, canvas, **kwargs):

  #   self.grid = parent
  #   self.canvas = canvas
  #   self.set_properties(kwargs)

  #   # arrow draw class
  #   self.arrows = Arrows( parent.cell_pixels, parent.padding,length=24,width=7,height=11)     


  # def set_properties(self,props):
  #   ''' setup the grid properties '''    

  #   if props is not None:
  #     colors = props.get('colors',None)
  #     if colors is not None:
          
  #       self.arrow_color = colors.get('arrows', self.arrow_color)    
  #       self.text_fg_color = colors.get('text_fg', self.text_fg_color)  
  #       self.text_bg_color = colors.get('text_bg', self.text_bg_color)  


  # '''
  #     Draw Functions
  # '''        

  # def draw_compass(self):      
  #   ''' draw the compass '''

  #   canvas = self.canvas
  #   if self.add_compass: 
  #     arrows = Arrows(64,2,length=15,width=5,height=11)
  #     arrows.draw(canvas,
  #                 self.width_pixels + 27, 14,
  #                 [Direction.North,Direction.West,Direction.South,Direction.East],
  #                 center_width = 28 )

  #     canvas.font = 'bold 20px sans-serif'
  #     canvas.fill_text(str("W"), self.width_pixels + 13, 52)    
  #     canvas.fill_text(str("N"), self.width_pixels + 49, 18)     
  #     canvas.fill_text(str("E"), self.width_pixels + 82, 52)     
  #     canvas.fill_text(str("S"), self.width_pixels + 51, 85)         


  # '''
  #     Direction Functions
  # '''
          
  # def draw_directions( self, x, y, directions ):   
  #   ''' draw an arrow in each direction from the supplied list ''' 
    
  #   canvas = self.canvas
  #   color = self.arrow_color
    
  #   with hold_canvas(canvas):       
  #     px,py = self.grid_to_pixels( [x,y], self.padding, self.padding )    
  #     canvas.clear_rect(px,py,self.cell_pixels,self.cell_pixels) 
  #     self.arrows.draw(canvas,px,py,directions,color)   


  # def draw_direction_array(self, directions: np.array):
  #   ''' draw arrows in each direction in the supplied numpy array '''
  #   canvas = self.canvas
    
  #   with hold_canvas(canvas):    
  #     for y in range(directions.shape[0]):
  #       for x in range(directions.shape[1]):
  #         self.draw_directions( x, y, directions[y,x])    


  # '''
  #     Text Functions
  # '''

  # def show_cell_text( self, row, col, value, color = '#002', back_color = None ):
  #   ''' display the given value in the specified cell '''                     
    
  #   canvas = self.canvas

  #   x,y = self.grid_to_pixels( [col,row], self.padding, self.padding )    
  #   cx,cy = self.get_center(x,y) # calculate the center of this cell
    
  #   with hold_canvas(canvas):                
  #     canvas.clear_rect(cx-18,cy-18,36,36) 

  #     if back_color is not None:
  #       canvas.fill_style = back_color
  #       canvas.fill_rect(cx-18,cy-10,36,20)      

  #     canvas.fill_style = color
  #     canvas.text_align = 'center'
  #     canvas.font = 'bold 12px sans-serif'
  #     canvas.fill_text(f"{value}", cx, cy+4)  


  # def show_cell_direction_text(self,directions):   
  #   ''' add a text string to each cell showing the directions '''              
  #   for row in range(directions.shape[0]):
  #     for col in range(directions.shape[1]):
  #       # dont show directions on the exit
  #       if col != self.end[0] or row != self.end[1]:                  
  #         dir_list = Direction.get_direction_list(directions[row][col])
  #         dir_string = ""
  #         for direction in dir_list:          
  #           if direction == Direction.North: dir_string += "N"      
  #           if direction == Direction.South: dir_string += "S"                  
  #           if direction == Direction.East:  dir_string += "E"                
  #           if direction == Direction.West:  dir_string += "W"     

  #         self.show_cell_text( row, col, dir_string, self.text_fg_color, self.text_bg_color )                       