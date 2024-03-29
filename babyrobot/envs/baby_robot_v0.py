# Copyright (c) Steve Roberts
# Distributed under the terms of the Modified BSD License.


import random
import numpy as np
from gymnasium.spaces import Discrete, MultiDiscrete
from .baby_robot_interface import BabyRobotInterface


class BabyRobot_v0( BabyRobotInterface ):
    ''' Baby Robot Gym Environment '''

    metadata = {'render_modes': ['human'], 'render_fps': 4}

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # test if the 'step' function should use the new, 2 boolean, return format
        self.apply_api_compatibility = kwargs.get('apply_api_compatibility',False)

        self.max_episode_steps = kwargs.get('max_steps', None)

        # by default use a dynamic action space
        if kwargs.get('action_space','dynamic') == 'dynamic':
          self.action_space = self.dynamic_action_space
        else:
          # use discrete action space
          # - required for Stable Baselines environment checker which can't yet
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
        ''' take the action and update the position

            - under the latest version of Gym a single 'done' value is no longer returned, instead 2 boolean values are used:
            (from the Gym documentation)

            terminated (bool): whether a `terminal state` (as defined under the MDP of the task) is reached.
                In this case further step() calls could return undefined results.
            truncated (bool): whether a truncation condition outside the scope of the MDP is satisfied.
                Typically a timelimit, but could also be used to indicate agent physically going out of bounds.
                Can be used to end the episode prematurely before a `terminal state` is reached.

        '''
        reward, target_reached = self.take_action(action)
        obs = np.array([self.x,self.y])

        # increment the number of steps taken since the last reset
        # - if this is greater than the maximum allowed for the episode set the 'truncated' flag
        self.steps += 1
        truncated = False if self.max_episode_steps is None else (self.steps > self.max_episode_steps)

        # set the 'terminated' flag if we've reached the exit or the episode is truncated
        # (previously this was called 'done')
        terminated = (self.x == self.end[0]) and (self.y == self.end[1])
        if truncated: terminated = True

        info = {'target_reached':target_reached}

        if self.apply_api_compatibility:
          # old style return format - uses a single boolean to indicate episode termination
          return obs, reward, terminated, info
        else:
          # new style return format - uses 2 booleans
          return obs, reward, terminated, truncated, info


    def render(self, mode='human', info=None ):
        ''' render as an HTML5 canvas '''
        # move baby robot to the current position
        self.robot.move(self.x,self.y)

        if self.render_mode is not None:
          # write the info to the grid side-panel
          self.level.show_info(info)
          return self.level.draw()


    def reset(self, seed=None, return_info=False, options=None):
        ''' reset Baby Robot's position in the grid '''
        super().reset(seed=seed)
        if seed is not None:
           random.seed(seed)

        # the number of steps taken since the last reset
        self.steps = 0

        self.robot.set_cell_position(self.initial_pos)
        if self.render_mode is not None:
          self.robot.reset()
        self.x = self.initial_pos[0]
        self.y = self.initial_pos[1]
        self.set_available_actions()
        info = {}
        return np.array([self.x,self.y]),info