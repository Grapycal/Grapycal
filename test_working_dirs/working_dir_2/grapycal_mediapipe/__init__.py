
from typing import Any, Dict, List
from grapycal import Node, Edge, InputPort, TextControl, ButtonControl, IntTopic, FunctionNode
from grapycal.sobjects.edge import Edge
from grapycal.sobjects.port import InputPort

import matplotlib
matplotlib.use('agg') # use non-interactive backend
import matplotlib.pyplot as plt

from mediapipe import solutions
from mediapipe.framework.formats import landmark_pb2
import numpy as np


def draw_landmarks_on_image(rgb_image, detection_result):
  pose_landmarks_list = detection_result.pose_landmarks
  annotated_image = np.copy(rgb_image)

  # Loop through the detected poses to visualize.
  for idx in range(len(pose_landmarks_list)):
    pose_landmarks = pose_landmarks_list[idx]

    # Draw the pose landmarks.
    pose_landmarks_proto = landmark_pb2.NormalizedLandmarkList()
    pose_landmarks_proto.landmark.extend([
      landmark_pb2.NormalizedLandmark(x=landmark.x, y=landmark.y, z=landmark.z) for landmark in pose_landmarks
    ])
    solutions.drawing_utils.draw_landmarks(
      annotated_image,
      pose_landmarks_proto,
      solutions.pose.POSE_CONNECTIONS,
      solutions.drawing_styles.get_default_pose_landmarks_style())
  return annotated_image

import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision


class PoseEstimateNode(FunctionNode):
    inputs = ['image']
    outputs = ['pose']
    max_in_degree = [1]
    category = 'mediapipe'

    def build_node(self):
        super().build_node()
        self.label.set('PoseEstimate')
        self.shape.set('normal')

    def init_node(self):
        super().init_node()
        base_options = python.BaseOptions(model_asset_path='pose_landmarker_heavy.task')
        options = vision.PoseLandmarkerOptions(
            base_options=base_options,
            output_segmentation_masks=True)
        self.detector = vision.PoseLandmarker.create_from_options(options)

    def calculate(self,image):
        
        # STEP 3: Load the input image.
        image = mp.Image(image_format=mp.ImageFormat.SRGB, data=(image[0].transpose(1,2,0)*255).astype(np.uint8))
        
        # STEP 4: Detect pose landmarks from the input image.
        detection_result = self.detector.detect(image)
        
        # STEP 5: Process the detection result. In this case, visualize it.
        annotated_image = draw_landmarks_on_image(image.numpy_view(), detection_result)

        annotated_image = (annotated_image.astype(np.float32)/255).transpose(2,0,1)
        return annotated_image