import gymnasium


class BabyRobotEnv_v0(gymnasium.Env):
    
    def __init__(self):
        super().__init__()
        pass

    def step(self, action):        
        state = 1    
        reward = -1            
        done = True
        truncated = False
        info = {}
        return state, reward, done, truncated, info

    def reset(self):
        state = 0
        return state
  
    def render(self,mode):
        pass
