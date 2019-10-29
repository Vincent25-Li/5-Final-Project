import sys
import cv2
import os
from sys import platform
import argparse
import numpy as np
from django.conf import settings


root ='/Users/Jessie/MultiPersonMatching-master/'
openpose_path = '/Users/Jessie/openpose/build/python'
sys.path.append(openpose_path)
from openpose import pyopenpose as op

class OpenposeObject():
    def __init__(self):
        self.model_keypoints = []
        self.model_width= []
        self.model_height= [] 
        self.params = dict()
        self.params['model_folder'] = '/Users/Jessie/openpose/models/'
        self.params['model_pose'] = 'COCO'
        self.params['net_resolution'] = '-1x256'
        self.opWrapper, self.datum = self.start_openpose()
        self.body25 = {
            'face_idx': [0] + list(range(15, 19)),
            'torso_idx': list(range(1, 8)),
            'leg_idx': list(range(8, 15)) + list(range(19, 25))
        }
        self.coco = {
            'face_idx': [0] + list(range(14, 18)),
            'torso_idx': list(range(1, 8)),
            'leg_idx': list(range(8, 14)) 
        }
    
    def start_openpose(self):
        #  starting openpose
        opWrapper = op.WrapperPython()
        opWrapper.configure(self.params)
        opWrapper.start()

        # process image
        datum = op.Datum()
        return opWrapper, datum

    def model_wh(self, width, height):
        self.model_width = width
        self.model_height = height

    def load_model_img(self, imageToProcess, user_account):
       
        #imageToProcess = cv2.imread(model_path)
        #print(imageToProcess.shape)
        #print(imageToProcess)
        self.datum.cvInputData = imageToProcess
        self.opWrapper.emplaceAndPop([self.datum])
        self.model_keypoints = self.datum.poseKeypoints[0, :, :2]

        # cv2.imshow('model', datum.cvOutputData)
        # cv2.waitKey(0) 


        # print(self.model_keypoints)

        openpose_path= os.path.join(settings.MEDIA_ROOT, user_account, "openpose")
        if os.path.exists(openpose_path):
            model_path = os.path.join(settings.MEDIA_ROOT, user_account, "openpose", "model.jpg")
            
            cv2.imwrite(model_path, self.datum.cvOutputData)

        else:
            os.mkdir(openpose_path)
            model_path = os.path.join(settings.MEDIA_ROOT, user_account, "openpose", "model.jpg")
            
            cv2.imwrite(model_path, self.datum.cvOutputData)


    def openpose_matching(self, imageToProcess, user_account):
        imageToProcess_flip = cv2.flip(imageToProcess, 1)
        self.datum.cvInputData = imageToProcess_flip
        self.opWrapper.emplaceAndPop([self.datum])
        realtime_keypoints = self.datum.poseKeypoints[0, :, :2]

        input_face_transformed = self.affine_transform(self.model_keypoints, realtime_keypoints, self.coco['face_idx'])
        input_torso_transformed = self.affine_transform(self.model_keypoints, realtime_keypoints, self.coco['torso_idx'])
        input_leg_transformed = self.affine_transform(self.model_keypoints, realtime_keypoints, self.coco['leg_idx'])
        input_rejoin_keypoints = np.concatenate([
            input_face_transformed,
            input_torso_transformed,
            input_leg_transformed
        ])
        input_rejoin_idx = np.array(self.coco['face_idx']+self.coco['torso_idx']+self.coco['leg_idx'])
        # input_rejoin_idx = tuple(self.body25['face_idx']+self.body25['torso_idx']+self.body25['leg_idx'])
        input_keypoints_transformed = input_rejoin_keypoints.take(input_rejoin_idx, 0)

        # print(input_keypoints_transformed)

        model_keypoints_n = self.transform_percent_vector(self.model_keypoints)
        input_keypoints_transformed_n = self.transform_percent_vector(input_keypoints_transformed)
        score2 = self.similarity_score(model_keypoints_n, input_keypoints_transformed_n)
        print(score2)
        if score2 > 0.1:
        
            openpose_path= os.path.join(settings.MEDIA_ROOT, user_account, "openpose")
            realtime_path = os.path.join(settings.MEDIA_ROOT, user_account, "openpose", "realtime.jpg")
            realtime_original_path = os.path.join(settings.MEDIA_ROOT, user_account, "openpose", "realtime_o.jpg")
            if os.path.exists(openpose_path):
                cv2.imwrite(realtime_original_path, imageToProcess)
                cv2.imwrite(realtime_path, self.datum.cvOutputData)

            else:
                os.mkdir(openpose_path)
                cv2.imwrite(realtime_original_path, imageToProcess)
                cv2.imwrite(realtime_path, self.datum.cvOutputData)
          
            return True
        return False
    



    def transform_percent_vector(self, model_keypoints):
        percent_vector = model_keypoints / np.array((self.model_width, self.model_height))

        return percent_vector


    def similarity_score(self, model, input):
        d = np.sqrt(np.sum(np.square(model - input)))
        score = 1 - (1 / (1 +np.exp(-d)))
        print(d)

        return score

    # affine transformation of input

    def affine_transform(self, model, input, idx=False):
        if not idx:
            idx = list(range(model.shape[0]))
        pad = lambda x: np.hstack([x, np.ones([x.shape[0], 1])])
        Y = pad(model[idx])
        X = pad(input[idx])
        A_b, res, rank, s = np.linalg.lstsq(X, Y)
        transform = np.dot(X, A_b)
        return transform[:, :2].astype(np.float32)


# give score to model and input
# image_wh = cv2.imread('/Users/Jessie/MultiPersonMatching-master/data/image_data/IMG_8840.JPG',0)
# print(image_wh.shape)
# quit()









# np.save('my_array', model_keypoints)

