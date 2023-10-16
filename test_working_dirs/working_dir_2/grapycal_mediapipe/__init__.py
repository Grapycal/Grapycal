
import time
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


class PoseEstimateNode(Node):
    category = 'mediapipe'

    def build_node(self):
        super().build_node()
        self.label.set('Pose Estimate')
        self.shape.set('normal')
        self.add_in_port('image',1)
        self.add_out_port('pose')
        self.add_out_port('annotated')

    def init_node(self):
        super().init_node()
        base_options = python.BaseOptions(model_asset_path='pose_landmarker_heavy.task')
        options = vision.PoseLandmarkerOptions(
            base_options=base_options,
            output_segmentation_masks=False,
            running_mode = mp.tasks.vision.RunningMode.LIVE_STREAM,
            result_callback = self.result_callback
            )
        self.detector = vision.PoseLandmarker.create_from_options(options)

    def edge_activated(self, edge: Edge, port: InputPort):
        self.run(self.task,image=edge.get_data())

    def task(self,image):
        
        image = mp.Image(image_format=mp.ImageFormat.SRGB, data=(image.transpose(1,2,0)*255).astype(np.uint8))
        self.detector.detect_async(image,int(time.time()*1000))

    def result_callback(self,result,image,timestamp):
        annotated_image = draw_landmarks_on_image(image.numpy_view(), result)
        self.get_out_port('pose').push_data(result.pose_landmarks)
        self.get_out_port('annotated').push_data(annotated_image.transpose(2,0,1)/255)