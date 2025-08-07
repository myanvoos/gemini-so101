import time
from lerobot.common.robots.so101_follower import SO101FollowerConfig, SO101Follower
from lerobot.common.teleoperators.so101_leader import SO101LeaderConfig, SO101Leader
from lerobot.common.teleoperators.keyboard import KeyboardTeleopConfig, KeyboardTeleop
from lerobot.common.cameras.opencv.configuration_opencv import OpenCVCameraConfig
from PIL import Image
# from gemini_planner import GeminiRobotPlanner
import os

PORT = "/dev/ttyACM0"
FOLLOWER_ID = "SO101_Follower"
KEYBOARD_TELEOP_ID = "Keyboard_Teleop"
SLEEP_INVERVAL = 0.02
LEADER_ID = "SO101_Leader"
LEADER_PORT = "/dev/ttyACM1"

# Standard webcam cameras - front (gripper view) and scene (full view)
camera_config = {
    "front": OpenCVCameraConfig(
        index_or_path="/dev/video2",
        width=640,
        height=480,
        fps=30,
    ),
    "scene": OpenCVCameraConfig(
        index_or_path="/dev/video0",
        width=640,
        height=480,
        fps=25,
    )
}

robot_config = SO101FollowerConfig(
    port=PORT,
    id=FOLLOWER_ID,
    cameras=camera_config
)

leader_config = SO101LeaderConfig(
    port=LEADER_PORT,
    id=LEADER_ID,
)

leader = SO101Leader(leader_config)
leader.connect(calibrate=False)
leader.calibrate()
leader.disconnect()

# teleop_config = KeyboardTeleopConfig(
#     id=KEYBOARD_TELEOP_ID,
# )

# teleop = KeyboardTeleop(teleop_config)
# follower = SO101Follower(robot_config)
# teleop.connect()
# follower.connect()

# # frame_counter = 0

# # # Initialize Gemini planner
# # gemini_api_key = os.getenv("GEMINI_API_KEY")
# # if not gemini_api_key:
# #     print("Warning: GEMINI_API_KEY not found. Set it with: export GEMINI_API_KEY='your_key'")
# #     print("AI planning will be disabled.")
# #     planner = None
# # else:
# #     planner = GeminiRobotPlanner(gemini_api_key)

# current_pos = follower.get_observation()
# joint_positions = {
#     "shoulder_pan": current_pos["shoulder_pan.pos"],
#     "shoulder_lift": current_pos["shoulder_lift.pos"], 
#     "elbow_flex": current_pos["elbow_flex.pos"],
#     "wrist_flex": current_pos["wrist_flex.pos"],
#     "wrist_roll": current_pos["wrist_roll.pos"],
#     "gripper": current_pos["gripper.pos"]
# }

# print("Controls:")
# print("Manual: q/a: shoulder_pan, w/s: shoulder_lift, e/d: elbow_flex")
# print("r/f: wrist_flex, t/g: wrist_roll, y/h: gripper")
# print("AI Planning: p: start planning, o: stop planning")
# print("ESC to exit")

# shoulder_pan_step_size = 2  # degrees
# shoulder_lift_step_size = 1.5  # degrees
# elbow_flex_step_size = 1.5  # degrees
# wrist_flex_step_size = 1.5  # degrees
# wrist_roll_step_size = 1.5  # degrees
# gripper_step_size = 3  # degrees

# ai_planning_active = False

# try:
#     while True:
#         pressed_keys = teleop.get_action()
        
#         # # Handle AI planning toggle
#         # if 'p' in pressed_keys and planner and not ai_planning_active:
#         #     task = input("\nEnter task description: ")
#         #     planner.start_planning_session(task)
#         #     ai_planning_active = True
#         #     print("AI planning started!")
            
#         # if 'o' in pressed_keys and ai_planning_active:
#         #     planner.stop_planning()
#         #     ai_planning_active = False
#         #     print("AI planning stopped!")
        
#         # Manual controls (only when AI planning is off)
#         if not ai_planning_active:
#             if 'q' in pressed_keys:
#                 joint_positions["shoulder_pan"] -= shoulder_pan_step_size
#             if 'a' in pressed_keys:
#                 joint_positions["shoulder_pan"] += shoulder_pan_step_size
#             if 'w' in pressed_keys:
#                 joint_positions["shoulder_lift"] += shoulder_lift_step_size
#             if 's' in pressed_keys:
#                 joint_positions["shoulder_lift"] -= shoulder_lift_step_size
#             if 'e' in pressed_keys:
#                 joint_positions["elbow_flex"] -= elbow_flex_step_size
#             if 'd' in pressed_keys:
#                 joint_positions["elbow_flex"] += elbow_flex_step_size
#             if 'r' in pressed_keys:
#                 joint_positions["wrist_flex"] -= wrist_flex_step_size
#             if 'f' in pressed_keys:
#                 joint_positions["wrist_flex"] += wrist_flex_step_size
#             if 't' in pressed_keys:
#                 joint_positions["wrist_roll"] += wrist_roll_step_size
#             if 'g' in pressed_keys:
#                 joint_positions["wrist_roll"] -= wrist_roll_step_size
#             if 'y' in pressed_keys:
#                 joint_positions["gripper"] += gripper_step_size
#             if 'h' in pressed_keys:
#                 joint_positions["gripper"] -= gripper_step_size
                
#         joint_positions["gripper"] = max(0, min(100, joint_positions["gripper"]))
        
#         # Action dict in the format expected by follower
#         action = {f"{joint}.pos": pos for joint, pos in joint_positions.items()}
        
#         # Get camera observation
#         observation = follower.get_observation()
#         front_image = Image.fromarray(observation["front"])
#         scene_image = Image.fromarray(observation["scene"])
        
#         # # AI Planning
#         # if ai_planning_active and planner:
#         #     plan = planner.analyze_and_plan(front_image, scene_image, joint_positions)
#         #     if plan:
#         #         print(f"Gemini plan: {plan.get('explanation', 'No explanation')}")
#         #         ai_action = planner.execute_plan(plan, joint_positions)
#         #         if ai_action:
#         #             # Update joint positions with AI plan
#         #             for joint_key, new_pos in ai_action.items():
#         #                 joint_name = joint_key.replace(".pos", "")
#         #                 if joint_name in joint_positions:
#         #                     joint_positions[joint_name] = new_pos
                    
#         #             action = ai_action
#         #             print(f"Executing: {list(ai_action.keys())}")
                    
#         #         if plan.get("action") == "complete":
#         #             print("Task completed!")
#         #             ai_planning_active = False
#         #             planner.stop_planning()
        
#         follower.send_action(action)
#         time.sleep(SLEEP_INVERVAL)

#         # The observation method returns a dictionary of joint positions and camera images as numpy arrays
#         # We can parse the camera images to PIL images and display them
#         # SLEEP_INTERVAL is the time between observations and directly affects camera frame rate
#         observation = follower.get_observation()
#         front_display = observation["front"]
#         front_display = Image.fromarray(front_display)
#         scene_display = observation["scene"]
#         scene_display = Image.fromarray(scene_display)
#         frame_counter += 1

#         if frame_counter % 5 == 0:
#             front_display.show()
#             scene_display.show()
        
# except KeyboardInterrupt:
#     print("\nExiting...")
# finally:
#     # if planner and ai_planning_active:
#     #     planner.stop_planning()
#     teleop.disconnect()
#     follower.disconnect()