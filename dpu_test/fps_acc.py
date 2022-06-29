#!/usr/bin/env python
# coding: utf-8

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


# In[10]:


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

# prepare input and putput tensors
inputTensors = runner.get_input_tensors()
outputTensors = runner.get_output_tensors()
input_ndim = tuple(inputTensors[0].dims)
output_ndim0 = tuple(outputTensors[len(outputTensors) - 2].dims)
output_ndim1 = tuple(outputTensors[len(outputTensors) - 1].dims)

def run_one_image(image_in, dpu, height_ratio, width_ratio):
    outputData = [np.empty(output_ndim0, dtype=np.int8, order="C"), 
            np.empty(output_ndim1, dtype=np.int8, order="C")]
    inputData = [np.empty(input_ndim, dtype=np.int8, order="C")]
    inputData[0][0, ...] = image_in
    
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
    
    if prob_score > 0.2:
        # draw bb
        bb = np.array(outputData[0][0])

        r_ind = c_max / 8                                                                                 
        c_ind = c_max % 8                                                                                 
        row = 8 * hei_max + r_ind                                                                         
        col = 8 * wid_max + c_ind                                                                        
        x_1 = int((col * 4 + bb[hei_max, wid_max, c_max]) * width_ratio)                 
        y_1 = int((row * 4 + bb[hei_max, wid_max, 64 + c_max]) * height_ratio)            
        x_3 = int((col * 4 + bb[hei_max, wid_max, 256 + c_max]) * width_ratio)                           
        y_3 = int((row * 4 + bb[hei_max, wid_max, 320 + c_max]) * height_ratio)                           

        return [x_1, y_1, x_3, y_3]
    else:
        return None


# In[11]:


images_paths = []
buffer = []
results = []
height_ratios = []
width_ratios = []

directory = 'images'
for filename in os.listdir(directory):
    f = os.path.join(directory, filename)
    # checking if it is a file
    if os.path.isfile(f):
        results.append(None)
        images_paths.append(filename)
        image = cv2.imread(f)
        height, width = image.shape[0:2]
        height_ratios.append(float(height) / 320)
        width_ratios.append(float(width) / 320)
        buffer.append(preprocess_image(image))


# In[12]:


start = time.time()
for i in range(len(buffer)):
    result = run_one_image(buffer[i], runner, height_ratios[i], width_ratios[i])
    results[i] = [images_paths[i], result]
stop = time.time()


# In[14]:


t = 0
c = 0
for result in results:
    t += 1
    if result[1] is not None:
        c += 1
        print("%s,%d,%d,%d,%d" % (result[0], result[1][0], result[1][1], result[1][2], result[1][3]))
    else:
        print("%s,,,," % (result[0]))
    
print('Acc:' + str(c) + "/" + str(t))

# In[13]:


delta = stop - start
print("Taken time: ", delta, "seconds")
fps = float(len(buffer) / delta)
print("FPS: ", fps)