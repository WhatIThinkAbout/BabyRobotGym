from enum import IntEnum

''' simple helper class to enumerate actions in the grid levels '''
class Actions(IntEnum):  
    Stay  = 0    
    North = 1
    East  = 2
    South = 3
    West  = 4

    # get the enum name without the class
    def __str__(self): return self.name  