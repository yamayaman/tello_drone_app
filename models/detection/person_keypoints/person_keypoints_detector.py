import cv2
import numpy as np

from models.detection.person_keypoints.tflite_net import TFLiteNet

class PersonKpPredictor(TFLiteNet):
    """ 
    骨格検知クラス
    """

    def __init__(self, interpreter):
        super().__init__(interpreter)

        self.input_image_width = None
        self.input_image_height = None

        self.keypoint_labels = (
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

    def preprocess(self, image):
        """
        画像の前処理:リサイズ、RGBへの変換、float32への変換、リシェイプを行う
        Args:
            image:入力画像
        Returns:
            処理した画像（processed_image）と入力画像のサイズ (shapes)
        """
        _, input_height, input_width, _ = self.interpreter.get_input_details()[0]['shape']
        self.input_image_height,  self.input_image_width, _ = image.shape

        resized_input = cv2.resize(image, (input_width, input_height))
        # BGR => RGB
        resized_rgb_input = cv2.cvtColor(resized_input, cv2.COLOR_BGR2RGB)
        processed_input = resized_rgb_input.astype(np.float32)

        return processed_input

    def predict(self, image_np):
        """
        骨格検知を行う
        Args:
            image_np: (height, width, 3)
        Returns:
            検知結果: 人の骨格点17個(person_keypoints) を格納した辞書
        """
        image = self.preprocess(image_np)
        self.set_input_tensor(image)
        self.interpreter.invoke()
        pers_kpts_with_scores = self.get_output_tensor(0)
        person_keypoints = {}
        scores = []

        for index in range(len(pers_kpts_with_scores)):
            keypoint_x = pers_kpts_with_scores[index][1]
            keypoint_y = pers_kpts_with_scores[index][0]
            score = pers_kpts_with_scores[index][2]

            # y座標をマイナスすることで画像座標系から標準座標系へ変換
            person_keypoints[self.keypoint_labels[index]] = {'x': keypoint_x, 'y': keypoint_y, 'score': score}

        return person_keypoints

    def get_person_kpts(self, key_points, score_threshold_for_per_kpts):
        """
               信頼度スコアが閾値以上の骨格点を取得する
               Args:
                   key_points:骨格点
                   score_threshold_for_per_kpts: scoreの低い検知を削除するために使用する閾値

               Returns:
                   検知結果: 信頼度スコアが閾値より大きい、人の骨格点17個(person_keypoints) を格納した辞書
                       キー：部位
                       バリュー： xy座標
               """

        person_keypoints = {}


        scale_x = self.input_image_width
        scale_y = self.input_image_height

        for index in range(len(key_points)):

            keypoint_x = int(scale_x * key_points[self.keypoint_labels[index]]['x'])
            keypoint_y = int(scale_y * key_points[self.keypoint_labels[index]]['y'])
            score = key_points[self.keypoint_labels[index]]['score']

            if score > score_threshold_for_per_kpts:
                person_keypoints[self.keypoint_labels[index]] = {'x': keypoint_x, 'y': keypoint_y, 'score': score}
            else:
                person_keypoints[self.keypoint_labels[index]] = {'x': None, 'y': None, 'score':None}

        return person_keypoints