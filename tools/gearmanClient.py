import sys
sys.path.append('..')

import gearman
import json
import time


def client(flag, params):
    gm_client = gearman.GearmanClient(['127.0.0.1:4730'])
    result = gm_client.submit_job(flag, json.dumps(obj=params))
    # print(result.result)
    s = result.result
    print(s)
    return s


if __name__ == "__main__":
    client("MONITOR_TRACKER_SERVER", dict(updateConfig=True, timestamp=time.time()))