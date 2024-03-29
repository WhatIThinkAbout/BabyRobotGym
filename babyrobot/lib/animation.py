# Copyright (c) Steve Roberts
# Distributed under the terms of the Modified BSD License.

import os
import numpy as np
import imageio.v2 as imageio

from ..envs import BabyRobotInterface
from ..envs.lib import Actions
from ..envs.lib import Direction
from . import Utils
from . import PolicyEvaluation
from . import Policy
from . import MonteCarloGPI


from ipywidgets import HBox, VBox

from time import sleep
import os
import time

import logging
logging.getLogger().setLevel(logging.ERROR)


class Animate():


  def __init__(self, env: BabyRobotInterface):

    self.env = env
    self.canvases = env.level.get_canvases()

    self.step = 0
    self.partial_step = 0
    self.max_partial_step = 0

    # the default time between each step when just displaying the episode
    self.kPlayInterval = 80

    # if set true an image will be written for each step of the animation
    self.create_images: False

    # the default time between each step when creating images from the episode
    self.kImageInterval = 300


  def set_parameters(self, **kwargs):
    '''
        set all the parameters using any supplied values,
        otherwise use the defaults
    '''
    # the maximum number of steps for which the episode should run
    self.max_steps = kwargs.get('max_steps',10)

    # the number of iterations between each displayed update or image write
    self.save_interval = kwargs.get('save_interval',1)

    # the precision to display the state values
    self.precision = kwargs.get('precision',1)

    # test if directions should be displayed
    self.show_directions = kwargs.get('show_directions',True)

    # test if state or action visits should be shown
    # - MC only
    self.show_visits = kwargs.get('show_visits',True)

    # can turn off all side-panel info
    self.show_info =  kwargs.get('show_info',True)

    # test if an image should be written at each step
    self.create_images = kwargs.get('create_images',False)

    # the folder to use when generating images during the run
    self.image_folder = kwargs.get('image_folder',"animate_images")

    self.play_interval = kwargs.get('interval',self.kPlayInterval)
    if self.create_images and self.play_interval < self.kImageInterval:
      # when images are being written need to go more slowly
      self.play_interval = self.kImageInterval


  def get_info_string( self, details ):
    '''
        basic function to display text information
    '''
    info = {}
    info['side_info'] = \
    [
      ((10,10),f"step: {details['step']}"),
      ((10,30),f"state: {details['state']}"),
      ((10,50),f"action: {details['action']}"),
      ((10,70),f"new state: {details['new_state']}"),
      ((10,90),f"direction: {details['direction']}"),
      ((10,110),f"reward: {details['reward']}"),
      ((10,130),f"done: {details['done']}"),
      ((10,170),f"total reward: {details['total_reward']}"),
    ]
    return info


  def write_file(self,delay=5):
    '''
        write the current environment to a file and wait for it to be created
    '''
    filename = f'{self.image_folder}/step_{self.partial_step}.png'

    # save the environment to a file
    self.canvases[3].save()
    self.canvases[3].restore()
    self.canvases.to_file(filename)

    # wait for the file to be created
    time_to_wait = 10
    time_counter = 0
    while not os.path.exists(filename):
        time.sleep(1)
        time_counter += 1
        if time_counter > time_to_wait:break
    time.sleep(delay)


  def clear_image_folder(self):
    '''
        Helper method to delete any images in the image folder
    '''
    Utils.clear_directory(self.image_folder)


  def create_movie( self, **kwargs ):
    '''
        create a gif movie from the images in the specified directory
        where:
          duration = time between each frame
    '''
    movie_name = kwargs.get('movie_name',"")
    movie_frames = kwargs.get('movie_frames',self.max_partial_step)

    # the folder to use when generating images during the run
    # - by default use the same folder as that used for generation
    image_folder = kwargs.get('image_folder',self.image_folder)

    # use the supplied duration parameter if present
    if 'duration' in kwargs:
      self.duration = kwargs.get('duration')

    print(f"Creating the movie: {movie_name} (duration = {self.duration}, steps = {movie_frames})",end="")
    with imageio.get_writer(movie_name, mode='I', duration=self.duration) as writer:
      for index in range(0,movie_frames+1):
        file = f"{image_folder}/step_{index}.png"
        if os.path.exists(file):
          image = imageio.imread(file)
          writer.append_data(image)
        else:
          print(f"Could not find image: {file}")
    print(f" - Complete")

    # remove the images when the movie has been made
    if kwargs.get('clear_images',True):
      self.clear_image_folder()


  def show(self, on_update, **kwargs):
    '''
        the base show function that performs the common operations of all show functions
    '''
    self.env.reset()
    self.total_reward = 0
    self.step = 0
    self.partial_step = 0
    self.done = False

    # define a callback function to call when the canvases are changed
    # - this then saves the current view
    def save_to_file(*args, **kwargs):
        # do a save and restore to force canvas update before writing
        # self.canvases[3].save()
        # self.canvases[3].restore()
        # self.canvases.to_file(f'{self.image_folder}/step_{self.partial_step}.png')
        self.write_file(delay=1)
        self.write_file(delay=1)

    if self.create_images:
      Utils.create_image_directory(self.image_folder)
      self.canvases.observe(save_to_file,'image_data')

    # run multiple policy iterations
    play, progress, layout = Utils.setup_play_level( self.env.level, on_update, max=(self.max_partial_step/self.save_interval), interval=self.play_interval )
    return VBox((self.canvases, HBox((play, progress))),layout=layout)


  def show_policy(self, policy: Policy, **kwargs):
    '''
        animate the steps of the supplied policy
    '''
    # store the supplied policy
    self.policy = policy

    # the default time between each step when just displaying the episode
    self.kPlayInterval = 80

    # the default time between each step when creating images from the episode
    self.kImageInterval = 300

    # setup any supplied parameter values
    self.set_parameters(**kwargs)

    # the time between each frame if a movie is created
    self.duration = 0.08

    # test if information should be shown
    # - the default function relies on the side panel being created for this
    info_function = kwargs.get('info_function',None)
    if kwargs.get('show_info') and info_function is None:
      # if an info function has not been supplied use the basic class member function
      info_function = self.get_info_string

    # each step is broken into 16 step_interval
    self.max_steps = kwargs.get('max_steps',10)
    step_interval = 16
    self.max_partial_step = (self.max_steps * step_interval)

    self.last_action = self.policy.get_action(self.env.x,self.env.y)
    self.last_state = np.array([0,0])

    self.current_state = [self.env.x,self.env.y]
    self.new_state = [self.env.x,self.env.y]

    def on_update(*args):

      if self.partial_step < self.max_partial_step:

        if (self.partial_step % step_interval) == 0:

          self.step += 1

          # keep going until the exit is reached
          if not self.done:

            self.current_state = [self.env.x,self.env.y]

            # get an action from the environment
            action = self.policy.get_action(self.env.x,self.env.y)


            # take the action and get the properties of the next state
            self.new_state, reward, self.done, truncated, info = self.env.step(action)
            self.total_reward += reward

            if info_function is not None:
              details = \
              {
                'state': self.current_state,
                'action': Direction.from_action(action),
                'reward': reward,
                'new_state': self.new_state,
                'total_reward': self.total_reward,
                'done': self.done,
                'truncated': truncated,
                'info': info,
                'step': self.step,
                'direction': Direction.get_string(Direction.get_direction(self.current_state,self.new_state))
              }
              self.env.show_info(info_function(details))

            # if the state hasn't changed set the last action to be 'stay'
            self.last_action = action
            if np.array_equal(self.new_state,self.last_state):
              self.last_action = Actions.Stay
            self.last_state = self.new_state

          else:
            # set the last action to 'stay' to signify the exit being reached
            self.last_action = Actions.Stay

        # test if an action that caused a move occurred
        if Actions(self.last_action) is not Actions.Stay:

          direction = Direction.get_direction(self.current_state,self.new_state)

          # 'partial_move' moves part of the way to the next state
          self.env.robot.partial_move(direction)

        self.partial_step += 1

      else:
        # reset at the end of the run
        self.last_state = [self.env.x,self.env.y]
        self.partial_step = 0
        self.done = False

    return self.show(on_update,**kwargs)


  def show_policy_evaluation(self, policy_evaluation: PolicyEvaluation, **kwargs):
    '''
        animate the iterations of policy evaluation
    '''
    # store the supplied policy evaluation object
    self.policy_evaluation = policy_evaluation

    # the default time between each step when just displaying the episode
    self.kPlayInterval = 500

    # the default time between each step when creating images from the episode
    self.kImageInterval = 3000

    # setup any supplied parameter values
    self.set_parameters(**kwargs)

    # the time between each frame if a movie is created
    self.duration = 1.0

    # each step is a single step_interval
    self.max_partial_step = self.max_steps

    # flag to indicate if policy evaluation has converged
    self.convergence = False

    # helper function to display grid information
    def get_info_string( iteration, values, directions=None ):
      info = {'text': values, 'precision': self.precision}

      if directions is not None:
        info['directions'] = {'arrows':directions}

      if iteration is not None:
        info_string = [((10,10),f"Iteration: {iteration}")]
        if self.convergence:
          info_string.append(((10,30),"Convergence"))
        info['side_info'] = info_string
      return info

    def on_update(*args):

      if self.partial_step < self.max_partial_step:

        # do policy updates for the specified number of iterations before a save
        for n in range(self.save_interval):
          self.policy_evaluation.do_iteration()
          self.partial_step += 1

        # calculate the largest difference in the state values from the start to end of the iteration
        delta = np.max(np.abs(self.policy_evaluation.end_values - self.policy_evaluation.start_values))

        # test if the difference is less than the defined convergence threshold
        if delta < self.policy_evaluation.threshold:
          self.convergence = True

        # get and display the state values and directions
        directions = self.policy_evaluation.policy.calculate_greedy_directions(self.policy_evaluation.end_values) if self.show_directions else None
        self.env.show_info(get_info_string(self.partial_step, self.policy_evaluation.end_values, directions))

        # add an extra delay between each step if images are being generated
        if self.create_images: sleep(2)
        self.env.render()

        if ((self.partial_step == self.max_partial_step) or self.convergence):
          self.done = True

          # reduce the max steps in case convergence has finished early
          self.max_partial_step = self.partial_step

    # add the initial state values to the grid at partial_step = 0
    directions = self.policy_evaluation.policy.calculate_greedy_directions(self.policy_evaluation.end_values) if self.show_directions else None
    self.env.show_info(get_info_string(self.partial_step, self.policy_evaluation.end_values, directions))
    self.env.render()

    return self.show(on_update,**kwargs)



  def show_monte_carlo_gpi(self, monte_carlo_gpi: MonteCarloGPI, min_delta=None, seed=None, **kwargs):
    '''
        animate the iterations of policy evaluation
    '''
    # store the supplied policy evaluation object
    self.monte_carlo_gpi = monte_carlo_gpi

    # the minimum delta stopping point
    self.min_delta = min_delta

    # the default time between each step when just displaying the episode
    self.kPlayInterval = 80

    # the default time between each step when creating images from the episode
    self.kImageInterval = 3000

    # setup any supplied parameter values
    self.set_parameters(**kwargs)

    # the time between each frame if a movie is created
    self.duration = 1.0

    # each step is a single step_interval
    self.max_partial_step = self.max_steps

    # flag to indicate if policy evaluation has converged
    self.convergence = False

    # save the initial state action values
    self.initial_values = self.monte_carlo_gpi.action_values.copy()

    # set the seed used to choose random actions
    self.seed = seed
    if seed is not None:
      np.random.seed(seed=seed)


    # helper function to display grid information
    def get_info_string( iteration, values, directions=None, delta=0 ):      

      # test if directions should be shown - otherwise show supplied values
      if self.show_directions and directions is not None:
        info = {'directions': {'arrows':directions,'text':directions}}
      else:
        info = {'values': values, 'precision': self.precision}

      if self.show_info and iteration is not None:
        info_string = [((10,10),f"Iteration: {iteration}"),
                       ((10,30),f"Delta: {delta:.4f}")]
        if self.convergence:
          info_string.append(((10,50),"Convergence"))
        info['side_info'] = info_string
      return info

    def on_update(*args):

      if self.partial_step <= self.max_partial_step and self.convergence == False:

        self.partial_step += 1
        delta = self.monte_carlo_gpi.do_iteration(self.seed)

        # test if the difference is less than the defined convergence threshold
        if self.min_delta is not None and delta < self.min_delta:
          print(f"delta: {delta} min_delta: {min_delta} convergence: {self.convergence}")
          self.convergence = True

        # get and display the state values, visits or directions
        directions = self.monte_carlo_gpi.policy.get_directions()
        values = self.monte_carlo_gpi.visits if self.show_visits else self.monte_carlo_gpi.action_values
        self.env.show_info(get_info_string(self.partial_step, values, directions, delta))

        # add an extra delay between each step if images are being generated
        if self.create_images: sleep(2)
        self.env.render()

        if ((self.partial_step == self.max_partial_step) or self.convergence):
          self.done = True

          # reduce the max steps in case convergence has finished early
          self.max_partial_step = self.partial_step

    # add the initial state values or visits to the grid at partial_step = 0
    directions = self.monte_carlo_gpi.policy.get_directions()
    values = self.monte_carlo_gpi.visits if self.show_visits else self.monte_carlo_gpi.action_values
    self.env.show_info(get_info_string(self.partial_step, values, directions))
    self.env.render()

    return self.show(on_update,**kwargs)