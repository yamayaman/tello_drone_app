import time

from tensorflow.lite.python.interpreter import Interpreter

from models.detection.person_keypoints.person_keypoints_detector import PersonKpPredictor


def get_person_kp_predictor(model_file):
    """
    人の骨格点の検知モデル
    Args:
        conf: アプリ設定

    Returns:
        骨格検知モデル
    """

    print('Loading file: %s ...' % model_file)
    start_time = time.time()
    interpreter = Interpreter(model_file, num_threads=2)
    interpreter.allocate_tensors()

    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f'It took {elapsed_time} seconds to load the model.')

    pers_kpts_predictor = PersonKpPredictor(interpreter)

    return pers_kpts_predictor