
import functools
import time
from typing import Any, Dict, List
from grapycal import Node, Edge, InputPort, TextControl, ButtonControl, IntTopic, FunctionNode
from grapycal.sobjects.controls.threeControl import ThreeControl
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
        self.add_out_port('points')
        self.add_out_port('annotated')

    def init_node(self):
        super().init_node()
        if self.is_preview.get():
            return
        base_options = python.BaseOptions(model_asset_path='pose_landmarker_heavy.task')
        result_callback = lambda result,image,timestamp: self.run(self.result_callback,result=result,image=image,timestamp=timestamp)
        options = vision.PoseLandmarkerOptions(
            base_options=base_options,
            output_segmentation_masks=False,
            running_mode = mp.tasks.vision.RunningMode.LIVE_STREAM,
            result_callback = result_callback
            )
        self.detector = vision.PoseLandmarker.create_from_options(options)

    def edge_activated(self, edge: Edge, port: InputPort):
        self.run(self.task,image=edge.get_data())

    def task(self,image):
        
        image = mp.Image(image_format=mp.ImageFormat.SRGB, data=(image.transpose(1,2,0)*255).astype(np.uint8))
        self.detector.detect_async(image,int(time.time()*1000))

    def result_callback(self,result,image,timestamp):
        annotated_image = draw_landmarks_on_image(image.numpy_view(), result)
        y_scale = image.numpy_view().shape[0]/image.numpy_view().shape[1]
        points = []
        self.workspace.vars()['result'] = result
        for landmark in result.pose_world_landmarks[0]:
            points.append([
                landmark.x,
                -landmark.y,
                landmark.z,
            ])
        
        centerx = (points[11][0]+points[12][0]+points[23][0]+points[24][0])/4
        centery = (points[11][1]+points[12][1]+points[23][1]+points[24][1])/4
        centerz = (points[11][2]+points[12][2]+points[23][2]+points[24][2])/4
        
        for point in points:
            point[0]-=centerx 
            point[1]-=centery
            point[2]-=centerz

        self.get_out_port('points').push_data(points)
        self.get_out_port('annotated').push_data(annotated_image.transpose(2,0,1)/255)

class ThreeNode(Node):
    category = 'mediapipe'
    def build_node(self):
        super().build_node()
        self.label.set('Three')
        self.three = self.add_control(ThreeControl,'three')
        self.css_classes.append('fit-content')
        self.points_port = self.add_in_port('points')
        self.lines_port = self.add_in_port('lines')

    def edge_activated(self, edge: Edge, port: InputPort):
        if port is self.points_port:
            self.three.points.set(edge.get_data())
        elif port is self.lines_port:
            self.three.lines.set(edge.get_data())

    