import imageio
import os

def write_when_drawn( canvas, file_path ):
  ''' save the canvas to the specified file when its drawing is complete
      - note: requires 'sync_image_data=True' to be set on the canvas
  '''
  def save_to_file(*args, **kwargs):
      canvas.to_file(file_path)  
  canvas.observe(save_to_file, "image_data")


def create_animated_gif( image_folder, output_file, max_images=100, duration=0.06 ):
  ''' create an animated gif by concatenating the images in the specified directory '''
  with imageio.get_writer(output_file, mode='I', duration=duration) as writer:    
    for index in range(0,max_images):      
      file = f"{image_folder}/step_{index}.png"
      if os.path.exists(file):      
        image = imageio.imread(file)
        writer.append_data(image)        