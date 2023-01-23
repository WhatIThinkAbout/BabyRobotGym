
from .grid_level import GridLevel
from .draw_grid import DrawGrid
from .draw_info import DrawInfo


class GraphicalGridLevel( GridLevel ):

  def __init__( self, **kwargs: dict ):
    super().__init__( **kwargs )
    self.draw_grid = DrawGrid( self.grid_base, **kwargs )
    self.draw_info = DrawInfo( self.draw_grid, self.grid_info, **kwargs )    