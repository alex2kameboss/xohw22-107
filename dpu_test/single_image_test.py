#!/usr/bin/env python
# coding: utf-8

# load graph and create runner

# In[1]:


from ctypes import *
from typing import List
import cv2
import numpy as np
import vart
import os
import pathlib
import xir
import threading
import time
import sys
import argparse
import math


# In[2]:


def get_child_subgraph_dpu(graph: "Graph") -> List["Subgraph"]:
    assert graph is not None, "'graph' should not be None."
    root_subgraph = graph.get_root_subgraph()
    assert (root_subgraph is not None), "Failed to get root subgraph of input Graph object."
    if root_subgraph.is_leaf:
        return []
    child_subgraphs = root_subgraph.toposort_child_subgraph()
    assert child_subgraphs is not None and len(child_subgraphs) > 0
    return [
        cs
        for cs in child_subgraphs
        if cs.has_attr("device") and cs.get_attr("device").upper() == "DPU"
    ]


# In[3]:


model = "plate_detect.xmodel"
g = xir.Graph.deserialize(model)
subgraphs = get_child_subgraph_dpu(g)
runner = vart.Runner.create_runner(subgraphs[0], "run")


# In[4]:


def preprocess_image(image_in):
    means = [128, 128, 128]
    scales = [1.0, 1.0, 1.0]
    image = cv2.resize(image_in, (320, 320))
    B, G, R = cv2.split(image)
    B = (B - means[0]) * scales[0]
    G = (G - means[1]) * scales[1]
    R = (R - means[2]) * scales[2]
    image = cv2.merge([B, G, R])
    image = image.astype(np.int8)
    return image

def run_one_image(image_in, dpu):
    # prepare input and putput tensors
    inputTensors = runner.get_input_tensors()
    outputTensors = runner.get_output_tensors()
    input_ndim = tuple(inputTensors[0].dims)
    output_ndim0 = tuple(outputTensors[len(outputTensors) - 2].dims)
    output_ndim1 = tuple(outputTensors[len(outputTensors) - 1].dims)
    outputData = [np.empty(output_ndim0, dtype=np.int8, order="C"), 
            np.empty(output_ndim1, dtype=np.int8, order="C")]
    inputData = [np.empty(input_ndim, dtype=np.int8, order="C")]
    inputData[0][0, ...] = preprocess_image(image_in)
    
    # start dpu and wait for result
    job_id = dpu.execute_async(inputData,outputData)
    dpu.wait(job_id)

    # process the output
    # find the bb with the max score for plate
    c_max = 0                                             
    hei_max = 0                                           
    wid_max = 0                                           
    maxvalue = outputData[1][0][0][0][64]                              
    for c in range(64):                                                                        
        for hei in range(10):                                                                  
            for wid in range(10):                                                              
                if (outputData[1][0][hei][wid][64 + c] > maxvalue):                                                        
                    c_max = c                                                                             
                    hei_max = hei                                                                         
                    wid_max = wid                                                                         
                    maxvalue = outputData[1][0][hei][wid][64 + c]                                                                      
    ne_maxvalue = outputData[1][0][hei_max][wid_max][c_max]                                                        
    prob_score = math.exp(maxvalue) /(math.exp(maxvalue) + math.exp(ne_maxvalue))
    
    # draw bb
    height, width = image_in.shape[0:2]
    height_ratio = float(height) / 320
    width_ratio = float(width) / 320

    bb = np.array(outputData[0][0])

    r_ind = c_max / 8                                                                                 
    c_ind = c_max % 8                                                                                 
    row = 8 * hei_max + r_ind                                                                         
    col = 8 * wid_max + c_ind                                                                        
    x_1 = int((col * 4 + bb[hei_max, wid_max, c_max]) * width_ratio)                 
    y_1 = int((row * 4 + bb[hei_max, wid_max, 64 + c_max]) * height_ratio)            
    x_2 = int((col * 4 + bb[hei_max, wid_max, 128 + c_max]) * width_ratio)                
    y_2 = int((row * 4 + bb[hei_max, wid_max, 192 + c_max]) * height_ratio)                          
    x_3 = int((col * 4 + bb[hei_max, wid_max, 256 + c_max]) * width_ratio)                           
    y_3 = int((row * 4 + bb[hei_max, wid_max, 320 + c_max]) * height_ratio)                           
    x_4 = int((col * 4 + bb[hei_max, wid_max, 384 + c_max]) * width_ratio)                            
    y_4 = int((row * 4 + bb[hei_max, wid_max, 448 + c_max]) * height_ratio)                          

    return cv2.rectangle(image_in, (x_1, y_1), (x_3, y_3), (0, 255, 0), 2)


# run for one image

# read the image and save

# In[8]:


img = cv2.imread("test.jpg")
result = run_one_image(img, runner)
cv2.imwrite("demo.jpg", result)