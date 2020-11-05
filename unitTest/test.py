import sys
import copy
sys.path.append('..')
from utils.config_utils import *
import json

if __name__ == '__main__':
    y = yaml_config()
    JZConfig = y.config['jzconfig']
    print(json.dumps(JZConfig))
    config_new = copy.deepcopy(y.config)
    config_new['jzconfig']['camera'][2]['heatMap']['params'] = []
    y.config = config_new
    print(config_new['jzconfig'])
