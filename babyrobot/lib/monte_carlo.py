# Copyright (c) Steve Roberts
# Distributed under the terms of the Modified BSD License.

import numpy as np
from tqdm import tqdm
from enum import IntEnum
import babyrobot
from ..envs import BabyRobotInterface
from ..envs.lib import Actions
from ..lib import Policy


class DeltaType(IntEnum):
    Max, Mean = range(2)



class MonteCarlo():

  last_start_pos = None         # the episode start position
  rewards: np.array             # rewards array to be initialised by child class
  values: np.array              # values array to be initialised by child class

  def __init__(self, policy: Policy, exploring_starts=False, every_visit=False, env=None, **env_setup):

    # store the setup used to define the environment
    self.env_setup = env_setup

    self.exploring_starts = exploring_starts
    self.every_visit = every_visit

    # store the policy used to select actions in the environment
    self.policy = policy
    
    if env is None:
      # create an evaluation version of the environment
      self.env = babyrobot.make("BabyRobot-v0", render_mode=None, **env_setup)
    else:
      # use the supplied environment
      self.env = env


  #
  # Graphical Helper Functions
  #

  def get_graphical_environment(self, text_data):
    ''' create a graphical version of the environment - virtual base method '''
    raise NotImplementedError()

  def show_values(self):
    ''' show the calculated state values '''
    env = self.get_graphical_environment(self.returns)
    return env

  def show_visits(self):
    ''' show the visits to each state '''
    env = self.get_graphical_environment(self.visits)
    return env


  #
  # Monte Carlo Method Functions
  #

  def get_next_start_state(self):
    ''' get the environment starting position for the next episode '''

    # by default begin at the defined start position
    x = self.env.start[0]
    y = self.env.start[1]

    if self.exploring_starts:

      if self.last_start_pos is not None:
        # move horizontally to the next state
        x = self.last_start_pos[0] + 1
        y = self.last_start_pos[1]

      while self.env.level.is_grid_state(x,y) == False:
        # move horizontally to the next state
        x += 1

        if x >= self.env.width:
          # move to the start of the next row
          x = 0
          y += 1

        # test if the last row is complete
        if y >= self.env.height:
          # go back to the start
          x = self.env.start[0]
          y = self.env.start[1]

    self.last_start_pos = [x,y]
    return self.last_start_pos


  def single_episode(self):
    '''
      run a single episode to collect the reward for each action of the trajectory
      - virtual base method
    '''
    raise NotImplementedError()


  def get_returns(self):
    raise NotImplementedError()


  def run(self, max_episodes = 1, delta_interval = 10, delta_type = DeltaType.Max, hide_progress = False):

    deltas = []
    for episode in (pbar:=tqdm(range(max_episodes), disable=hide_progress)):

      initial_values = self.returns.copy()

      # set the next start position
      self.env.set_initial_pos(self.get_next_start_state())

      rewards = self.single_episode()
      returns = self.rewards_to_returns(rewards)
      self.get_returns(returns)

      # save the change in the calculated values at regular intervals
      if episode%delta_interval == 0:
        # calculate the difference in the values from the start to end of the iteration
        if delta_type == DeltaType.Max:
          delta = np.max(np.abs(self.returns - initial_values))  # get the largest difference
        else:
          delta = np.mean(np.abs(self.returns - initial_values)) # get the average difference
        deltas.append(delta)
        pbar.set_description(f"Delta {delta:0.5f}")

    return self.returns, self.visits, deltas



class MonteCarloStateValues( MonteCarlo ):
  ''' base class for Monte Carlo methods calculating state values '''

  def __init__(self, policy: Policy, **setup):
    super().__init__(policy, **setup)

    # keep a count of the visits to each state
    self.visits = np.zeros((self.env.height,self.env.width))

    # the average returns for each state
    self.returns = np.zeros((self.env.height,self.env.width))


  def get_graphical_environment(self, text_data):
    ''' create a graphical version of the environment '''
    env = babyrobot.make("BabyRobot-v0", **self.env_setup)
    info = {'text': text_data, 'precision': 0}
    env.show_info(info)
    return env


  def rewards_to_returns(self, state_rewards):
    ''' work backwards to convert the rewards into returns '''
    γ = 1.0
    G = 0
    state_returns = []
    for state, reward in reversed(state_rewards):
      G = reward + γ*G
      state_returns.append((state,G))

    # put back into the order of states visited
    state_returns.reverse()
    return state_returns


  def single_episode(self):
    '''
      run a single episode to collect the reward for each action of the trajectory
    '''
    state,info = self.env.reset()
    state_rewards = []
    total_reward = 0
    terminated = False
    while not terminated:
      # get the policy's action in the current state
      action = self.policy.get_action(self.env.x,self.env.y)

      new_state, reward, terminated, truncated, info = self.env.step(action)
      total_reward += reward
      state_rewards.append((state,reward))
      state = new_state

    return state_rewards


  def get_returns(self, state_returns):
    ''' find the value of the first visit to a state '''
    episode_visits = np.zeros((self.env.height,self.env.width))

    # the first time a state is seen store the return value
    for s, G in state_returns:

      # if first-visit only process the state if it hasn't already been visited
      if self.every_visit or episode_visits[s[1],s[0]] == 0:

        # keep a count of the number of times this state is visited during this episode
        episode_visits[s[1],s[0]] += 1

        # increment the total count of first visits to this state
        self.visits[s[1],s[0]] += 1

        # get (1/visits) setting the result of any divide by zero to zero
        inv_visits = 1 / self.visits[s[1],s[0]]

        # only update the average returns of the states visited in this episode
        self.returns[s[1],s[0]] = ((1 - inv_visits)*self.returns[s[1],s[0]]) + (inv_visits*G)



class MonteCarloActionValues( MonteCarlo ):
  ''' base class for Monte Carlo methods calculating action values '''

  def __init__(self, policy: Policy, epsilon=0, env=None, seed=None, **setup):
    super().__init__(policy, env=env, **setup)

    # set the probability of taking a random action
    self.epsilon = epsilon

    # keep a count of the visits to each action
    self.visits = np.zeros((self.env.height,self.env.width, len(Actions)))

    # the average returns for each action
    self.returns = np.zeros((self.env.height, self.env.width, len(Actions)))

    # set the seed used to choose random actions
    if seed is not None:
      np.random.seed(seed=seed)    


  def get_graphical_environment(self, text_data):
    ''' create a graphical version of the environment '''
    env = babyrobot.make("BabyRobot-v0", **self.env_setup)
    info = {'values': text_data, 'precision': 0}
    env.show_info(info)
    return env


  def rewards_to_returns(self, rewards):
    ''' work backwards to convert the rewards into returns '''
    γ = 1.0
    G = 0
    returns = []
    for state, action, reward in reversed(rewards):
      G = γ*G + reward
      returns.append((state,action,G))

    # put back into the order of actions visited
    returns.reverse()
    return returns


  def single_episode(self):
    '''
      run a single episode to collect the reward for each action of the trajectory
    '''
    state,info = self.env.reset()
    action_rewards = []
    total_reward = 0
    terminated = False
    while not terminated:

      # probability of selecting a random action
      p = np.random.random()

      # if the probability is less than epsilon then a random action
      # is chosen from the state's available actions
      if p < self.epsilon:
        action = self.env.action_space.sample()
      else:
        # get the policy's action in the current state
        action = self.policy.get_action(self.env.x,self.env.y)

      new_state, reward, terminated, truncated, info = self.env.step(action)
      total_reward += reward
      action_rewards.append((state,action,reward))
      state = new_state

    return action_rewards


  def get_returns(self, returns):
    ''' get the return values for each state '''

    # the count of the number of times each action is visited during this episode
    action_visits = np.zeros((self.env.height, self.env.width, len(Actions)))

    # process every state-action pair in the supplied set of returns
    for s, a, G in returns:

      # if first-visit only process the action if it hasn't already been visited
      if self.every_visit or action_visits[s[1],s[0],a] == 0:

        # keep a count of the number of times this action is visited during this episode
        action_visits[s[1],s[0],a] += 1

        # increment the total count of first visits to this state action
        self.visits[s[1],s[0],a] += 1

        # get (1/visits) setting the result of any divide by zero to zero
        inv_visits = 1 / self.visits[s[1],s[0],a]

        # only update the average returns of the state actions visited in this episode
        self.returns[s[1],s[0],a] = ((1 - inv_visits)*self.returns[s[1],s[0],a]) + (inv_visits*G)




class MonteCarloGPI():

  def __init__(self, policy: Policy, evaluation_steps=1, epsilon=0.1, delta_type=DeltaType.Mean, **env_setup):    
    self.policy = policy
    self.evaluation_steps = evaluation_steps
    self.epsilon = epsilon
    self.delta_type = delta_type

    # create an evaluation version of the environment
    self.env = babyrobot.make("BabyRobot-v0", render_mode=None, **env_setup)    

    # keep a count of the first visits to each action
    self.visits = np.zeros((self.env.height, self.env.width, len(Actions)))

    # the average returns for each action
    self.action_values = np.zeros((self.env.height, self.env.width, len(Actions)))    

    # keep track of the deltas over the run
    self.deltas = []


  def do_iteration(self,seed=None):  

        initial_values = self.action_values.copy()     

        mc = MonteCarloActionValues(self.policy, epsilon = self.epsilon, env = self.env, seed = seed)
        eval_values, eval_visits, _ = mc.run(self.evaluation_steps, hide_progress = True)

        # increment the count of any actions that have been visited
        self.visits += eval_visits

        # get (1/visits) setting the result of any divide by zero to zero
        inv_visits = np.reciprocal(self.visits, where=self.visits!=0)

        # only update the average action values of the states visited in this episode
        self.action_values = self.action_values + (inv_visits * (eval_values - (self.action_values*eval_visits)))

        # update the policy with respect to the latest calculated action values
        self.policy.update_policy(self.action_values)  

        # calculate the difference in the action values from the start to end of the iteration
        if self.delta_type == DeltaType.Max:
          delta = np.max(np.abs(self.action_values - initial_values))  # get the largest difference
        else:
          delta = np.mean(np.abs(self.action_values - initial_values)) # get the average difference      

        # save the change in the action values 
        self.deltas.append(delta)          

        return delta      


  # def run( self, max_iterations=10, evaluation_steps=1, epsilon=0.1, min_delta=None, delta_interval=1, delta_type=DeltaType.Mean ):

  def run( self, max_iterations=10, min_delta=None, seed=None ):    
    ''' run 'max_iterations' of policy evaluation and improvement 
      - policy evaluation uses first-visit MC and runs for 'evaluation_steps' steps
    '''      
    
    self.deltas = []
    for episode in (pbar:=tqdm(range(max_iterations))):      

      # perform a single step of MC GPI
      delta = self.do_iteration(seed)
      pbar.set_description(f"Delta {delta:0.5f}")

      # if a minimum delta has been supplied test if the new delta has reached the threshold
      if min_delta is not None and delta < min_delta: 
        break      

    return self.action_values, self.visits, self.deltas, episode