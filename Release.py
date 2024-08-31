from __release__ import RELEASE
from __release__ import LOAD_INIT

from json import dumps
import os


def up_expand():
    expand_list = {
    "blocklist":[],
    "data":[],
    "version": "v1"
}
    expand_files = os.listdir(LOAD_INIT()['expand_path'])
    expand_files = [LOAD_INIT()['expand_path']+i for i in expand_files]
    print('更新插件列表 {}'.format(expand_files))
    expand_list['data'] = [RELEASE(i) for i in expand_files]

    with open('expand_list.json','w') as json_file:
        json_file.write(dumps(expand_list))
    return expand_list

if __name__ == "__main__":
    up_expand()