import sys
sys.path.append('..')

import gearman
import json
import time
import traceback


def task_listener_reverse(gearman_worker, gearman_job):
    try:
        s = gearman_job.data
        params_dic = json.loads(s)
        print(params_dic)
        return "ok"
    except Exception as e:
            print(e)
            traceback.print_exc()
            return 'error'


if __name__ == "__main__":
    gm_worker = gearman.GearmanWorker(['localhost:4730'])
    gm_worker.set_client_id('python-worker')
    gm_worker.register_task('MONITOR_TRACKER_SERVER', task_listener_reverse)
    gm_worker.work()