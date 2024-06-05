import numpy as np


class TFLiteNet():
    """
    TFliteのネットワークをルパー
    """

    def __init__(self, interpreter):
        self.interpreter = interpreter

    def set_input_tensor(self, image):
        """
        画像を入力する
        Args:
            image:画像

        """
        tensor_index = self.interpreter.get_input_details()[0]['index']
        # 本モデルは index=0
        input_tensor = self.interpreter.tensor(tensor_index)()[0]
        input_tensor[:, :] = image

    def get_output_tensor(self, index):
        """
        指定されたindexで出力Tensorを返します
        Args:
            index:

        Returns:
            検知結果を含むTensor
        """
        output_details = self.interpreter.get_output_details()[index]
        tensor = np.squeeze(self.interpreter.get_tensor(output_details['index']))
        return tensor
