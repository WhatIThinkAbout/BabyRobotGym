from gym.envs.registration import register

register(
    id='BabyRobotEnv-v0',
    entry_point='baby_robot_gym.envs:BabyRobotEnv_v0',
)

register(
    id='BabyRobotEnv-v1',
    entry_point='baby_robot_gym.envs:BabyRobotEnv_v1',
)

register(
    id='BabyRobotEnv-v2',
    entry_point='baby_robot_gym.envs:BabyRobotEnv_v2',
)
