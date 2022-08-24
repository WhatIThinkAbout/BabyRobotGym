from gym.envs.registration import register
from .lib.utils import make
from ._version import __version__


#
# Release Gym Environments
#


register(
    id='BabyRobot-v0',
    entry_point='babyrobot.envs:BabyRobot_v0',
)


#
# Example Gym Environments
#

register(
    id='BabyRobotEnv-v0',
    entry_point='babyrobot.envs:BabyRobotEnv_v0',
)

register(
    id='BabyRobotEnv-v1',
    entry_point='babyrobot.envs:BabyRobotEnv_v1',
)

register(
    id='BabyRobotEnv-v2',
    entry_point='babyrobot.envs:BabyRobotEnv_v2',
)

register(
    id='BabyRobotEnv-v3',
    entry_point='babyrobot.envs:BabyRobotEnv_v3',
)

register(
    id='BabyRobotEnv-v4',
    entry_point='babyrobot.envs:BabyRobotEnv_v4',
)

register(
    id='BabyRobotEnv-v5',
    entry_point='babyrobot.envs:BabyRobotEnv_v5',
)

register(
    id='BabyRobotEnv-v6',
    entry_point='babyrobot.envs:BabyRobotEnv_v6',
)

register(
    id='BabyRobotEnv-v7',
    entry_point='babyrobot.envs:BabyRobotEnv_v7',
)
