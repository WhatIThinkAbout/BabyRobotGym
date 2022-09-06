# Copyright (c) Steve Roberts
# Distributed under the terms of the Modified BSD License.

import gym

from .lib.grid_level import GridLevel
from .lib.robot_draw import RobotDraw
from .lib.dynamic_space import Dynamic

from .lib.direction import Direction
from .lib.actions import Actions


class BabyRobotInterface(gym.Env):
    ''' Baby Robot Gym Environment Base Class '''

    def __init__(self, **kwargs):
        super().__init__()

        # initially no actions are available      
        self.dynamic_action_space = Dynamic()          

        # dimensions of the grid
        self.width = kwargs.get('width',3)
        self.height = kwargs.get('height',3)      
      
        # define the maximum x and y values
        self.max_x = self.width - 1
        self.max_y = self.height - 1

        # the start and end positions in the grid
        # - by default these are the top-left and bottom-right respectively
        self.start = kwargs.get('start',[0,0])       
        self.end = kwargs.get('end',[self.max_x,self.max_y])        
        
        # Baby Robot's initial position
        # - by default this is the grid start 
        self.initial_pos = kwargs.get('initial_pos',self.start)  

        # Baby Robot's position in the grid
        self.x = self.initial_pos[0]
        self.y = self.initial_pos[1]         

        # graphical creation of the level
        self.level = GridLevel( **kwargs )  
        
        # add baby robot
        self.robot = RobotDraw(self.level,**kwargs)   
        self.robot.draw()          

        # set the initial position and available actions
        self.reset()


    #
    # Helper Methods
    #         

    def take_action(self, action):
        ''' apply the supplied action 

            returns:
            - the reward obtained for taking the action
            - a flag to indicate if the target state was reached - if it wasn't this indicates
              that a slip has occurred
        '''         

        # convert the action into a direction bitfield 
        direction = Direction.from_action(action)  
          
        # calculate the postion of the next state and the reward for moving there
        next_pos,reward,target_reached = self.level.get_next_state( self.x, self.y, direction )  

        # store the new position
        self.x = next_pos[0]
        self.y = next_pos[1]
    
        # update the available actions for the new position        
        self.set_available_actions()      
        return reward, target_reached  


    def get_available_actions( self, x = None, y = None ):
        ''' test which actions are allowed at the specified grid state '''

        # if no coordinate supplied use the current position
        if x is None: x = self.x
        if y is None: y = self.y

        # get the available actions from the grid level
        direction_value = self.level.get_directions(x,y) 

        # convert the grid directions into environment actions
        return Direction.get_action_list(direction_value)  

              
    def set_available_actions( self ):
        ' set the list of available actions into the action space '
        action_list = self.get_available_actions()   
        self.dynamic_action_space.set_actions( action_list )      


    def show_available_actions( self ):
        ''' return a string of avaiable actions for current state '''
        available_actions = str(self.dynamic_action_space.get_available_actions()).replace("'","")
        return f"({self.x},{self.y}) {available_actions:36}"


    def get_transition_probability( self, x = None, y = None ):
        ''' get the probability of moving to the intended target when in the specified cell '''
        # if no coordinate supplied use the current position
        if not x: x = self.x
        if not y: y = self.y      
        return self.level.grid_base.get_transition_probability( x, y )


    def get_reward( self, x, y, direction = None ):
        ''' get the reward for moving to cell (x,y) or, if a direction is specified, 
            the reward for moving from (x,y) to the cell in the specified direction
        '''
        return self.level.get_reward(x,y,direction)

    #
    # Information Methods
    #    

    def show_info(self,info):
        ''' display the supplied information on the grid level '''
        self.level.show_info( info )

    def clear_info(self,all_info=False):
        ''' clear any current information of the grid level '''
        self.level.clear(all_info)

    def save(self, filename):
        ''' save the level as an image to the specified file '''
        self.level.save(filename)                   