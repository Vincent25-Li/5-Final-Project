import sys
import cv2
import os
from sys import platform
import argparse
import numpy as np
import time


root ='/Users/Jessie/MultiPersonMatching-master/'
openpose_path = root + '/Users/Jessie/openpose/build/python'
sys.path.append(openpose_path)
from openpose import pyopenpose as op


# affine transformation of input

def affine_transform(model, input, idx=False):
  if not idx:
    idx = list(range(model.shape[0]))
  pad = lambda x: np.hstack([x, np.ones([x.shape[0], 1])])
  Y = pad(model[idx])
  X = pad(input[idx])
  A_b, res, rank, s = np.linalg.lstsq(X, Y)
  transform = np.dot(X, A_b)
  return transform[:, :2].astype(np.float32)



# give score to model and input
model_keypoints = np.load('my_array.npy')

# print(image_wh.shape)
# quit()
height, width = 1600, 1600
def transform_percent_vector(model_keypoints):
  percent_vector = model_keypoints / np.array((height, width))

  return percent_vector


def similarity_score(model, input):
  d = np.sqrt(np.sum(np.square(model - input)))
  score = 1 / (1 +np.exp(-d))
  print(d)

  return score

params = dict()
params['model_folder'] = '/Users/Jessie/openpose/models/'
# params['num_gpu'] = 1 
# params['face'] = True
# params['hand'] = True

 #  starting openpose
opWrapper = op.WrapperPython()
opWrapper.configure(params)
opWrapper.start() 

datum = op.Datum()

start=time.time()
cap = cv2.VideoCapture(0)

while(True):
    # Capture frame-by-frame
    ret, frame = cap.read()

    # Our operations on the frame come here
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    if time.time() - start > 10 :
        datum.cvInputData = frame
        opWrapper.emplaceAndPop([datum])
        
        input_keypoints= datum.poseKeypoints[0, :, :2]

        # print(input_keypoints)

        # get 2d keypoints of model and input images
        body25 = {
            'face_idx': [0] + list(range(15, 19)),
            'torso_idx': list(range(1, 8)),
            'leg_idx': list(range(8, 15)) + list(range(19, 25))
        }
        input_face_transformed = affine_transform(model_keypoints, input_keypoints, body25['face_idx'])
        input_torso_transformed = affine_transform(model_keypoints, input_keypoints, body25['torso_idx'])
        input_leg_transformed = affine_transform(model_keypoints, input_keypoints, body25['leg_idx'])
        input_rejoin_keypoints = np.concatenate([
            input_face_transformed,
            input_torso_transformed,
            input_leg_transformed
        ])
        input_rejoin_idx = np.array(body25['face_idx']+body25['torso_idx']+body25['leg_idx'])
        # input_rejoin_idx = tuple(body25['face_idx']+body25['torso_idx']+body25['leg_idx'])
        input_keypoints_transformed = input_rejoin_keypoints.take(input_rejoin_idx, 0)

        print(input_keypoints_transformed)

        model_keypoints_n = transform_percent_vector(model_keypoints)
        input_keypoints_transformed_n = transform_percent_vector(input_keypoints_transformed)
        score2 = similarity_score(model_keypoints_n, input_keypoints_transformed_n)
        print(score2)
        if score2 > 0.6 :
          cv2.imwrite("./input.png", datum.cvInputData, [int(cv2.IMWRITE_PNG_COMPRESSION), 5])
          
            
          break

        start = time.time()

    # Display the resulting frame
    cv2.imshow('frame',frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break


# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()