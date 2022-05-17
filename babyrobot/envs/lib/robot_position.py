from time import sleep
import random
import os

from ipycanvas import Canvas, hold_canvas
from ipywidgets import Image

from .direction import Direction
from .draw_grid import Level

import logging
logging.basicConfig(level=logging.DEBUG, format='(%(threadName)-9s) %(message)s',)


''' control robot positioning and drawing '''
class RobotPosition():
    
    sprite_count = 0
    move_count = 0   
    canvas_sprites = []

    x_offset = 0
    y_offset = 0

    maze = None
    
    def __init__(self, level, x_size = 256, y_size = 256, initial_sprite = 4, start_pos = None,
                 x_offset = 0, y_offset = 0 ):
        
        if hasattr(level,'grid_base'):
          self.level = level.grid_base
          self.grid  = level.draw_grid
        else:
          # old format - retained for backwards compatibility
          self.level = level
          self.grid  = level

        self.canvas = self.grid.canvases[Level.Robot]

        # canvas to hold the baby-robot sprites
        # self.sprite_canvas = Canvas(width=132, height=328, sync_image_data=True)           
        # self.sprite_canvas.observe(self.get_array, 'image_data')           
        
        if hasattr(level, 'maze'):
          self.maze = level.maze
          
        # the position in grid cells
        self.x_cell = 0
        self.y_cell = 0
        
        # the position in pixels                        
        self.x = 0
        self.y = 0     
        
        self.step = 4
        self.robot_size = 64
        self.x_offset = x_offset
        self.y_offset = y_offset
        
        # the number of steps before a sprite change
        self.sprite_change = 2
        
        if self.maze is None:
            self.x_size = self.grid .width_pixels
            self.y_size = self.grid .height_pixels
        else:
            x,y = self.maze.dimensions()
            self.x_size = x * self.robot_size
            self.y_size = y * self.robot_size
                       
        self.sprite_index = initial_sprite        
        self.load_sprites()              
        
        if not start_pos:
          self.set_cell_position(self.level.start)
        else:
          self.set_cell_position(start_pos)
        
    def get_number_of_sprites(self):
      ''' return the number of sprites on the sprite sheet '''
      num_sprites = len(self.canvas_sprites)

      # # check that the sprite sheet has been created
      # if num_sprites == 0:
      #   self.get_array()
      #   num_sprites = len(self.canvas_sprites)

      return num_sprites
    
    def get_cell_position(self):
      ''' get the current position in grid coords '''
      return self.x//self.robot_size, self.y//self.robot_size
           
    def set_cell_position(self, *args):
      ''' set the robot position in grid coords '''      
            
      # clear the canvas of any previous sprite
      self.canvas.clear()

      # convert from grid position to pixels
      if len(args) == 1:    
        self.x,self.y = self.grid.grid_to_pixels(args[0])
        self.x_cell = args[0][0]
        self.y_cell = args[0][1]
      elif len(args) == 2: 
        self.x,self.y = self.grid.grid_to_pixels([args[0],args[1]])     
        self.x_cell = args[0]
        self.y_cell = args[1]        

      self.draw()
        
    # def get_array(self, *args, **kwargs):                
    #     ' callback to split the sprite sheet into individual sprites '        
        
    #     for row in range(5):
    #       for col in range(2):                                 

    #         index = row + col

    #         # put each sprite onto its own canvas
    #         image_path = os.path.join("../babyrobot",f'images/baby_robot_{index}.png')        
    #         sprites = Image.from_file(image_path)        

    #         canvas = Canvas(width=self.robot_size, height=self.robot_size)
    #         canvas.draw_image( sprites, 0, 0 )             
    #         self.canvas_sprites.append( canvas ) 

        
    #     # add a sprite to the display
    #     self.canvas.clear()
    #     self.draw()     
        
    def load_sprites(self):        
        ' load the sprite sheet and when loaded callback to split it into individual sprites '   
        # image_path = os.path.join(self.level.working_directory,'images/BabyRobot64_Sprites.png')        
        # sprites = Image.from_file(image_path)                  
        # self.sprite_canvas.draw_image( sprites, 0, 0 )   

        for row in range(5):
          for col in range(2):                                 

            index = row + col

            # put each sprite onto its own canvas
            image_path = os.path.join(self.level.working_directory,f'images/baby_robot_{index}.png')        
            sprites = Image.from_file(image_path)        

            canvas = Canvas(width=self.robot_size, height=self.robot_size)
            canvas.draw_image( sprites, 0, 0 )             
            self.canvas_sprites.append( canvas ) 
        
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
                
    def move(self,new_x,new_y):
        ' move from the current position to the specified position '                

        while (self.x_cell < (self.level.width-1)) and (self.x_cell < new_x):          
          self.move_direction(Direction.East)
          self.x_cell += 1

        while (self.x_cell > 0) and (self.x_cell > new_x):          
          self.move_direction(Direction.West)      
          self.x_cell -= 1

        while (self.y_cell < (self.level.height-1)) and (self.y_cell < new_y):          
          self.move_direction(Direction.South)        
          self.y_cell += 1

        while (self.y_cell > 0) and (self.y_cell > new_y):          
          self.move_direction(Direction.North)                     
          self.y_cell -= 1

        self.draw() 

          
    def move_direction(self,direction):        
        ' move from one square to the next in the specified direction '
        
        # test if a move is actually specified
        if direction == Direction.Stay:
          return

        # check that the image sprites have been loaded
        if self.get_number_of_sprites() > 0:
            cell = None
            if self.maze is not None:
                x, y = self.get_cell_position()
                cell = self.maze.cell_at( x, y )            
                if direction == Direction.North and cell.walls['N']: return
                if direction == Direction.South and cell.walls['S']: return
                if direction == Direction.East and cell.walls['E']: return
                if direction == Direction.West and cell.walls['W']: return
            
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
        
        
    def move_East(self):        
        if self.x < (self.x_size - self.robot_size):
            self.x += self.step
            
    def move_West(self):
        if self.x > 0: 
            self.x -= self.step            
            
    def move_North(self):
        if self.y > 0:           
            self.y -= self.step
            
    def move_South(self):
        if self.y < (self.y_size - self.robot_size):
            self.y += self.step