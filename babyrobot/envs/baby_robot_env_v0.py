import gymnasium


class BabyRobotEnv_v0(gymnasium.Env):
    
    def __init__(self):
        super().__init__()
        pass

    def step(self, action):        
        state = 1    
        reward = -1            
        terminated = True
        truncated = False
        info = {}
        return state, reward, terminated, truncated, info

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        state = 0
        info = {}
        return state,info
  
    def render(self):
        pass
