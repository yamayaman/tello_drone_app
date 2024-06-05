import cv2
from collections import Counter

labels = (
    'nose',
    'eye_left',
    'eye_right',
    'ear_left',
    'ear_right',
    'shoulder_left',
    'shoulder_right',
    'elbow_left',
    'elbow_right',
    'wrist_left',
    'wrist_right',
    'hip_left',
    'hip_right',
    'knee_left',
    'knee_right',
    'ankle_left',
    'ankle_right'
)

pose_labels = [
    "Nomal",
    "is_hands_up",
    "is_left_hand_up",
    "is_right_hand_up",
    "T_pose"
]



def find_majority(list_det):
    vote_count = Counter(list_det)
    top_one = vote_count.most_common(1)
    return top_one[0][0]


def render(image, keypoints, pose):

    render = image

    # Person Keypoints
    for index in range(len(keypoints)):

        keypoint_x = keypoints[labels[index]]['x']
        keypoint_y = keypoints[labels[index]]['y']

        if keypoint_x and keypoint_y:
            cv2.circle(render, (int(keypoint_x), int(keypoint_y)), 2, (0, 255, 0), 2)
            cv2.putText(render, str(index), (keypoint_x, keypoint_y),cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2)
    # Pose
    cv2.putText(render, pose_labels[pose], (30, 60),cv2.FONT_HERSHEY_PLAIN, 5, (255, 0, 0), 5, cv2.LINE_AA)

    return render