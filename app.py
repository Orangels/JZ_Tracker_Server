from flask import Flask, jsonify, request, send_file, send_from_directory, render_template
from flask_socketio import SocketIO, emit
from flask_cors import CORS

from model.tables import *
from model.db import db_eng

import base64
import time
from os import popen
from urllib.parse import unquote
import sys
import cv2

import os
import json
from werkzeug.routing import BaseConverter
import random
import traceback
from tools.utils import *
from utils.config_utils import *
import copy
from tools.gearmanClient import client


class RegexConverter(BaseConverter):
    def __init__(self, map, *args):
        self.map = map
        self.regex = args[0]


BASE_DIR = os.path.dirname(os.path.abspath(__file__))


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads/'  # 保存文件位置
app.url_map.converters['regex'] = RegexConverter
app.debug = False
app.config['SECRET_KEY'] = 'DPHTracker'

app.config['MONGODB_SETTINGS'] = {
	'db': 'Face_lib',
	'host': '127.0.0.1',
	'port': 27017,
    'connect':False
}


socketio = SocketIO(app, cors_allowed_origins="*")
CORS(app, resources=r'/*')


with app.app_context():
    db_eng.init_app(app)


@app.route('/')
@app.route('/mode_1')
@app.route('/mode_2')
@app.route('/login')
@app.route('/real_time_show')
@app.route('/draw')
def index():
    # return 111
    return render_template("index.html")


@app.route('/test', methods=['POST'])
def test():
    dic = dict(code=200, result=dict(time=int(time.time()*1000)))
    return jsonify(dic)

@app.route('/cameraPersons', methods=['POST'])
def get_camera_persons():
    try:
        path_0 = '/home/user/workspace/project/ls-dev/TrackerEngineServer/camera_0.txt'
        path_1 = '/home/user/workspace/project/ls-dev/TrackerEngineServer/camera_1.txt'
        path_2 = '/home/user/workspace/project/ls-dev/TrackerEngineServer/camera_2.txt'

        path_list = [path_0, path_1, path_2]

        heatmap, entry, hesitate = 0, 0, 0
        hes_total_times = []
        list0 = []

        for j in range(len(path_list)):
            with open(path_list[j]) as f:
                list0 = f.readlines()
                for i in range(0, len(list0)):
                    list0[i] = int(list0[i].rstrip('\n'))
                    if list0[i] == -1:
                        list0[i] = 0
                    if i > 2:
                        hes_total_times.append(list0[i])
                heatmap += list0[0]
                if j == 1:
                    entry += list0[1]
                hesitate += list0[2]
        dic = dict(code=200, result=dict(heatmap=heatmap, entry=entry, hesitate=hesitate, hes_total_times=hes_total_times))
        return jsonify(dic)
    except Exception as e:
        print('***********')
        print(e)
        traceback.print_exc()
        print('***********')
        dic = dict(code=400, result='error')
        return jsonify(dic)


@app.route('/cameraImgs', methods=['POST'])
def get_camera_imgs():
    try:
        file_list = []
        for i in range(3):
            file_list_name_0 = get_filepath_from_dirs(BASE_DIR + "/static/cameraImgs/{}_camera/".format(i), mode=1)
            file_list_0 = []
            for file in file_list_name_0:
                file_list_0.append("/static/cameraImgs/{}_camera/".format(i)+file)
            file_list_0.sort(reverse=True)
            file_list.append(file_list_0[0])
        dic = dict(code=200, result=file_list)
        return jsonify(dic)
    except Exception as e:
        print('***********')
        print(e)
        traceback.print_exc()
        print('***********')
        dic = dict(code=400, result='error')
        return jsonify(dic)


@app.route('/get_remote_config', methods=['POST'])
def get_remote_config():
    try:
        y = yaml_config().config['jzconfig']
        dic = dict(code=200, result=y)
        return jsonify(dic)
    except Exception as e:
        print('***********')
        print(e)
        traceback.print_exc()
        print('***********')
        dic = dict(code=400, result='error')
        return jsonify(dic)


@app.route('/change_remote_config', methods=['POST'])
def change_remote_config():
    try:
        y = yaml_config()
        data = request.json
        print(data)
        config_new = copy.deepcopy(y.config)
        config_new['jzconfig'] = data
        y.config = config_new
        client("MONITOR_TRACKER_SERVER", dict(updateConfig=True, timestamp=time.time()))
        dic = dict(code=200, result=y.config['jzconfig'])
        return jsonify(dic)
    except Exception as e:
        print('***********')
        print(e)
        traceback.print_exc()
        print('***********')
        dic = dict(code=400, result='error')
        return jsonify(dic)


@app.route('/waring_img', methods=['POST'])
def post_new_waring_img():
    try:
        data = unquote(request.data.decode(), 'utf-8')
        client_params = json.loads(data)['persons']
        # print(client_params)
        time.sleep(6)
        socketio.emit('new_state', {
            'result': client_params
        },
                      namespace='/Camera_Web_ws')
        dic = dict(code=200, result='error')
        return jsonify(dic)
    except Exception as e:
        print('***********')
        print(e)
        traceback.print_exc()
        print('***********')
        dic = dict(code=400, result='error')
        return jsonify(dic)


@app.route('/tracker_coordinate', methods=['POST'])
def tracker_coordinate():
    try:
        data = unquote(request.data.decode(), 'utf-8')
        client_params = json.loads(data)
        socketio.emit('new_coor', {
            'result': client_params
        },
                      namespace='/Camera_Web_ws')
        dic = dict(code=200, result='error')
        return jsonify(dic)
    except Exception as e:
        print('***********')
        print(e)
        traceback.print_exc()
        print('***********')
        dic = dict(code=400, result='error')
        return jsonify(dic)


@app.route('/device_info', methods=['POST'])
def device_info():
    try:
        dic = dict(code=200, result=get_device_basic_info())
        return jsonify(dic)
    except Exception as e:
        print('***********')
        print(e)
        traceback.print_exc()
        print('***********')
        dic = dict(code=400, result='error')
        return jsonify(dic)


@app.route('/get_rtmp_url', methods=['POST'])
def get_rtmp_url():
    try:
        y = yaml_config()
        rtmpUrls = y.config['rtmpUrl']
        dic = dict(code=200, result=rtmpUrls)
        return jsonify(dic)
    except Exception as e:
        print('***********')
        print(e)
        traceback.print_exc()
        print('***********')
        dic = dict(code=400, result='error')
        return jsonify(dic)


@app.route('/add_rtmp_url', methods=['POST'])
def add_rtmp_url():
    try:
        data = request.json
        rtmp_url_new = data['url']
        rtmp_url_new = "http://{}/hls/room.m3u8".format(rtmp_url_new)
        y = yaml_config()
        rtmpUrls = y.config['rtmpUrl']
        if rtmp_url_new in rtmpUrls['url']:
            dic = dict(code=400, result=rtmpUrls, message="已存在")
            return jsonify(dic)
        else:
            rtmpUrls['url'].append(rtmp_url_new)
            y.config = dict(rtmpUrl=rtmpUrls)
        dic = dict(code=200, result=rtmpUrls)
        return jsonify(dic)
    except Exception as e:
        print('***********')
        print(e)
        traceback.print_exc()
        print('***********')
        dic = dict(code=400, result='error')
        return jsonify(dic)


@app.route('/del_rtmp_url', methods=['POST'])
def del_rtmp_url():
    try:
        data = request.json
        rtmp_url_new = data['url']
        y = yaml_config()
        rtmpUrls = y.config['rtmpUrl']
        if rtmp_url_new in rtmpUrls['url']:
            rtmpUrls['url'].remove(rtmp_url_new)
            y.config = dict(rtmpUrl=rtmpUrls)
        else:
            dic = dict(code=400, result=rtmpUrls, message="不存在")
            return jsonify(dic)
        dic = dict(code=200, result=rtmpUrls)
        return jsonify(dic)
    except Exception as e:
        print('***********')
        print(e)
        traceback.print_exc()
        print('***********')
        dic = dict(code=400, result='error')
        return jsonify(dic)


# config api
@app.route('/all_persons', methods=['POST'])
def all_persons():
    try:
        persons = Person.objects.all()
        persons = list(map(lambda x: m2d_exclude(x, '_id', "feature"), persons))
        return jsonify(error_code=0, status=200, err_msg=persons)
    except Exception as e:
        print('***********')
        print(e)
        traceback.print_exc()
        print('***********')
        dic = dict(code=400, result='error')
        return jsonify(dic)


@app.route('/add_person', methods=['POST'])
def add_person():
    try:
        data = request.json
        if data['img_addr']:
            img_base64 = is_base64_code(data['img_addr'])
            if img_base64:
                imagedata = base64.b64decode(img_base64)
                img_path = img_pat(BASE_DIR + "/static/uploadIcon")
                with open(img_path, 'wb') as f:
                    f.write(imagedata)
                data['img_addr'] = '/static/upload/' + img_path.split('/')[-1]
            else:
                return jsonify(error_code=1, status=400, err_msg='base64 coding error')
        persons = Person.objects.all()
        persons = list(map(lambda x: m2d_exclude(x, '_id', "feature"), persons))
        return jsonify(error_code=0, status=200, err_msg=persons)
    except Exception as e:
        print('***********')
        print(e)
        traceback.print_exc()
        print('***********')
        dic = dict(code=400, result='error')
        return jsonify(dic)


@app.route('/upload_tmp', methods=['POST'])
def upload_tmp():
    try:
        print("22")
        f = request.files['file']
        return '200'
    except Exception as e:
        print('***********')
        print(e)
        traceback.print_exc()
        print('***********')
        return jsonify(error_code=1, status=400, err_msg=e)


@socketio.on('test_message', namespace='/Camera_Web_ws')
def test_message(message):
    print(message)
    emit('my response', {'data': message['data']})


@socketio.on('my broadcast event', namespace='/Camera_Web_ws')
def test_message(message):
    print('my broadcast event')
    emit('my response', {'data': message['data']}, broadcast=True)


@socketio.on('connect', namespace='/Camera_Web_ws')
def test_connect():
    print('Web connected')


@socketio.on('disconnect', namespace='/Camera_Web_ws')
def test_disconnect():
    print('Web disconnected')


if __name__ == '__main__':
    # app.run(host='0.0.0.0', port=5000, debug=True)
    socketio.run(app, host='0.0.0.0', port=5000)
