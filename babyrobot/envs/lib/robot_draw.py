
from ipycanvas import Canvas, hold_canvas
from ipywidgets import Image
from time import sleep

import random
import os

from .robot_position import RobotPosition
from .draw_grid import Level


class RobotDraw( RobotPosition ):

  sprite_count = 0
  canvas_sprites = []

  def __init__( self, 
                level, 
                x_size = 256, 
                y_size = 256, 
                initial_sprite = 4, 
                start_pos = None,
                x_offset = 0, y_offset = 0 ):  

    super().__init__( level, x_size, y_size, start_pos, x_offset, y_offset )

    self.canvas = self.grid.canvases[Level.Robot] 
      
    # the number of steps before a sprite change
    self.sprite_change = 2     

    self.sprite_index = initial_sprite        
    self.load_sprites()     


  def get_number_of_sprites(self):
    ''' return the number of sprites on the sprite sheet '''
    num_sprites = len(self.canvas_sprites)
    return num_sprites   


  def show_cell_position(self, *args):
    ''' set the robot position in grid coords and draw at this position '''      
    self.set_cell_position( *args )    
    self.canvas.clear()   
    self.draw()    

               
  def load_sprites(self):
      ' load the sprite sheet and when loaded callback to split it into individual sprites '

      for row in range(5):
        for col in range(2):

          index = row + col

          # put each sprite onto its own canvas
          image_path = os.path.join(
              self.level.working_directory, f'images/baby_robot_{index}.png')
          sprites = Image.from_file(image_path)

          canvas = Canvas(width=self.robot_size, height=self.robot_size)
          canvas.draw_image(sprites, 0, 0)
          self.canvas_sprites.append(canvas)

      # add a sprite to the display
      self.canvas.clear()
      self.draw()


  def update_sprite(self):
      ' randomly change to the next sprite '        
      self.sprite_count += 1
      if self.sprite_count > self.sprite_change: 
          self.sprite_count = 0   
          self.sprite_index = self.sprite_index + random.randint(-1,+1)   
          if self.sprite_index < 0: 
              self.sprite_index = 0
          if self.sprite_index >= self.get_number_of_sprites():
              self.sprite_index = (self.get_number_of_sprites()-1)    
                            
  def draw_sprite(self,index):   
      ' remove the last sprite and add the new one at the current position '
      if self.sprite_index < self.get_number_of_sprites():
          with hold_canvas(self.canvas):
              x = self.x + self.x_offset
              y = self.y + self.y_offset
              self.canvas.clear_rect(x, y, self.robot_size)                       
              self.canvas.draw_image(self.canvas_sprites[index], x, y )                       
      
  def draw(self):    
      ' add the current sprite at the current position '     
      self.draw_sprite(self.sprite_index)
      self.update_sprite()    

          
  def move_direction(self,direction):        
      ' move from one square to the next in the specified direction '
      
      # test if a move is actually specified
      if self.test_for_valid_move(direction):
          
          move_method_name = f"move_{direction.name}"        
          for _ in range(self.robot_size//self.step):
              getattr(self,move_method_name)()  
              self.draw()  
              sleep(0.10) # pause between each move step        
              
          self.move_count += 1     


  def partial_move(self,direction,sprite_index=None):        
      ' move from one square to the next in the specified direction '
              
      if direction is not None:
        move_method_name = f"move_{direction.name}"        
        getattr(self,move_method_name)()  

      if sprite_index is not None:
        self.sprite_index = sprite_index 
      self.draw()  
          
      self.move_count += 1               
