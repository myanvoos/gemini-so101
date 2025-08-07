import time
from lerobot.common.robots.so101_follower import SO101FollowerConfig, SO101Follower
from lerobot.common.teleoperators.so101_leader import SO101LeaderConfig, SO101Leader
from lerobot.common.teleoperators.keyboard import KeyboardTeleopConfig, KeyboardTeleop
from lerobot.common.cameras.opencv.configuration_opencv import OpenCVCameraConfig
from PIL import Image
import os

PORT = "/dev/ttyACM0"
FOLLOWER_ID = "SO101_Follower"
KEYBOARD_TELEOP_ID = "Keyboard_Teleop"
SLEEP_INVERVAL = 0.02
LEADER_ID = "SO101_Leader"
LEADER_PORT = "/dev/ttyACM1"

# # Standard webcam cameras - front (gripper view) and scene (full view)
# camera_config = {
#     "front": OpenCVCameraConfig(
#         index_or_path="/dev/video2",
#         width=640,
#         height=480,
#         fps=30,
#     ),
#     "scene": OpenCVCameraConfig(
#         index_or_path="/dev/video0",
#         width=640,
#         height=480,
#         fps=25,
#     )
# }

robot_config = SO101FollowerConfig(
    port=PORT,
    id=FOLLOWER_ID,
    # cameras=camera_config
)

leader_config = SO101LeaderConfig(
    port=LEADER_PORT,
    id=LEADER_ID,
)

leader = SO101Leader(leader_config)
leader.connect(calibrate=False)

follower = SO101Follower(robot_config)
follower.connect(calibrate=False)
follower.calibrate()

# teleop_config = KeyboardTeleopConfig(
#     id=KEYBOARD_TELEOP_ID,
# )

# teleop = KeyboardTeleop(teleop_config)
# follower = SO101Follower(robot_config)
# teleop.connect()
# follower.connect()

while True:
    action = leader.get_action()
    follower.send_action(action)