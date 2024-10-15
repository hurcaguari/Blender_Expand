import hashlib
from os.path import exists
from os.path import getsize
from os.path import splitext
from os.path import basename
from os.path import join
from os import walk
from json import load as json_load
from toml import load as toml_load
from toml import dump as toml_dump
from .git_url import serach_git
import re
import ast
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

def out_toml(out_dict, file_path):
    with open(file_path, 'w', encoding='utf-8') as file:
        toml_dump(out_dict, file)
    return out_dict

def get_variable_from_file(file_path, variable_name):
    with open(file_path, 'r', encoding='utf-8') as file:
        file_content = file.read()
    
    # 解析文件内容为 AST
    tree = ast.parse(file_content, filename=file_path)
    
    for node in ast.walk(tree):
        # 查找变量赋值语句
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == variable_name:
                    # 使用 eval 安全地计算变量值
                    return eval(compile(ast.Expression(node.value), filename="", mode="eval"))

    raise ValueError(f"Variable '{variable_name}' not found in {file_path}")

def find_urls_in_dict(data):
    """
    遍历字典中的所有值并查找 URL
    :param data: 输入字典
    :return: 包含所有 URL 的列表
    """
    urls = []
    url_pattern = re.compile(r'https?://[^\s]+')

    def _find_urls(value):
        if isinstance(value, dict):
            for v in value.values():
                _find_urls(v)
        elif isinstance(value, list):
            for item in value:
                _find_urls(item)
        elif isinstance(value, str):
            matches = url_pattern.findall(value)
            urls.extend(matches)

    _find_urls(data)
    return urls

def construct_toml(toml_path,path):
    bl_info = get_variable_from_file(path+'\\__init__.py','bl_info')
    urls = find_urls_in_dict(bl_info)
    out_dict = {
        "schema_version": '.'.join(map(str, bl_info['version'])),
        "id": bl_info['name'].lower().replace(' ','_'),
        "name": bl_info['name'],
        "version": '.'.join(map(str, bl_info['version'])),
        "tagline": bl_info['description'],
        "maintainers": bl_info['author'],
        "type": "add-on",
        "tags" : [bl_info['category']],
        "blender_version_min": '.'.join(map(str, bl_info['blender'])),
        "license" : [ "SPDX:GPL-2.0-or-later",],
        "website" : find_urls_in_dict(bl_info)[0] if urls else serach_git(bl_info['name'])['html_url'],
        "copyright" : [ "blender"]
    }
    return out_toml(out_dict,toml_path)

def get_info(path):
    # out_dict = {}
    toml_path = path+'\\'+'blender_manifest.toml'
    init = load_init()

    if exists(toml_path):
        out_dict = toml_load(toml_path)
    else:
        out_dict = construct_toml(toml_path,path)
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