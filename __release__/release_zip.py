import hashlib
from os.path import exists
from os.path import getsize
from os.path import splitext
from os.path import basename
from os.path import join
from os import walk
from json import load as json_load
from toml import load as toml_load
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

def load_init():
    with open('init.json','r',encoding='UTF-8') as init_file:
        return json_load(init_file)

def get_info(path):
    # out_dict = {}
    toml_path = path+'\\'+'blender_manifest.toml'
    init = load_init()
    out_dict = toml_load(toml_path)
    out_dict['archive_url'] = "{}__release__/{}.zip".format(init['urlpath'],splitext(basename(path))[0])
    return out_dict

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
        for filename in filenames:
            zip.write(join(path, filename), join(fpath, filename))
    zip.close()

def Release(path):
    info = get_info(path)
    path = out_zip(path)
    info['archive_hash'] = file_hash(path)
    info['archive_size'] = getsize(path)
    return info
 
if __name__ == "__main__":
    path = '.\\expand_data\\Quad_Remesher'
    x = Release(path)