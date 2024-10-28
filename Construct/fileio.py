# -*- coding: utf-8 -*-
# Desc: 从文件中加载数据
# former: MainFest/fileio.py

from toml import load as toml_load
from toml import dump as toml_dump
from toml import TomlDecodeError
from json import load as json_load
from json import dump as json_dump
from json import JSONDecodeError
from ast import parse as ast_parse
from ast import walk as ast_walk
from ast import Assign as ast_Assign
from ast import Name as ast_Name
from ast import literal_eval as ast_literal_eval
from ast import FunctionDef as ast_FunctionDef

from os import makedirs as make_dirs
from os.path import normpath
from os.path import exists as path_exists
from os.path import join as path_join
from os.path import basename as base_name
from os.path import splitext as path_name
from os.path import splitext as path_splitext
from os import walk as os_walk
from os import path as os_path
from os import makedirs
from os import walk

from requests import get as get_request
from requests.exceptions import ConnectionError
from shutil import rmtree as delete
import zipfile
from .utils import TimeStamp
from .utils import CONFIG

def load_toml_to_dict(file_path) -> dict:
    """
    读取 TOML 文件并将其内容加载到字典中
    :param file_path: TOML 文件路径
    :return: 包含 TOML 文件内容的字典
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = toml_load(file)
        return data
    except FileNotFoundError:
        print(f"{TimeStamp} [ERRO] 文件丢失: {file_path}")
        return {}
    except TomlDecodeError as e:
        print(f"{TimeStamp} [INFO] 解码错误: {e}")
        return {}

def load_json_to_dict(file_path:str,find:str = None) -> dict:
    """
    读取 JSON 文件并将其内容加载到字典中
    :param file_path: JSON 文件路径
    :return: 包含 JSON 文件内容的字典
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json_load(file)
        return data[find] if find in data else data
    except FileNotFoundError:
        print(f"{TimeStamp()} [ERRO] 文件丢失: {file_path}")
        return {}
    except JSONDecodeError as e:
        print(f"{TimeStamp()} [INFO] 解码错误: {e}")
        return {}

def load_py_to_dict(file_path, load_function=False, find = None) -> dict:
    """
    读取 Python 文件并将其内容加载到字典中，但不执行其中代码
    :param file_path: Python 文件路径
    :return: 包含 Python 文件内容的字典
    """
    result = {}
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            tree = ast_parse(file.read(), filename=file_path)
            for node in ast_walk(tree):
                if isinstance(node, ast_Assign):
                    for target in node.targets:
                        if isinstance(target, ast_Name):
                            try:
                                result[target.id] = ast_literal_eval(node.value)
                            except (ValueError, SyntaxError) as e:
                                print(f"{TimeStamp()} [ERRO] 无法解析的变量名: {target.id}, 错误: {e}") if load_function else None
                elif isinstance(node, ast_FunctionDef):
                    result[node.name] = 'function'
        return GetInfo(result,find) if find else result
    except FileNotFoundError:
        print(f"{TimeStamp()} [ERRO] 文件丢失: {file_path}")
        return {}
    except SyntaxError as e:
        print(f"{TimeStamp()} [INFO] 语法错误: {e}")
        return {}

def save_dict_to_toml(data: dict, file_path: str):
    """
    将字典保存到 TOML 文件
    :param data: 要保存的字典
    :param file_path: TOML 文件路径
    :return: 无
    """
    make_dirs(os_path.dirname(file_path)) if not path_exists(os_path.dirname(file_path)) else None
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            toml_dump(data, file)
        print(f"{TimeStamp()} [INFO] 文件更新: {file_path}")
    except Exception as e:
        print(f"{TimeStamp()} [ERRO] 更新错误: {file_path}, 错误: {e}")

def GetInfo(data,find) -> dict:
    """
    搜索字典中的键值对
    :param data: 字典
    :param find: 要查找的键
    :return: 包含查找结果的字典
    """
    return data[find] if find in data else {}




def FindFile(directory: str, filename: str) -> list:
    """
    在指定目录中查找文件并返回匹配文件的路径列表。

    参数:
    directory (str): 要搜索的目录路径。
    filename (str): 要查找的文件名。

    返回:
    list: 包含匹配文件完整路径的列表。

    示例:
    >>> FindFile('/path/to/directory', 'example.txt')
    ['/path/to/directory/subdir/example.txt', '/path/to/directory/anotherdir/example.txt']
    """
    matches = []
    for root, _, files in os_walk(directory):
        if filename in files:
            matches.append(os_path.join(root, filename))
    return matches

def LoadFile(file_path: str, load_function: bool=False, find: str=None) -> dict:
    """
    加载指定路径的文件，并根据文件类型返回相应的字典格式数据。

    参数:
    file_path (str): 文件的路径。
    load_function (bool, 可选): 是否加载 Python 文件中的函数。默认为 False。
    find (str, 可选): 在 JSON 文件中查找的特定键。默认为 None。

    返回:
    dict: 根据文件类型返回相应的字典格式数据。

    文件类型支持:
    - toml: 使用 load_toml_to_dict 函数加载
    - json: 使用 load_json_to_dict 函数加载
    - py: 使用 load_py_to_dict 函数加载
    """
    type = path_splitext(file_path)[1][1:]
    if type == 'toml':
        return load_toml_to_dict(file_path)
    elif type == 'json':
        return load_json_to_dict(file_path,find)
    elif type == 'py':
        return load_py_to_dict(file_path,load_function,find)

def unzipFile(zip_path, dest_folder):
    """
    解压缩指定文件到指定文件夹
    :param zip_path: zip文件路径
    :param dest_folder: 目标文件夹路径
    :return: 无
    """

    makedirs(dest_folder) if not path_exists(dest_folder) else None
    try:
        with zipfile.ZipFile(normpath(zip_path), 'r') as zip_ref:
            # 提取根目录的名字
            root_dirs = set()
            for file in zip_ref.namelist():
                root_dir = file.split('/')[0]
                if root_dir:
                    root_dirs.add(root_dir)
            if '__init__.py' in root_dirs:
                zip_name = base_name(path_name(zip_path)[0])
                dest_folder = path_join(dest_folder,zip_name)
                zip_ref.extractall(dest_folder)
                print(f"{TimeStamp()} [UZIP] 解压文件: {zip_path} 到 {dest_folder}")
                return path_join(dest_folder)
            else:
                zip_ref.extractall(dest_folder)
                print(f"{TimeStamp()} [UZIP] 解压文件: {zip_path} 到 {dest_folder}")
    except zipfile.BadZipFile as e:
        print(f"{TimeStamp()} [ERRO] 解压失败: {zip_path} 到 {dest_folder}")
        return None
    return path_join(dest_folder,root_dir)

def zipDir(dirpath, outFullName):
    """
    压缩指定文件夹
    :param dirpath: 目标文件夹路径
    :param outFullName: 压缩文件保存路径+xxxx.zip
    :return: 无
    """

    make_dirs(os_path.dirname(outFullName)) if not path_exists(os_path.dirname(outFullName)) else None


    zip = zipfile.ZipFile(outFullName, "w", zipfile.ZIP_DEFLATED)
    for path, dirnames, filenames in walk(dirpath):
        # 去掉目标跟路径，只对目标文件夹下边的文件及文件夹进行压缩
        fpath = path.replace(dirpath, '') #basename(dirpath)+'\\'+path.replace(dirpath, '')
        for filename in filenames:
            zip.write(path_join(path, filename), path_join(fpath, filename))
    zip.close()
    print(f"{TimeStamp()} [UZIP] 压缩文件: {dirpath} 到 {outFullName}")
    return outFullName

def DownloadFile(url, dest_folder):
    """
    下载文件到指定文件夹。

    参数:
    url (str): 要下载文件的URL。
    dest_folder (str): 文件保存的目标文件夹路径。

    返回:
    str: 下载文件的完整路径，如果下载失败则返回None。

    功能:
    1. 检查目标文件夹是否存在，如果不存在则创建。
    2. 尝试从给定的URL下载文件。
    3. 如果下载成功，将文件保存到目标文件夹中。
    4. 如果下载失败，打印错误信息并返回None。

    异常处理:
    - 如果在请求过程中发生连接错误，捕获ConnectionError并打印错误信息。
    - 如果HTTP响应状态码不是200，打印错误信息。

    示例:
    >>> DownloadFile("http://example.com/file.zip", "/path/to/destination")
    """
    if not path_exists(dest_folder):
        make_dirs(dest_folder)
    try:
        response = get_request(url, stream=True)
    except ConnectionError as e:
        print(f"{TimeStamp()} [ERRO] 下载失败: {url} {e}")
        return None
    if response.status_code == 200:
        file_name = path_join(dest_folder, url.split('/')[-1])
        with open(file_name, 'wb') as file:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    file.write(chunk)
        print(f"{TimeStamp()} [DOWN] 下载文件: {url.split('/')[-1]} 到 {file_name}")
    else:
        print(f"{TimeStamp()} [ERRO] 下载失败: {url}")
    return file_name

def write_json(data:dict, file_path:str):
    """
    将字典保存到 JSON 文件
    :param data: 要保存的字典
    :param file_path: JSON 文件路径
    :return: 无
    """
    make_dirs(os_path.dirname(file_path)) if not path_exists(os_path.dirname(file_path)) else None
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            json_dump(data, file, ensure_ascii=False, indent=4)
        print(f"{TimeStamp()} [INFO] 文件更新: {file_path}")
    except Exception as e:
        print(f"{TimeStamp()} [ERRO] 更新错误: {file_path}, 错误: {e}")