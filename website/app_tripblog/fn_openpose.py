import sys
import cv2
import os
from sys import platform
import argparse
import numpy as np
import time


root ='/Users/Jessie/MultiPersonMatching-master/'
openpose_path = '/Users/Jessie/openpose/build/python'
sys.path.append(openpose_path)
from openpose import pyopenpose as op

class OpenposeObject():
    def __init__(self):
        self.model_keypoints = []
        self.params = dict()
        self.params['model_folder'] = '/Users/Jessie/openpose/models/'
    
    def load_model_img(self, imageToProcess):
        #  starting openpose
        opWrapper = op.WrapperPython()
        opWrapper.configure(self.params)
        opWrapper.start()

        # process image
        datum = op.Datum()
        


        #imageToProcess = cv2.imread(model_path)
        #print(imageToProcess.shape)
        #print(imageToProcess)
        datum.cvInputData = imageToProcess
        opWrapper.emplaceAndPop([datum])
        self.model_keypoints = datum.poseKeypoints[0, :, :2]

        # cv2.imshow('model', datum.cvOutputData)
        # cv2.waitKey(0) 


        print(self.model_keypoints)





# give score to model and input
# image_wh = cv2.imread('/Users/Jessie/MultiPersonMatching-master/data/image_data/IMG_8840.JPG',0)
# print(image_wh.shape)
# quit()









# np.save('my_array', model_keypoints)

