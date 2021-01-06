#import tensorflow as tf
import cv2
import numpy as np
#from backend.config import id2name

#PATH_TO_CKPT = 'models/ssdlite_mobilenet_v2.pb'
PATH_TO_CONFIG = 'backend/model_config/ladder/ladder_yolov4.cfg'
PATH_TO_WEIGTHS = 'backend/model_config/ladder/ladder_yolov4_best.weights'
def load_model():
    yolo_model = cv2.dnn.readNetFromDarknet(PATH_TO_CONFIG,PATH_TO_WEIGTHS)
    return yolo_model


def inference(img_arr, conf_thresh=0.5,max_suppression_thresh=0.4):
    # with detection_graph.as_default():
    #     with tf.Session(graph=detection_graph) as sess:
            # Definite input and output Tensors for detection_graph
    '''
    image_tensor = detection_graph.get_tensor_by_name('image_tensor:0')
    # Each box represents a part of the image where a particular object was detected.
    detection_boxes = detection_graph.get_tensor_by_name('detection_boxes:0')
    # Each score represent how level of confidence for each of the objects.
    # Score is shown on the result image, together with the class label.
    detection_scores = detection_graph.get_tensor_by_name('detection_scores:0')
    detection_classes = detection_graph.get_tensor_by_name('detection_classes:0')
    num_detections = detection_graph.get_tensor_by_name('num_detections:0')
    image_np_expanded = np.expand_dims(img_arr, axis=0)
    (boxes, scores, classes, num) = sess.run(
                    [detection_boxes, detection_scores, detection_classes, num_detections],
                    feed_dict={image_tensor: image_np_expanded})
        '''
    img_height = img_arr.shape[0]
    img_width = img_arr.shape[1]

    # convert to blob to pass into model
    img_blob = cv2.dnn.blobFromImage(img_arr, 0.003922, (416, 416), swapRB=True, crop=False)
    #recommended by yolo authors, scale factor is 0.003922=1/255, width,height of blob is 320,320
    #accepted sizes are 320×320,416×416,608×608. More size means more accuracy but less speed

    # set of 80 class labels
    class_labels = ["ladder"]

    #Declare List of colors as an array
    #Green, Blue, Red, cyan, yellow, purple
    #Split based on ',' and for every split, change type to int
    #convert that to a numpy array to apply color mask to the image numpy array
    '''
    class_colors = ["0,255,0","0,0,255","255,0,0","255,255,0","0,255,255"]
    class_colors = [np.array(every_color.split(",")).astype("int") for every_color in class_colors]
    class_colors = np.array(class_colors)
    class_colors = np.tile(class_colors,(16,1))
    '''
    # Loading pretrained model
    # input preprocessed blob into model and pass through the model
    # obtain the detection predictions by the model using forward() method
    yolo_model = load_model()

    # Get all layers from the yolo network
    # Loop and find the last layer (output layer) of the yolo network
    yolo_layers = yolo_model.getLayerNames()
    yolo_output_layer = [yolo_layers[yolo_layer[0] - 1] for yolo_layer in yolo_model.getUnconnectedOutLayers()]

    # input preprocessed blob into model and pass through the model
    yolo_model.setInput(img_blob)
    # obtain the detection layers by forwarding through till the output layer
    obj_detection_layers = yolo_model.forward(yolo_output_layer)


    ############## NMS Change 1 ###############
    # initialization for non-max suppression (NMS)
    # declare list for [class id], [box center, width & height[], [confidences]
    class_ids_list = []
    boxes_list = []
    confidences_list = []
    ############## NMS Change 1 END ###########


    # loop over each of the layer outputs
    for object_detection_layer in obj_detection_layers:
        # loop over the detections
        for object_detection in object_detection_layer:

            # obj_detections[1 to 4] => will have the two center points, box width and box height
            # obj_detections[5] => will have scores for all objects within bounding box
            all_scores = object_detection[5:]
            predicted_class_id = np.argmax(all_scores)
            prediction_confidence = all_scores[predicted_class_id]
            #print('predicted_confidence is',prediction_confidence)
            # take only predictions with confidence more than 50%
            if prediction_confidence > 0.50:

                #obtain the bounding box co-oridnates for actual image from resized image size
                bounding_box = object_detection[0:4] * np.array([img_width, img_height, img_width, img_height])
                (box_center_x_pt, box_center_y_pt, box_width, box_height) = bounding_box.astype("int")
                start_x_pt = int(box_center_x_pt - (box_width / 2))
                start_y_pt = int(box_center_y_pt - (box_height / 2))


                ############## NMS Change 2 ###############
                #save class id, start x, y, width & height, confidences in a list for nms processing
                #make sure to pass confidence as float and width and height as integers
                class_ids_list.append(predicted_class_id)
                confidences_list.append(float(prediction_confidence))
                boxes_list.append([start_x_pt, start_y_pt, int(box_width), int(box_height)])
                ############## NMS Change 2 END ###########

    print('cinfidence list is',confidences_list)
    ############## NMS Change 3 ###############
    # Applying the NMS will return only the selected max value ids while suppressing the non maximum (weak) overlapping bounding boxes
    # Non-Maxima Suppression confidence set as 0.5 & max_suppression threhold for NMS as 0.4 (adjust and try for better perfomance)
    max_value_ids = cv2.dnn.NMSBoxes(boxes_list, confidences_list,conf_thresh, max_suppression_thresh)
    print('what left is',max_value_ids)
    # loop through the final set of detections remaining after NMS and draw bounding box and write text
    results = []
    for max_valueid in max_value_ids:
        max_class_id = max_valueid[0]
        box = boxes_list[max_class_id]
        start_x_pt = box[0]
        start_y_pt = box[1]
        box_width = box[2]
        box_height = box[3]

        #get the predicted class id and label
        predicted_class_id = class_ids_list[max_class_id]
        predicted_class_label = class_labels[predicted_class_id]
        prediction_confidence = confidences_list[max_class_id]
        print('confidece is ',prediction_confidence)
    ############## NMS Change 3 END ###########


        #obtain the bounding box end co-oridnates
        end_x_pt = start_x_pt + box_width
        end_y_pt = start_y_pt + box_height


        results.append({"name": predicted_class_label,#id2name[class_id],
                        "conf": str(prediction_confidence),
                        "bbox": [start_x_pt, start_y_pt,end_x_pt,end_y_pt]
        })


    return {"results":results}

    '''
    height, width, _ = img_arr.shape
    results = []
    for idx, class_id in enumerate(classes[0]):
        conf = scores[0, idx]
        if conf > conf_thresh:
            bbox = boxes[0, idx]
            ymin, xmin, ymax, xmax = bbox[0] * height, bbox[1] * width, bbox[2] * height, bbox[3] * width

            results.append({"name": id2name[class_id],
                            "conf": str(conf),
                            "bbox": [int(xmin), int(ymin), int(xmax), int(ymax)]
            })
    '''
