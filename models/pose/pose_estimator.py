import numpy as np
from collections import deque
from utils.utils import find_majority

NOMAL = 0
HANDS_UP = 1
LEFT_HAND_UP = 2
RIGHT_HAND_UP = 3
T_POSE = 4


class HumanPoseEstimator:

    def __init__(self):
        self.pose_last = NOMAL
        # 初期値は、0:通常姿勢
        self.poses = deque(5 * [0], maxlen=5)
        self.body = None
        self.min_degree_arm_up = 50
        self.max_degree_leg_up = 140

    def pose_estimate(self, person_keypoints, check_multi_frame):

        self.body = person_keypoints        

        if self.is_hands_up():
            pose_cur = HANDS_UP
        elif self.is_left_hand_up():
            pose_cur = LEFT_HAND_UP
        elif self.is_right_hand_up():
            pose_cur = RIGHT_HAND_UP
        elif self.is_t_pose():
            pose_cur = T_POSE
        else:
            pose_cur = NOMAL

        if check_multi_frame:
            self.poses.append(pose_cur)
            self.pose_last = find_majority(self.poses)
            return find_majority(self.poses)
        else:
            self.pose_last = pose_cur
            return pose_cur

    def is_hands_up(self):
        return self.is_left_hand_up() and self.is_right_hand_up()
        
    def is_left_hand_up(self):
        if self.body_parts_not_exists(self.body['wrist_left']) or \
           self.body_parts_not_exists(self.body['elbow_left']) or \
           self.body_parts_not_exists(self.body['nose']):
            return False
        if self.body['wrist_left']['y'] < self.body['nose']['y']:
            return True
        elif self.body['elbow_left']['y'] < self.body['nose']['y']:
            return True
        else:
            return False
    
    def is_right_hand_up(self):
        if self.body_parts_not_exists(self.body['wrist_right']) or \
           self.body_parts_not_exists(self.body['elbow_right']) or \
           self.body_parts_not_exists(self.body['nose']):
            return False
        if self.body['wrist_right']['y'] < self.body['nose']['y']:
            return True
        elif self.body['elbow_right']['y'] < self.body['nose']['y']:
            return True
        else:
            return False
        
    def is_t_pose(self):
        if self.body_parts_not_exists(self.body['wrist_left']) or \
           self.body_parts_not_exists(self.body['hip_left']) or \
           self.body_parts_not_exists(self.body['shoulder_left']) or \
           self.body_parts_not_exists(self.body['wrist_right']) or \
           self.body_parts_not_exists(self.body['hip_right']) or \
           self.body_parts_not_exists(self.body['shoulder_right']):
            return False
        
        else:
            dgree_left = self.get_angle_between_human_joint(self.body['hip_left'], 
                                                            self.body['wrist_left'], 
                                                            self.body['shoulder_left'])
            
            dgree_right = self.get_angle_between_human_joint(self.body['hip_right'], 
                                                             self.body['wrist_right'], 
                                                             self.body['shoulder_right'])

            return 85<= dgree_left <= 115 and 85<= dgree_right <= 115 # TODO:ハードコーディング治す。


    def body_parts_not_exists(self, body_parts):
        return body_parts['x'] is None or body_parts['y'] is None

        if bed_line_top[0] == bed_line_bottom[0]:
            # x軸に平行な直線
            line['x'] = bed_line_top[0]
        else:
            # y = mx + n
            line['m'] = (bed_line_top[1] - bed_line_bottom[1]) / (bed_line_top[0] - bed_line_bottom[0])
            line['n'] = bed_line_top[1] - (line['m'] * bed_line_top[0])
        return line

    # 点A(body_parts1)，B(target_body_parts)，C(body_parts2)がなす角∠ABC (点B周りの角度)の算出方法
    def get_angle_between_human_joint(self, body_parts1, body_parts2, target_body_parts):
        if self.body_parts_not_exists(body_parts1) or \
            self.body_parts_not_exists(target_body_parts) or \
            self.body_parts_not_exists(body_parts2):
            return 0

        a = np.array([body_parts1['x'], - body_parts1['y']])
        b = np.array([target_body_parts['x'], - target_body_parts['y']])
        c = np.array([body_parts2['x'], - body_parts2['y']])

        vec_a = a - b
        vec_c = c - b

        length_vec_a = np.linalg.norm(vec_a)
        length_vec_c = np.linalg.norm(vec_c)
        inner_product = np.inner(vec_a, vec_c)
        cos = inner_product / (length_vec_a * length_vec_c)

        # 角度（ラジアン）の計算
        rad = np.arccos(cos)

        # 弧度法から度数法（rad ➔ 度）への変換
        degree = np.rad2deg(rad)

        return degree

    def is_arm_up(self, body_part_name1, body_part_name2, body_part_name3):
        '''
        body_part_name1->body_part_name2->body_part_name3の角度から腕が上がっているかを判定する

        '''
        degree_left = self.get_angle_between_human_joint(self.body[f'{body_part_name1}_left'],
                                                         self.body[f'{body_part_name2}_left'],
                                                         self.body[f'{body_part_name3}_left'])
        if degree_left != 0:
            is_left_arm_up = (self.min_degree_arm_up < degree_left)
        else:
            is_left_arm_up = False

        degree_right = self.get_angle_between_human_joint(self.body[f'{body_part_name1}_right'],
                                                          self.body[f'{body_part_name2}_right'],
                                                          self.body[f'{body_part_name3}_right'])
        if degree_right != 0:
            is_right_arm_up = (self.min_degree_arm_up < degree_right)
        else:
            is_right_arm_up = False

        return is_left_arm_up, is_right_arm_up

    def is_leg_up(self, body_part_name1, body_part_name2, body_part_name3):
        '''
         body_part_name1->body_part_name2->body_part_name3の角度から足が上がっているかを判定する

         '''
        degree_left = self.get_angle_between_human_joint(self.body[f'{body_part_name1}_left'],
                                                         self.body[f'{body_part_name2}_left'],
                                                         self.body[f'{body_part_name3}_left'])

        if degree_left != 0:
            is_left_leg_up = (degree_left < self.max_degree_leg_up)
        else:
            is_left_leg_up = False

        degree_right = self.get_angle_between_human_joint(self.body[f'{body_part_name1}_right'],
                                                          self.body[f'{body_part_name2}_right'],
                                                          self.body[f'{body_part_name3}_right'])

        if degree_right != 0:
            is_right_leg_up =(degree_right < self.max_degree_leg_up)
        else:
            is_right_leg_up = False

        return is_left_leg_up, is_right_leg_up
