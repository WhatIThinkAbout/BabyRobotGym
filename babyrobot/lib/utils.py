# Copyright (c) Steve Roberts
# Distributed under the terms of the Modified BSD License.

from babyrobot.envs.lib.grid_level import GridLevel
from ipywidgets import Layout
from ipywidgets import Play, IntProgress, HBox, VBox, link
import imageio
import os


class Utils():

  def setup_play_level( level:GridLevel, on_update, interval=1000, min=1, max=8 ):
    ''' setup all the main components required to animate a grid level '''
    play = Play(interval=interval, min=min, max=max, step=1)
    progress = IntProgress(min=min, max=max, step=1)

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