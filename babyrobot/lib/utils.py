# Copyright (c) Steve Roberts
# Distributed under the terms of the Modified BSD License.

from babyrobot.envs.lib.grid_level import GridLevel
from ipywidgets import Layout
from ipywidgets import Play, IntProgress, HBox, VBox, link
import imageio
import os
import gym


class Utils():

  def setup_play_level( level:GridLevel, on_update, interval=1000, min=0, max=8 ):
    ''' setup all the main components required to animate a grid level '''
    play = Play(interval=interval, min=min, max=max, step=1)
    progress = IntProgress(min=min, max=max)

    link((play, 'value'), (progress, 'value'))
    play.observe(on_update, 'value')

    canvas_dimensions = level.get_canvas_dimensions()
    layout = Layout(width=f'{canvas_dimensions[0]}px')
    return play, progress, layout


  def create_movie( movie_name, image_folder, max_steps, duration = 1.0 ):
    ''' create a gif movie from the images in the specified directory 
        where:
          duration = time between each frame
    '''
    with imageio.get_writer(movie_name, mode='I', duration=duration) as writer:      
      for index in range(0,max_steps):
        file = f"{image_folder}/step_{index}.png"
        if os.path.exists(file):
          image = imageio.imread(file)
          _ = writer.append_data(image)   


  def clear_directory( image_folder ):
    ''' clear any existing files from the directory '''
    filelist = [ f for f in os.listdir(image_folder) if f.endswith(".png") ]
    for f in filelist:
        os.remove(os.path.join(image_folder, f))      


  def create_image_directory( image_folder ):
    ''' create the specified folder to store each of the images that
        form an animated gif
        - if the folder already exists then clear any current files
    '''
    if not os.path.exists(image_folder):
        os.makedirs(image_folder)

    # clear any existing files from the directory
    Utils.clear_directory( image_folder )
          


def make( id: str, new_step_api=True, **setup: dict ):
  ''' custom make function for BabyRobot (used instead of 'gym.make')
      
    * In the latest version of Gym it forces the 'reset' function to be called
      before 'render'. This gives the error:        
      "Cannot call `env.render()` before calling `env.reset()`")
      
      Since we want to just create and then draw the environment
      we want to turn this off (using "env._disable_render_order_enforcing=True")

    * The render mode must be supplied to the make operation, otherwise you get 
      the warning:

      "You are calling render method, but you didn't specified the argument render_mode 
      at environment initialization."

    * The 'step' function now, instead of returning a single 'done' boolean to indicate
      the end of the episode, returns 2 booleans, 'terminated' and 'truncated'. 
      The 'new_step_api=True' parameter is required to stop a warning appearing:
      "Initializing wrapper in old step API"

    * id: The string used to create the environment with `gym.make`
  '''
  setup['new_step_api'] = new_step_api
  setup['render_mode'] = 'human'
  env = gym.make(id, **setup)  
  env._disable_render_order_enforcing=True  
  return env    


