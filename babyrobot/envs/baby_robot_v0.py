# Copyright (c) Steve Roberts
# Distributed under the terms of the Modified BSD License.


import gym
import numpy as np
from gym.spaces import Discrete, MultiDiscrete
from .baby_robot_interface import BabyRobotInterface


class BabyRobot_v0( BabyRobotInterface ):
    ''' Baby Robot Gym Environment '''
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs) 

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

