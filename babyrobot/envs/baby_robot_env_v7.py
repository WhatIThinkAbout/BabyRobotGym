import gym
import numpy as np
from gym.spaces import Discrete, MultiDiscrete

from .lib.direction import Direction
from .lib.actions import Actions
from .lib.dynamic_space import Dynamic
from .lib.grid_level import GridLevel
from .lib.robot_draw import RobotDraw


class BabyRobotEnv_v7(gym.Env):
    
    def __init__(self, **kwargs):
        super().__init__()

        # dimensions of the grid
        self.width = kwargs.get('width',3)
        self.height = kwargs.get('height',3)      
      
        # define the maximum x and y values
        self.max_x = self.width - 1
        self.max_y = self.height - 1 

        # initially no actions are available      
        self.dynamic_action_space = Dynamic()   

        # by default use a dynamic action space 
        if kwargs.get('action_space','dynamic') == 'dynamic':
          self.action_space = self.dynamic_action_space              
        else:
          # use discrete action space 
          # - required for Stable Baselines environment checker which cant yet
          #   recognise dynamic spaces
          # - all actions are available in each state
          # - there are 5 possible actions: move N,E,S,W or stay in same state
          self.action_space = Discrete(5)        


        # the observation will be the coordinates of Baby Robot            
        self.observation_space = MultiDiscrete([self.width, self.height])                       

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


    def get_available_actions( self ):
        ''' test which actions are allowed at the specified grid state '''      

        # get the available actions from the grid level
        direction_value = self.level.get_directions(self.x,self.y) 

        # convert the grid directions into environment actions
        action_list = []       
        if direction_value & Direction.North: action_list.append( Actions.North )
        if direction_value & Direction.South: action_list.append( Actions.South )
        if direction_value & Direction.East:  action_list.append( Actions.East ) 
        if direction_value & Direction.West:  action_list.append( Actions.West )                
        return action_list     

              
    def set_available_actions( self ):
        ' set the list of available actions into the action space '
        action_list = self.get_available_actions()   
        self.dynamic_action_space.set_actions( action_list )      


    def show_available_actions( self ):
        ''' return a string of avaiable actions for current state '''
        available_actions = str(self.dynamic_action_space.get_available_actions()).replace("'","")
        return f"({self.x},{self.y}) {available_actions:36}"


    def show_info(self,info):
        ''' display the supplied information on the grid level '''
        self.level.show_info( info )


    def clear_info(self,all_info=False):
        ''' clear any current information of the grid level '''
        self.level.clear(all_info)         


    #
    # Gym Interface Methods
    #

    def step(self, action): 
        ''' take the action and update the position '''        
        reward, target_reached = self.take_action(action)      
        obs = np.array([self.x,self.y])      
            
        # set the 'done' flag if we've reached the exit
        done = (self.x == self.end[0]) and (self.y == self.end[1])
          
        info = {'target_reached':target_reached}
        return obs, reward, done, info 


    def render(self, mode='human', info=None ):                 
        ''' render as an HTML5 canvas '''
              
        # move baby robot to the current position
        self.robot.move(self.x,self.y) 

        # write the info to the grid side-panel      
        self.level.show_info(info) 
        return self.level.draw()  


    def reset(self):
        ''' reset Baby Robot's position in the grid '''
        self.robot.set_cell_position(self.initial_pos)      
        self.robot.reset()               
        self.x = self.initial_pos[0]
        self.y = self.initial_pos[1]        
        self.set_available_actions()
        return np.array([self.x,self.y])  

