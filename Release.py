from __release__ import Release

from json import dumps

expand_list = {
    "blocklist":[],
    "data":[],
    "version": "v1"
}

def up_expand():
    for i in ['.\\expand_data\\Quad_Remesher','.\\expand_data\\Utilities_Gadget']:
        expand_list['data'].append(Release(i))
        
    with open('expand_list.json','w') as json_file:
        json_file.write(dumps(expand_list))
    pass

if __name__ == "__main__":
    up_expand()