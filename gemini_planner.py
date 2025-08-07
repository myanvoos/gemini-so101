import time
import io
import base64
import json
from typing import Dict, List, Optional
from google import genai
from google.genai import types
from PIL import Image
import numpy as np

class GeminiRobotPlanner:
    def __init__(self, api_key: str, model_name: str = "gemini-2.5-pro"):
        self.client = genai.Client(api_key=api_key)
        self.model_name = model_name
        self.chat = None
        self.planning_active = False
        self.last_plan_time = 0
        self.plan_interval = 2.0
        
    def start_planning_session(self, task_description: str):
        system_prompt = f"""
You are controlling a 6-DOF robotic arm. Here are the CORRECT joint directions:

Joints and their directions:
- shoulder_pan: rotation around vertical axis. POSITIVE = clockwise (right), NEGATIVE = counter-clockwise (left)
- shoulder_lift: POSITIVE = DOWN, NEGATIVE = UP (this is critical - positive moves arm DOWN!)
- elbow_flex: POSITIVE = retract backwards, NEGATIVE = extend forward  
- wrist_flex: POSITIVE = wrist down, NEGATIVE = wrist up
- wrist_roll: POSITIVE = clockwise rotation, NEGATIVE = counter-clockwise
- gripper: 0=closed, 100=open. NEGATIVE delta = close more, POSITIVE delta = open more

MOVEMENT RULES:
- To move arm DOWN: use POSITIVE shoulder_lift delta (e.g. +2.0)
- To move arm UP: use NEGATIVE shoulder_lift delta (e.g. -2.0)
- To extend arm forward: use NEGATIVE elbow_flex delta
- To retract arm back: use POSITIVE elbow_flex delta
- Use SMALL deltas (1-5 degrees) for safety

You have TWO cameras:
1. FRONT camera: shows gripper close-up view
2. SCENE camera: shows full workspace view

Task: {task_description}

Respond with SHORT JSON only:
{{
    "action": "move",
    "movements": [
        {{"joint": "shoulder_lift", "delta": 2.0, "reason": "move arm DOWN"}}
    ],
    "explanation": "Brief explanation"
}}

Remember: POSITIVE shoulder_lift = DOWN, NEGATIVE shoulder_lift = UP!
"""
        
        self.chat = self.client.chats.create(model=self.model_name)
        self.chat.send_message(system_prompt)
        self.planning_active = True
        
    def stop_planning(self):
        print("AI planning stopped!")
        self.planning_active = False
        self.chat = None
        
    def analyze_and_plan(self, front_image: Image.Image, scene_image: Image.Image, current_positions: Dict) -> Optional[Dict]:
        if not self.planning_active or not self.chat:
            return None
            
        current_time = time.time()
        if current_time - self.last_plan_time < self.plan_interval:
            return None
            
        try:
            front_buffer = io.BytesIO()
            front_image.save(front_buffer, format='JPEG', quality=85)
            front_bytes = front_buffer.getvalue()
            
            scene_buffer = io.BytesIO()
            scene_image.save(scene_buffer, format='JPEG', quality=85)
            scene_bytes = scene_buffer.getvalue()
            
            positions_text = f"""
Current joint positions:
- shoulder_pan: {current_positions.get('shoulder_pan', 0):.1f}°
- shoulder_lift: {current_positions.get('shoulder_lift', 0):.1f}°
- elbow_flex: {current_positions.get('elbow_flex', 0):.1f}°
- wrist_flex: {current_positions.get('wrist_flex', 0):.1f}°
- wrist_roll: {current_positions.get('wrist_roll', 0):.1f}°
- gripper: {current_positions.get('gripper', 0):.1f}%
"""
            
            response = self.chat.send_message([
                "Analyze these robot camera views and provide movement commands:",
                positions_text,
                "FRONT camera (gripper view):",
                types.Part.from_bytes(data=front_bytes, mime_type="image/jpeg"),
                "SCENE camera (full workspace view):",
                types.Part.from_bytes(data=scene_bytes, mime_type="image/jpeg")
            ])
            
            response_text = response.text.strip()
            print(response_text)
            
            if response_text.startswith("```json"):
                response_text = response_text[7:-3]
            elif response_text.startswith("```"):
                response_text = response_text[3:-3]
                
            plan = json.loads(response_text)
            self.last_plan_time = current_time
            return plan
            
        except Exception as e:
            print(f"Gemini planning error: {e}")
            return None
            
    def execute_plan(self, plan: Dict, current_positions: Dict) -> Dict:
        if not plan or plan.get("action") == "stop":
            return {}
            
        action = {}
        movements = plan.get("movements", [])
        
        for movement in movements:
            joint = movement.get("joint")
            delta = movement.get("delta", 0)
            
            if joint in current_positions:
                current_value = current_positions[joint]
                new_value = current_value + delta
                
                if joint == "gripper":
                    new_value = max(0, min(100, new_value))
                else:
                    new_value = max(-180, min(180, new_value))
                    
                action[f"{joint}.pos"] = new_value
                
        return action 