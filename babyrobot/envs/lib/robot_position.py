from .direction import Direction


import logging
logging.basicConfig(level=logging.DEBUG, format='(%(threadName)-9s) %(message)s',)


''' control robot positioning and drawing '''
class RobotPosition():
        
    move_count = 0   
    maze = None
    

    def __init__( self, level, **kwargs ):                
                
      self.level = level.grid_base
      self.grid  = level.draw_grid
      
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
              
      if self.maze is None:
          self.x_size = self.grid.width_pixels
          self.y_size = self.grid.height_pixels
      else:
          x,y = self.maze.dimensions()
          self.x_size = x * self.robot_size
          self.y_size = y * self.robot_size                                   

      # baby robot's initial position     
      self.initial_position = kwargs.get('initial_pos',self.level.start)
      self.set_cell_position(self.initial_position)        


    def get_cell_position(self):
      ''' get the current position in grid coords '''
      return self.x//self.robot_size, self.y//self.robot_size


    def set_cell_position(self, *args):
      ''' set the robot position in grid coords '''      
      # convert from grid position to pixels
      if len(args) == 1:    
        self.x,self.y = self.grid.grid_to_pixels(args[0])
        self.x_cell = args[0][0]
        self.y_cell = args[0][1]
      elif len(args) == 2: 
        self.x,self.y = self.grid.grid_to_pixels([args[0],args[1]])     
        self.x_cell = args[0]
        self.y_cell = args[1]        
                          
                
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


    def test_for_valid_move( self, direction ):
        ''' test if a move can actually be made in the specified direction '''
                
        if direction == Direction.Stay:
          return False

        cell = None
        if self.maze is not None:
            x, y = self.get_cell_position()
            cell = self.maze.cell_at( x, y )            
            if direction == Direction.North and cell.walls['N']: return False
            if direction == Direction.South and cell.walls['S']: return False
            if direction == Direction.East and cell.walls['E']: return False
            if direction == Direction.West and cell.walls['W']: return False        

        return True                        
        
        
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