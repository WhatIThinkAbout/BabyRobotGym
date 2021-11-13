from gym.envs.registration import register

register(
    id='baby-robot-v0',
    entry_point='baby_robot_gym.envs:BabyRobotEnv',
)
