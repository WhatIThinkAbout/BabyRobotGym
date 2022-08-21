
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

  x_offset = 0
  y_offset = 0  


  def __init__( self, level, **kwargs ):                      
      super().__init__( level, **kwargs )

      # the number of draw steps since the last reset
      self.move_step = 0

      # set to use the robot level of the multicanvas
      self.canvas = self.grid.canvases[Level.Robot] 

      # get any robot specific parameters
      robot_params = kwargs.get('robot',{})   

      # the number of steps before a sprite change
      self.sprite_change = robot_params.get('sprite_change',2)

      # the offset of the grid display
      offset = kwargs.get('offset',[0,0])  
      self.x_offset = offset[0]
      self.y_offset = offset[1]

      # test that baby robot should be shown
      self.show_robot = robot_params.get('show',True)

      # get robot speed parameters      
      self.sleep = robot_params.get('sleep',0.07)    
      self.canvas_sleep = robot_params.get('canvas_sleep',40)                    

      # the initial robot sprite (4 = center view)
      self.sprite_index = robot_params.get('initial_sprite',4)     
      self.load_sprites()


  def get_number_of_sprites(self):
      ''' return the number of sprites on the sprite sheet '''
      num_sprites = len(self.canvas_sprites)
      return num_sprites    


  def load_single_sprint(self):
      ''' load the defined sprite index - default is center robot '''
      image_path = os.path.join(self.level.working_directory,f'images/baby_robot_{self.sprite_index}.png')        
      self.sprite = Image.from_file(image_path)         


  def add_sprite(self,index):
      ''' add an image sprite with the specified index from an individual image 
          to the set of sprites to use for robot drawing
      '''
      # currently using individual sprite images rather than sprite sheet to fix Colab
      image_path = os.path.join(self.level.working_directory, f'images/baby_robot_{index}.png')
      sprites = Image.from_file(image_path)
      # put all sprites onto their own canvas
      canvas = Canvas(width=self.robot_size, height=self.robot_size)
      canvas.draw_image(sprites, 0, 0)
      self.canvas_sprites.append(canvas)      


  def load_sprites(self):
      ''' load the sprites used to draw baby robot
          - on Colab it seems to be limited to a single image and not on a canvas
      '''
      self.canvas_sprites = []
      if self.level.drawmode == 'colab':
        self.load_single_sprint()
      else:
        # load all sprites
        for row in range(5):
          for col in range(2):           
            index = (row*2) + col
            self.add_sprite(index)
        self.add_sprite(index+1)          


  def update_sprite(self):
      ' randomly change to the next sprite '    

      if self.get_number_of_sprites() > 1:
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

      x = self.x + self.x_offset
      y = self.y + self.y_offset

      if self.level.drawmode == 'colab':  
        self.canvas.clear_rect(x-10, y-10, self.robot_size+10, self.robot_size+10)                      
        self.canvas.draw_image(self.sprite, x, y ) 
      
      elif self.sprite_index < self.get_number_of_sprites():
        with hold_canvas(self.canvas):
          self.canvas.clear_rect(x, y, self.robot_size)                       
          self.canvas.draw_image(self.canvas_sprites[index], x, y )                            
      

  def draw(self):    
      ' add the current sprite at the current position '  
      if self.show_robot:   
        self.draw_sprite(self.sprite_index)
        self.update_sprite()      


  def move_direction(self,direction):        
      ' move from one square to the next in the specified direction '
      
      # test if a move is actually specified
      if self.test_for_valid_move(direction):          
          move_method_name = f"move_{direction.name}"        

          if self.level.drawmode == 'colab':
            self.move_direction_colab( move_method_name )
          else:
            for _ in range(self.robot_size//self.step):
              getattr(self,move_method_name)()  
              self.draw()  
              sleep(self.sleep) # pause between each move step        
              self.move_step += 1                 
               
          self.move_count += 1     


  def move_direction_colab( self, move_method_name ):        
      ''' move from one square to the next in the specified direction 
          - special drawing method to overcome problems in Colab
      '''                                      
      with hold_canvas(self.canvas):         
        for _ in range(self.robot_size//self.step):
            getattr(self,move_method_name)()  
            self.canvas.clear_rect(self.x-10, self.y-10, self.robot_size+10, self.robot_size+10)             
            self.canvas.draw_image(self.sprite, self.x, self.y )                     
            self.canvas.sleep(self.canvas_sleep)  
            sleep(self.sleep) # pause between each move step  
            self.move_step += 1


  def reset(self):
      ' clear the robot layer '
      self.move_step = 0
      self.canvas.clear()
      self.set_cell_position(self.initial_position) 
      self.draw()


  def partial_move(self,direction,sprite_index=None):        
      ' move from one square to the next in the specified direction '
              
      if direction is not None:
        if self.test_for_valid_move(direction):
          move_method_name = f"move_{direction.name}"        
          getattr(self,move_method_name)()  

          if sprite_index is not None:
            self.sprite_index = sprite_index 
          self.draw()                
          self.move_count += 1 

          # a move took place
          return True

      # no move occurred
      return False 