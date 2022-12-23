
import numpy as np
from numpy import inf
from ipycanvas import hold_canvas
from .draw_grid import DrawGrid, Level
from .grid_info import GridInfo
from .arrows import Arrows
from .direction import Direction


class DrawInfo():

  arrow_color = '#00008b'    # color of any information arrows

  text_bg_color = 'rgba(40,40,40,0.7)' # text background shading
  text_fg_color = '#fff'               # text foreground color

  precision = 3   # the precision to use when writing floating point values


  def __init__( self, draw_grid: DrawGrid, grid_info: GridInfo, **kwargs: dict ):
    
    # get the basic details of the grid
    self.grid = draw_grid.grid

    # store the GridInfo object
    self.grid_info = grid_info

    # get the underlying grid drawing and canvases
    self.draw_grid = draw_grid    
    self.canvas = self.draw_grid.canvases[Level.Text]

    # setup the grid properties
    self.set_properties(kwargs.get('grid',None))   

    # arrow draw class
    self.arrows = Arrows( draw_grid.cell_pixels, draw_grid.padding,length=24,width=7,height=11)     


  '''
      Interface Functions
  '''

  def draw( self, props: dict ):
    ''' add the supplied info to the grid '''

    # test if any information has been supplied
    # - if it has then print this as a string
    if props is not None:    

      # test if a floating point precision has been defined
      self.precision = props.get('precision', self.precision)

      # test if any directions have been specified to add to the grid
      directions = props.get('directions',None)
      if directions is not None:                                
        self.process_direction_arrows(directions)
        self.process_direction_text(directions)

      # process any text to add to the grid
      self.process_text(props)

      # process anything to add to the info panel
      self.process_info(props)

      # test if coordinates should be added to the grid
      if props.get('coords',False):
        self.draw_coordinates()


  '''
      Info Dictionary Processing
  '''

  def set_default_values(self,args): 
    ''' replace any missing tuple elements in a text item with a default value '''  
  
    # the default values for the info panel text item
    defaultargs = ((0,0),"",190,20)
    
    # pad args with None up to the length of the default tuple
    args += (None,)*len(defaultargs)      

    # process each element & replace missing elements with default
    args = tuple(map(lambda x, y: y if y is not None else x, defaultargs, args))
    return args


  def process_info(self,info):
      ''' test if any text has been specified to add to the info panel '''

      # default colors to use when writing info
      fg_color = 'black'
      bk_color = 'white'

      text = info.get('side_info',None)
      if text is not None:     

        # check that a side panel was setup during grid creation
        if self.draw_grid.side_panel is None:
          raise Exception("\'side_panel\' must be specified during grid creation to allow side panel text.")

        # setup the info panel colors
        if type(self.draw_grid.side_panel) == dict:
          fg_color = self.draw_grid.side_panel.get('text_fg','black') 
          bk_color = self.draw_grid.side_panel.get('color','white')           

        # put text on side panel
        if self.draw_grid.side_panel:

          # clear existing text
          for item in text:
            (cx,cy),value,width,height = self.set_default_values(item)

            # offset by the grid width to get the start of the side panel
            cx += self.draw_grid.width_pixels            
            self.clear_info_panel_text( cx, cy, width, height, bk_color)

          for item in text:
            (cx,cy),value,width,height = self.set_default_values(item)

            # offset by the grid width to get the start of the side panel
            cx += self.draw_grid.width_pixels            
            self.info_panel_text(cx,cy,value,width,height,fg_color=fg_color,bk_color=bk_color)  


      text = info.get('bottom_info',None)
      if text is not None:        

        # check that a side panel was setup during grid creation
        if self.draw_grid.bottom_panel is None:
          raise Exception("\'bottom_panel\' must be specified during grid creation to allow bottom panel text.")

        if type(self.draw_grid.bottom_panel) == dict:
          fg_color = self.draw_grid.bottom_panel.get('text_fg','black') 
          bk_color = self.draw_grid.bottom_panel.get('color','white')             

        # put text on bottom panel
        if self.draw_grid.bottom_panel:

          # clear existing text
          for item in text:
            (cx,cy),value,width,height = self.set_default_values(item)
            cy += self.draw_grid.height_pixels 
            self.clear_info_panel_text( cx, cy, width, height, bk_color)

          for item in text:
            (cx,cy),value,width,height = self.set_default_values(item)
          
            # offset by the grid height to get the start of the bottom panel
            cy += self.draw_grid.height_pixels            
            self.info_panel_text(cx,cy,value,width,height,fg_color=fg_color,bk_color=bk_color)            


  def process_text(self,info):
      ''' test if any text has been specified to add to the grid '''

      text = info.get('text',None)      
      if text is not None:
        if isinstance(text,np.ndarray):
          self.draw_text_array(text)
        else:
          for (cx,cy),value in text:  
            self.draw_cell_text(cx,cy,value)


  def process_direction_arrows(self,directions):
    ''' test if any arrows should be added to the grid '''

    arrows = directions.get('arrows',None)
    if arrows is not None:
      # directions can be specified as a numpy array containing the 
      # directions for all cells or as individual cell directions
      if isinstance(arrows,np.ndarray):
        self.draw_direction_arrow_array(arrows)  
      else:          

        if len(arrows) > 0 and (type(arrows[0][0]) == int):
          # only cell coordinate supplied              
          for (cx,cy) in arrows:
            direction = self.grid_info.get_directions(cx,cy)
            self.draw_direction_arrow(cx,cy,direction)   

        else:
          # direction supplied with each cell
          for (cx,cy),direction in arrows:  
            self.draw_direction_arrow(cx,cy,direction)  


  def process_direction_text(self,directions):
    ''' test if the direction text should be added to the grid '''

    text = directions.get('text',None)
    if text is not None:
      # direction text can be specified as a numpy array containing the 
      # directions for all cells or as individual cell directions
      if isinstance(text,np.ndarray):
        self.draw_direction_text_array(text)  
      else:
        if len(text) > 0 and (type(text[0][0]) == int):
          # only cell coordinate supplied              
          for (cx,cy) in text:
            direction = self.grid_info.get_directions(cx,cy)
            self.draw_direction_text(cx,cy,direction)   

        else:
          # direction supplied with each cell
          for (cx,cy),direction in text:  
            self.draw_direction_text(cx,cy,direction)     


  '''
      Setup Functions
  '''

  def set_properties( self, grid_props: dict ):
    ''' setup the draw info properties '''    

    if grid_props is not None:
      colors = grid_props.get('colors',None)
      if colors is not None:    
        self.arrow_color = colors.get('arrows', self.arrow_color)    
        self.text_fg_color = colors.get('text_fg', self.text_fg_color)  
        self.text_bg_color = colors.get('text_bg', self.text_bg_color)  


  '''
      Direction Arrow Functions
  '''
          
  def draw_direction_arrow( self, x, y, directions ):   
    ''' draw an arrow in each direction from the supplied list ''' 
    
    canvas = self.draw_grid.canvases[Level.Overlay]
    color = self.arrow_color    
    padding = self.draw_grid.padding
    cell_pixels = self.draw_grid.cell_pixels
    px,py = self.draw_grid.grid_to_pixels( [x,y], padding, padding )          

    with hold_canvas(canvas):             
      canvas.clear_rect(px,py,cell_pixels,cell_pixels)
    
    with hold_canvas(canvas):       
      self.arrows.draw(canvas,px,py,directions,color)       


  def draw_direction_arrow_array(self, directions: np.array):
    ''' draw arrows in each direction in the supplied numpy array '''  
    canvas = self.draw_grid.canvases[Level.Overlay]      
    with hold_canvas(canvas):    
      for y in range(directions.shape[0]):
        for x in range(directions.shape[1]):
          self.draw_direction_arrow( x, y, directions[y,x])    


  '''
      Text Directions
  '''      
    
  def draw_direction_text( self, x, y, direction ):
    ''' convert the supplied direction bitfield value to a string, with a character for 
        each possible direction, and draw this on the specified cell
    '''
    self.draw_cell_text( x, y, Direction.get_string(direction) )


  def draw_direction_text_array(self,directions):   
    ''' add a text string to each cell showing the directions '''              
    
    # self.canvas.save()
    # with hold_canvas(self.canvas):    
    for y in range(directions.shape[0]):
      for x in range(directions.shape[1]):
        if x != self.grid.end[0] or y != self.grid.end[1]: 
          self.draw_direction_text( x, y, directions[y,x])    
    # self.canvas.restore()

  '''
      Coordinates
  '''            

  def draw_coordinates(self):
    ''' add the coordinates to each cell '''
    with hold_canvas(self.canvas):    
      for y in range(self.draw_grid.grid.height):
        for x in range(self.draw_grid.grid.width):
          self.draw_cell_text( x, y, f"({x},{y})")   
  


  '''
      Text Functions
  '''

  def draw_text_array(self,text):
    ''' draw the supplied array of text items to the grid '''
    with hold_canvas(self.canvas):    
      for y in range(text.shape[0]):
        for x in range(text.shape[1]):
          self.draw_cell_text( x, y, text[y,x])   


  def info_panel_text( self, x, y, text,width,height,                        
                       fg_color='#000', 
                       bk_color='#fff',
                       font='bold 14px sans-serif',
                       text_align='left',
                       text_baseline='top'):                       
    ''' add information text in the side panel ''' 
    canvas = self.canvas
    canvas.save()
    with hold_canvas(canvas): 
      canvas.fill_style = fg_color
      canvas.text_align = text_align
      canvas.text_baseline = text_baseline
      canvas.font = font
      canvas.fill_text(text, x, y)
    canvas.restore()


  def clear_info_panel_text( self, x, y, width, height, bk_color='#fff'):
    ''' clear the side panel at the specified location ''' 
    canvas = self.canvas
    with hold_canvas(canvas):     
      canvas.fill_style = bk_color      
      canvas.fill_rect(x,y-5,width,height) 


  def draw_cell_text( self, x, y, value, color = None, back_color = None ):
    ''' display the given value in the specified cell '''    
    
    # dont draw anything if no text is supplied
    num_value = False
    if type(value).__name__.startswith('str'):
      if len(value) == 0:
        return
    elif isinstance(x, (int, float, complex)) and not isinstance(x, bool):
      num_value = True
      if np.isnan(value):
        # don't show anything for NaN number values
        return

    # dont display text on base areas
    if self.grid.test_for_base_area(x,y):      
      return
    
    # limit floating point values to the default precision
    if isinstance(value, float):
      value = round(value,self.precision)
      if self.precision == 0:
        # convert to int if set to have no decimal places
        value = value.astype(int)       
    
    canvas = self.canvas
    padding = self.draw_grid.padding

    if color is None: color = self.text_fg_color
    if back_color is None: back_color = self.text_bg_color
    
    gx,gy = self.draw_grid.grid_to_pixels( [x,y], padding, padding )    
    cx,cy = self.draw_grid.get_center(gx,gy) # calculate the center of this cell

    # dimensions of background text shading
    bk_height = 20
    bk_width = 36

    # the width is set for 4 characters - expand if more than this
    if len(str(value)) > 4:
      bk_width += (len(str(value))-4) * 6
    
    # don't let the background extend outside the cell
    if bk_width > (self.draw_grid.cell_pixels - 4):
      bk_width = (self.draw_grid.cell_pixels - 4)

    # center the text
    x_off = (bk_width//2)
    y_off = (bk_height//2)

    # use a smaller font size for high precision, since more digits to fit
    font_size = 14
    text_offset = 5
    if (num_value and self.precision > 1) or \
       (not num_value and len(str(value)) >= 3):
          font_size = 12 
          text_offset = 4
    font_str = f"bold {font_size}px sans-serif"

    canvas.save()

    with hold_canvas(canvas):                    
      canvas.clear_rect(cx-x_off,cy-y_off,bk_width,bk_height) 
      if back_color is not None:
        canvas.fill_style = back_color        
        canvas.fill_rect(cx-x_off,cy-y_off,bk_width,bk_height) 
        
    with hold_canvas(canvas):                         
      canvas.fill_style = color
      canvas.text_align = 'center'
      canvas.font = font_str
      canvas.fill_text(f"{value}", cx, cy+text_offset)
      
    canvas.restore()