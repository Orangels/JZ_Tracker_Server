import gearman
import cv2
import json
import sys
import time
import gearman
import traceback
from utils.config_utils import *
from tools.utils import *
import numpy as np
import uuid

UPLOAD_FOLDER = 'static/uploads/'  # 保存文件位置
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

upload_pic_url = 'http://127.0.0.1:5000/tracker_coordinate'

y = yaml_config()

gm_worker = gearman.GearmanWorker(['localhost:4730'])


def random_filename(file):
    file_name, extension_name = os.path.splitext(file)
    random_name = uuid.uuid4().hex
    # random_name = str(random.randint(1, 10000))
    return file_name + random_name + extension_name


def task_listener_reverse(gearman_worker, gearman_job):
    """
    :param gearman_worker:
    :param gearman_job:
    :return:
    """
    try:
        s = gearman_job.data
        dic_json = json.loads(s)
        print(dic_json)
        postMethod(upload_pic_url, dic_json)
        return 'ok'
    except Exception as e:
        print(e)
        traceback.print_exc()
        return 'error'


if __name__ == '__main__':
    print('worker start')
    gm_worker.set_client_id('python-worker')
    gm_worker.register_task('DHP_WSParams', task_listener_reverse)
    gm_worker.work()

