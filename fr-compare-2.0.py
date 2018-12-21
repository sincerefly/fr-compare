# -*- coding: utf-8 -*-

from flask import Flask, request, jsonify, make_response, current_app
from functools import update_wrapper
from gevent.pywsgi import WSGIServer
from datetime import timedelta
import face_recognition
from io import BytesIO
from PIL import Image
import numpy as np
import requests
import base64
import time
import json

#
# 监听 :8726/detect(POST) 接口使用 face_recognition 裁剪人脸
# 监听 :8726/compare(POST) 接口使用保存传递过来的Base64图片到本地, 进行人证比对
#

app = Flask(__name__)

def after_request(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET,POST,OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
    return response

app.after_request(after_request)


def crossdomain(origin=None, methods=None, headers=None,
                max_age=21600, attach_to_all=True,
                automatic_options=True):
    if methods is not None:
        methods = ', '.join(sorted(x.upper() for x in methods))
    if headers is not None and not isinstance(headers, basestring):
        headers = ', '.join(x.upper() for x in headers)
    if not isinstance(origin, basestring):
        origin = ', '.join(origin)
    if isinstance(max_age, timedelta):
        max_age = max_age.total_seconds()

    def get_methods():
        if methods is not None:
            return methods

        options_resp = current_app.make_default_options_response()
        return options_resp.headers['allow']

    def decorator(f):
        def wrapped_function(*args, **kwargs):
            if automatic_options and request.method == 'OPTIONS':
                resp = current_app.make_default_options_response()
            else:
                resp = make_response(f(*args, **kwargs))
            if not attach_to_all and request.method != 'OPTIONS':
                return resp

            h = resp.headers

            h['Access-Control-Allow-Origin'] = origin
            h['Access-Control-Allow-Methods'] = get_methods()
            h['Access-Control-Max-Age'] = str(max_age)
            if headers is not None:
                h['Access-Control-Allow-Headers'] = headers
            else:
                h['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
            return resp

        f.provide_automatic_options = False
        return update_wrapper(wrapped_function, f)
    return decorator


def detect_it(b64_image):
    '''
    使用 face_recognition 截取头像
    '''

    #image = face_recognition.load_image_file("origin.png")
    bytes_img = BytesIO(base64.b64decode(b64_image))

    im = Image.open(bytes_img)
    width, height = im.size


    image = face_recognition.load_image_file(bytes_img)

    face_locations = face_recognition.face_locations(image)

    print("I found {} face(s) in this photograph.".format(len(face_locations)))

    if len(face_locations) == 0:
        return ""

    face_size = 0
    face = (0, 0, 0, 0)
    for face_location in face_locations:

        # Print the location of each face in this image
        top, right, bottom, left = face_location
        print("A face is located at pixel location Top: {}, Left: {}, Bottom: {}, Right: {}".format(top, left, bottom, right))

        if (bottom - top) * (right - left) > face_size:
            face = (top, right, bottom, left)
            face_size = (bottom - top) * (right - left)

    top, right, bottom, left = face

    top = top - 60 if top > 60 else 0
    right = right + 40 if width > right + 40 else width
    bottom = bottom + 60 if height > bottom + 60 else height
    left = left - 40 if left > 40 else 0
    # face_image = image[top-60:bottom+60, left-40:right+40]
    face_image = image[top:bottom, left:right]

    pil_image = Image.fromarray(face_image)
    buffer = BytesIO()
    pil_image.save(buffer, format="JPEG")

    encoded_string = base64.b64encode(buffer.getvalue())
    return encoded_string


def compare_face(b64_image_01, b64_image_02):

    bytes_img_01 = BytesIO(base64.b64decode(b64_image_01))
    bytes_img_02 = BytesIO(base64.b64decode(b64_image_02))

    known_image = face_recognition.load_image_file(bytes_img_01)
    unknown_image = face_recognition.load_image_file(bytes_img_02)

    known_encoding = face_recognition.face_encodings(known_image)[0]
    unknown_encoding = face_recognition.face_encodings(unknown_image)[0]

    distance = face_recognition.face_distance([known_encoding], unknown_encoding)
    return distance


@app.route('/detect', methods=['GET', 'POST', 'OPTIONS'])
@crossdomain(origin='*')
def detect():
    if request.method == 'POST':

        try:
            resp_data = request.get_json()
            # print(resp_data['b64_image'])
        except Exception as err:
            data = { "b64_image": "", "message": "please post data with json encode string and setting json header" }
            return jsonify(data)
        if not resp_data.has_key("b64_image"):
            return jsonify({ "b64_image": "", "message": "'b64_image' argument not found" })
        try:
            photo = detect_it(resp_data['b64_image'])

        except Exception as err:
            print(err)
            data = { "b64_image": "", "message": "server error" }
        else:
            if photo:
                data = { "b64_image": photo, "message": "success" }
            else:
                data = { "b64_image": "", "message": "face not found" }
        finally:
            resp = make_response(jsonify(data))

            return resp

    else:
        return '''请使用Post方式传递数据<br><br>
                  请求头<br>
                  'Content-Type': 'application/json'
                  <br><br>
                  请求体<br>
                  {<br>
                  &nbsp;&nbsp;"b64_image": "/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAIBAQEBAQIBAQEC..."<br>
                  }<br>
                  <br>
                  回复内容<br>
                  {<br>
                  &nbsp;&nbsp;"b64_image": "/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAIBAQEBAQIBAQEC...", "message": "success" <br>
                  }<br>
                  <br>
                  返回的 b64_image 为裁剪后的头像数据, message 为 "succcess" 时为截取头像成功, 否则为报错信息, b64_image 为空字符串
               '''


@app.route('/compare', methods=['GET', 'POST', 'OPTIONS'])
@crossdomain(origin='*')
def compare():
    t1 = time.time()

    if request.method == 'POST':
        json_data = request.get_json()
        # print(json_data)
        b64_image_01 = json_data['b64_image_01']
        b64_image_02 = json_data['b64_image_02']

        try:
            distance = compare_face(b64_image_01, b64_image_02)
        except IndexError as err:
            t2 = time.time()
            use_time = str(round(t2-t1, 2)) + 's'
            return jsonify({ "message": "face not found", "distance": "0.0", "use_time": use_time})
        except Exception as err:
            print(err)
            t2 = time.time()
            use_time = str(round(t2-t1, 2)) + 's'
            return jsonify({ "message": "unknow error", "distance": "0.0", "use_time": use_time})

        distance_string = str(round((1-distance[0]) * 100, 2))
        print(json.dumps({ "message": "ok", "distance": distance_string}))
        t2 = time.time()
        use_time = str(round(t2-t1, 2)) + 's'
        resp = make_response(jsonify({ "message": "ok", "distance": distance_string, "use_time": use_time}))
        return resp

    else:
        return '''请使用Post方式传递数据<br><br>'''


@app.route('/', methods=['GET'])
@crossdomain(origin='*')
def welcome():
    return jsonify({ "message": "face_recognition server 2.0", "code": 200 })


if __name__ == '__main__':

    http_server = WSGIServer(('0.0.0.0', 8726), app)
    print("* Detect or Compare with Fr_py, Server 2.0")
    print("* Running on http://0.0.0.0:8726/detect")
    print("* Running on http://0.0.0.0:8726/compare (Press CTRL+C to quit)")
    http_server.serve_forever()

