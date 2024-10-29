# -*- coding: utf-8 -*-
# Desc: 插件构建工具
# former: MainFest/tool.py

from os import makedirs as make_dirs
from os.path import exists as path_exists
from os.path import join as path_join
from os.path import dirname as dir_name
from os.path import basename as base_name
from os.path import split as path_split
from os.path import getsize as path_size
from shutil import move as rename
from shutil import rmtree as remove
from os import listdir
from os import makedirs
from urllib.parse import urlparse
from urllib.parse import urlunparse

from shutil import rmtree as delete
import re
from .utils import TimeStamp
from .utils import CONFIG
from .utils import FindHash
from .fileio import LoadFile
from .fileio import FindFile
from .fileio import save_dict_to_toml
from .fileio import zipDir
from .fileio import unzipFile
from .fileio import DownloadFile
from .fileio import write_json
from .fileio import move_files_to_directory
from .giturl import SerachGit
from .giturl import clone_or_pull_repo as PullRepo
from .giturl import get_url_from_dict

def clear_directory(directory_path):
    """
    清空指定路径的文件夹
    :param directory_path: 文件夹路径
    :return: 无
    """
    delete(directory_path) if path_exists(directory_path) else None
    make_dirs(directory_path) if not path_exists(directory_path) else None

def normalize_and_validate_url(url):
    """
    标准化并验证 URL
    :param url: 原始 URL
    :return: 标准化后的 URL
    """
    parsed_url = urlparse(url)
    if parsed_url.scheme == '' or parsed_url.netloc == '':
        raise ValueError(f"{TimeStamp()} [DOWN] URL '{url}' 不合法")
    return urlunparse(parsed_url)




def normalize_plugin_structure(mainifest:tuple, expand_path:str, exp_path:str):
    """
    标准化插件目录结构
    :param expand_path: 插件目录路径
    :return: 无
    """
    path = dir_name(mainifest[0])
    expand_path = base_name(path)
    expand_path = path_join(CONFIG.expand_path,expand_path)
    # x = move_files_to_directory(path,expand_path)
    # remove(exp_path) if len(path_split(path)) > 2 else None
    return move_files_to_directory(path,expand_path)
    pass


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

def normalize_plugin_info(info:tuple, expand_path:str,dow_url:str):
    """
    标准化插件信息
    :param expand_path: 插件目录路径
    :return: 无
    """
    path = dir_name(info)
    bl_info = LoadFile(info,find='bl_info')
    init_urls = find_urls_in_dict(bl_info)

    if urlparse(dow_url) != 'github.com':
        url = dow_url
    else:
        url = init_urls[0] if init_urls else SerachGit(bl_info['name'],CONFIG.retry)['html_url']
    if not len(bl_info['version']) == 3:
        ins = 3-len(bl_info['version'])
        versions = list(bl_info['version'])
        for i in range(ins):
            versions.append(0)
        version = '.'.join(map(str, (versions)))
    else:
        version = '.'.join(map(str, bl_info['version']))
    out_dict = {
        "schema_version": version if 'version' in bl_info else '1.0.0',
        "id": bl_info['name'].lower().replace(' ','_'),
        "name": bl_info['name'],
        "version": version if 'version' in bl_info else '1.0.0',
        "tagline": bl_info['description'],
        "maintainer": bl_info['author'],
        "type": "add-on",
        "tags" : [bl_info['category']],
        "blender_version_min": '.'.join(map(str, bl_info['blender'])),
        "license" : [ "SPDX:GPL-2.0-or-later",],
        "website" : dow_url if not url else url,
        "copyright" : [ "blender"]
    }
    save_dict_to_toml(out_dict,path_join(path,'blender_manifest.toml'))
    return out_dict

def url_join(*url):
    """
    拼接 URL
    :param url: URL 元组
    :return: 拼接后的 URL
    """
    url_pattern = re.compile(r'https?://[^\s]+')
    out_url = ''
    for i in url:
        url = url_pattern.findall(i)
        if url:
            out_url += url[0]
        else:
            paths = path_split(i)
            for path in paths:
                out_url += '/'+path
    return out_url

def find_value_in_list_of_dicts(list_of_dicts, key, value):
    """
    在列表中的字典中查找某个值
    :param list_of_dicts: 字典列表
    :param key: 要查找的键
    :param value: 要查找的值
    :return: 包含该值的字典
    """
    for d in list_of_dicts:
        if d.get(key) == value:
            return d
    return None

def ConstrucatToml(exp_path: str, url: str) -> dict:
    """
    构建并返回一个包含插件信息的字典。

    参数:
    exp_path (str): 插件的路径。
    url (str): 插件的URL地址。

    返回:
    dict: 包含插件信息的字典。

    功能:
    1. 查找并读取指定路径下的 'blender_manifest.toml' 和 '__init__.py' 文件。
    2. 如果两个文件都存在，调用 `normalize_plugin_structure` 函数进行插件结构规范化。
    3. 如果 'blender_manifest.toml' 文件不存在，调用 `normalize_plugin_structure` 和 `normalize_plugin_info` 函数进行插件结构和信息的规范化。
    4. 最后，加载并返回 'blender_manifest.toml' 文件的内容。
    """
    mainifest = FindFile(exp_path,'blender_manifest.toml')
    initial = FindFile(exp_path,'__init__.py')
    if mainifest and initial:
        normalize_plugin_structure(mainifest,CONFIG.expand_path,exp_path)
    elif not mainifest:
        upexp_path = normalize_plugin_structure(initial,CONFIG.expand_path,exp_path)
        if upexp_path:
            normalize_plugin_info(upexp_path['init'],CONFIG.expand_path,url)
        else:
            normalize_plugin_info(initial[0],CONFIG.expand_path,url)
    return LoadFile(path_join(exp_path,'blender_manifest.toml'))

def ConstrucatJson(data:dict,path:str) -> dict:
    """
    构建包含压缩文件信息的JSON数据。

    参数:
    data (dict): 包含初始数据的字典。
    path (str): 文件路径。

    返回:
    dict: 更新后的数据字典，包含压缩文件的URL、哈希值、大小和网站链接。

    详细说明:
    1. 根据给定的路径创建压缩文件，并生成其URL。
    2. 计算压缩文件的哈希值和大小，并将这些信息添加到数据字典中。
    3. 如果数据字典中没有提供网站链接，则尝试从Git仓库或文件中获取默认链接。
    """
    file = path_join(CONFIG.expand_zip,base_name(path) + '.zip')
    zip_file = zipDir(path,file)
    url = url_join(CONFIG.urlpath,zip_file)
    data['archive_url'] = url
    data['archive_hash'] = FindHash(zip_file)
    data['archive_size'] = path_size(zip_file)
    data['website']  = '' if not 'website' in data else data['website']
    if not data['website']:
        data['website'] = SerachGit(data['id'],config=CONFIG.retry)['html_url']
        data['website'] = LoadFile(path_join(path,'__init__.py'),find='bl_info') if not data['website'] else data['website']
        data['website'] = data['website']['doc_url'] if 'doc_url' in data['website'] else get_url_from_dict(data['id'])
        print(f'{TimeStamp()} [INFO] 未找到网站链接，使用默认链接: {data["website"]}')
    return data

def ConstructApi(api_file:str) -> dict:
    """
    构建 API 文件并更新插件列表。

    此函数处理 CONFIG 对象中定义的插件列表。根据每个插件的类型（'git' 或 URL），获取必要的数据，构建所需的信息，并更新插件列表。最终列表将写入指定的 API 文件。

    参数：
        api_file (str)：要写入更新后的插件列表的 API 文件路径。

    返回：
        dict：包含更新后插件列表的字典。

    步骤：
        1. 初始化一个带有版本的空插件列表。
        2. 遍历 CONFIG.addons 中的每个插件。
        3. 对于 'git' 类型的插件，克隆或拉取仓库并构建必要的信息。
        4. 对于 URL 类型的插件，下载并解压文件，然后构建必要的信息。
        5. 清理临时目录。
        6. 将构建的插件列表写入指定的 API 文件。
        7. 返回更新后的插件列表。

    打印：
        记录插件列表更新过程的开始和完成。
    """
    print(f"{TimeStamp()} [INFO] 开始更新插件列表")
    expand_list = {
    "blocklist":[],
    "data":[],
    "version": "v1"
}
    addons = CONFIG.addons
    for name in addons:
        addon = addons[name]
        if addon['path_type'] == 'git':
            url = SerachGit(name,CONFIG.retry)['html_url'] if not addon['path'] else addon['path']
            exp_path = path_join(CONFIG.expand_path,name)
            repo = PullRepo(url,exp_path)
            toml = ConstrucatToml(exp_path,url) if repo else None
            if toml:
                expand_list['data'].append(ConstrucatJson(toml,exp_path))
        else:
            url = normalize_and_validate_url(addon['path'])
            zip_path = DownloadFile(url,CONFIG.expand_tmp)
            exp_path = unzipFile(zip_path,CONFIG.expand_path) if zip_path else None
            toml = ConstrucatToml(exp_path,url) if exp_path else None
            if toml and exp_path:
                expand_list['data'].append(ConstrucatJson(toml,exp_path))
    clear_directory(CONFIG.expand_tmp)
    write_json(expand_list,api_file)
    print(f"{TimeStamp()} [INFO] 插件列表更新完成")
    return expand_list