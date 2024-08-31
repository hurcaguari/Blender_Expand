import hashlib
from os.path import exists
from os.path import getsize
from os.path import splitext
from os.path import basename
from os.path import join
from os import walk
from json import load
import zipfile


def str_sha256(text: str = 'UTF-8') -> str:
#    """生成SHA256摘要"""
    return hashlib.sha256(text.encode()).hexdigest()

def file_hash(file_path:str,sha:str = 'sha256') -> str:
    if exists(file_path):
        h = hashlib.new('sha256')
        with open(file_path,'rb') as f:
            while b := f.read(8192):
                h.update(b)
        return '{}:{}'.format(sha,h.hexdigest())
    else:
        print(file_path, '没找到文件')


def get_infos(path):
    out_list = []
    first = 0
    end = 0
    path = path+'\\'+'__init__.py'
    with open(path, 'r',encoding='UTF-8') as f:
        inx = 0
        for line in f.readlines():
            inx += 1
            if line.split('=')[0].strip() == 'bl_info':
                first = inx
            elif line == '}\n':
                if inx > first:
                    out_list.append(line) if first and not end else None
                    return out_list
            out_list.append(line) if first and not end else None

def get_info(path):
    out_dict = {}
    list_text = [line.strip('\n').strip('\r').strip('\t').strip(',') for line in get_infos(path)]
    for line in list_text:
        if not '#' in line:
            if not '=' in line and len(line.split(':')) > 1:
                strdata = line.split(':',1)
                out_dict[eval(strdata[0])] = eval(strdata[1])
    return out_dict

def get_data(path):
    info = get_info(path)
    x = list(info.keys())

    with open('init.json','r',encoding='UTF-8') as init_file:
        init = load(init_file)
    
    return {
        "schema_version":info['schema'] if 'schema' in list(info.keys()) else '1.0.0',
        "version":'.'.join(str(i) for i in info['blender']),
        "tagline":info['description'],
        "archive_url":"{}__release__/{}.zip".format(init['urlpath'],splitext(basename(path))[0]),
        "type":'add-on',
        "blender_version_min":'4.2.0',
        "website":info['doc_url'],
        "maintainer":"xz-blender"
    }

def out_zip(path):
    out_path = r'.\\__release__\\{}'.format(basename(path)+'.zip')
    zipDir(path,out_path)
    return out_path

def zipDir(dirpath, outFullName):
    """
    压缩指定文件夹
    :param dirpath: 目标文件夹路径
    :param outFullName: 压缩文件保存路径+xxxx.zip
    :return: 无
    """
    zip = zipfile.ZipFile(outFullName, "w", zipfile.ZIP_DEFLATED)
    for path, dirnames, filenames in walk(dirpath):
        # 去掉目标跟路径，只对目标文件夹下边的文件及文件夹进行压缩
        fpath = path.replace(dirpath, '') #basename(dirpath)+'\\'+path.replace(dirpath, '')
        pass
        for filename in filenames:
            zip.write(join(path, filename), join(fpath, filename))
    zip.close()

def Release(path):
    info = get_data(path)
    path = out_zip(path)
    return {
            "id": '_'.join(splitext(basename(path))[0].split('_')),
            "schema_version": info['schema_version'],
            "name": ' '.join(splitext(basename(path))[0].split('_')),
            "version": info['version'],
            "tagline": info['tagline'],
            "archive_hash": file_hash(path),
            "archive_size": getsize(path),
            "archive_url": info['archive_url'],
            "type": info['type'],
            "blender_version_min": info['blender_version_min'],
            "website": info['website'],
            "maintainer": info['maintainer'],
            "license": [
                "SPDX:GPL-2.0-or-later"
            ],
            "tags": [
                "3D View"
            ]
        }

 
if __name__ == "__main__":
    path = '.\\expand_data\\Quad_Remesher'
    x = Release(path)