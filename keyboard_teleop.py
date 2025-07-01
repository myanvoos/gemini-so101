import time
from lerobot.common.robots.so101_follower import SO101FollowerConfig, SO101Follower
from lerobot.common.teleoperators.keyboard import KeyboardTeleopConfig, KeyboardTeleop
from lerobot.common.cameras.opencv.configuration_opencv import OpenCVCameraConfig
from PIL import Image

PORT = "/dev/ttyACM0"
FOLLOWER_ID = "SO101_Follower"
KEYBOARD_TELEOP_ID = "Keyboard_Teleop"
SLEEP_INVERVAL = 2

# Standard webcam camera
camera_config = {
    "front": OpenCVCameraConfig(
        index_or_path="/dev/video2",
        width=640,
        height=480,
        fps=30,
    )
}

robot_config = SO101FollowerConfig(
    port=PORT,
    id=FOLLOWER_ID,
    cameras=camera_config
)

teleop_config = KeyboardTeleopConfig(
    id=KEYBOARD_TELEOP_ID,
)

teleop = KeyboardTeleop(teleop_config)
follower = SO101Follower(robot_config)
teleop.connect()
follower.connect()

current_pos = follower.get_observation()
joint_positions = {
    "shoulder_pan": current_pos["shoulder_pan.pos"],
    "shoulder_lift": current_pos["shoulder_lift.pos"], 
    "elbow_flex": current_pos["elbow_flex.pos"],
    "wrist_flex": current_pos["wrist_flex.pos"],
    "wrist_roll": current_pos["wrist_roll.pos"],
    "gripper": current_pos["gripper.pos"]
}

print("Keyboard controls:")
print("q/a: shoulder_pan, w/s: shoulder_lift, e/d: elbow_flex")
print("r/f: wrist_flex, t/g: wrist_roll, y/h: gripper")
print("ESC to exit")

shoulder_pan_step_size = 1  # degrees
shoulder_lift_step_size = 1.5  # degrees
elbow_flex_step_size = 1.5  # degrees
wrist_flex_step_size = 1.5  # degrees
wrist_roll_step_size = 1.5  # degrees
gripper_step_size = 3  # degrees

try:
    while True:
        pressed_keys = teleop.get_action()
        
        if 'q' in pressed_keys:
            joint_positions["shoulder_pan"] -= shoulder_pan_step_size
        if 'a' in pressed_keys:
            joint_positions["shoulder_pan"] += shoulder_pan_step_size
        if 'w' in pressed_keys:
            joint_positions["shoulder_lift"] += shoulder_lift_step_size
        if 's' in pressed_keys:
            joint_positions["shoulder_lift"] -= shoulder_lift_step_size
        if 'e' in pressed_keys:
            joint_positions["elbow_flex"] -= elbow_flex_step_size
        if 'd' in pressed_keys:
            joint_positions["elbow_flex"] += elbow_flex_step_size
        if 'r' in pressed_keys:
            joint_positions["wrist_flex"] -= wrist_flex_step_size
        if 'f' in pressed_keys:
            joint_positions["wrist_flex"] += wrist_flex_step_size
        if 't' in pressed_keys:
            joint_positions["wrist_roll"] += wrist_roll_step_size
        if 'g' in pressed_keys:
            joint_positions["wrist_roll"] -= wrist_roll_step_size
        if 'y' in pressed_keys:
            joint_positions["gripper"] += gripper_step_size
        if 'h' in pressed_keys:
            joint_positions["gripper"] -= gripper_step_size
            
        joint_positions["gripper"] = max(0, min(100, joint_positions["gripper"]))
        
        # Action dict in the format expected by follower
        action = {f"{joint}.pos": pos for joint, pos in joint_positions.items()}
        
        follower.send_action(action)
        time.sleep(SLEEP_INVERVAL)  

        # The observation method returns a dictionary of joint positions and camera images as numpy arrays
        # We can parse the camera images to PIL images and display them
        # SLEEP_INTERVAL is the time between observations and directly affects camera frame rate
        observation = follower.get_observation()
        image = observation["front"]
        image = Image.fromarray(image)
        image.show()
        
except KeyboardInterrupt:
    print("\nExiting...")
finally:
    teleop.disconnect()
    follower.disconnect()