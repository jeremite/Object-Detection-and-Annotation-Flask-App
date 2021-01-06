from flask import Flask, request, jsonify,render_template,session,redirect,url_for
from PIL import Image
import numpy as np
import base64
import io
import os
#import cv2
from backend.yolo_inference import load_model, inference

os.environ['CUDA_VISIBLE_DEVICES'] = '0'

app = Flask(__name__)
app.config['DEBUG']=True
app.config['SECRET_KEY']='secret'
img_arr = np.array([])
#print("cur dir is",os.getcwd())

@app.route('/')
def index():
    num_f = get_newData_cnt()
    return render_template('index.html',num_f=num_f)


@app.route('/api', methods=["GET","POST"])
def main_interface():
    response = request.get_json()
    print('data is',request.files)
    data_str = response['image']
    point = data_str.find(',')
    base64_str = data_str[point:]  # remove unused part like this: "data:image/jpeg;base64,"

    image = base64.b64decode(base64_str)
    img = Image.open(io.BytesIO(image))
    print('img',img)
    if(img.mode!='RGB'):
        img = img.convert("RGB")

    # convert to numpy array.
    global img_arr
    img_arr = np.array(img)

    #session['img_arr'] = img_arr

    print("shapre is ",img_arr.shape)
    # do object detection in inference function.
    results = inference(img_arr, conf_thresh=0.5, max_suppression_thresh=0.4)

    is_ladder=1
    if not results['results']:
        is_ladder=0
    results['is_ladder']=is_ladder
    print(results)
    return jsonify(results)

@app.route('/save', methods=["POST"])
def save():
    response = request.get_json()
    coordinates = response['coordinates']
    filename = response['filename']
    w = response['width']
    h = response['height']
    print('coordinates',coordinates)
    # save the coor and image
    write_new_data(filename,coordinates,w,h)
    # caculate new data number
    num_f = get_newData_cnt()
    print('num_f new is ',num_f)
    return jsonify({"num_f":num_f})

def write_new_data(filename,co,w,h):
    path = "backend/model_config/ladder/images/"
    im = Image.fromarray(img_arr)
    im.save(os.path.join(path,filename))
    #cv2.imwrite(os.path.join(path,filename), img_arr)
    new_cor = []
    for c in co:
        x,y,wi,he = c
        x = (x+wi/2.)/w
        y = (y+he/2.)/h
        wi = wi/w
        he = he/h
        new_cor.append([0,x,y,wi,he])
    with open(os.path.join(path,filename.split(".")[0]+'.txt'), "w") as result:
        result.write("\n".join([' '.join(map(str, item)) for item in new_cor]))

def get_newData_cnt(): return int(len(next(os.walk("backend/model_config/ladder/images/"))[2])/2)

@app.after_request
def add_headers(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    return response


if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5000)
