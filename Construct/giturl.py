# -*- coding: utf-8 -*-
# Desc: 从GitHub搜索Blender插件的URL
# former: MainFest/giturl.py

import requests
from time import sleep
from .utils import TimeStamp
from .fileio import FindFile
from urllib.parse import urlparse
from os.path import exists
from os import listdir
import subprocess

def clone_specific_directory(repo_url, dest_path, directory, branch = None):
    """
    克隆仓库中特定目录
    :param repo_url: 仓库 URL
    :param branch: 分支名称
    :param directory: 要拉取的目录
    :param dest_path: 目标路径
    :return: 无
    """
    
    branch = branch if branch else 'main'
    # 克隆仓库但不检出文件
    run_git_command(['git', 'clone', '--no-checkout', '--depth', '1', '--branch', branch, repo_url, dest_path])
    
    # 配置 sparse-checkout
    run_git_command(['git', 'sparse-checkout', 'init', '--cone'], cwd=dest_path)
    run_git_command(['git', 'sparse-checkout', 'set', directory], cwd=dest_path)
    
    # 检出指定目录
    run_git_command(['git', 'checkout'], cwd=dest_path)
    return FindFile(dest_path,'__init__.py')

def clone_or_pull_repo(repo_url, repo_path):
    """
    拉取或克隆存储库
    :param repo_url: 存储库 URL
    :param repo_path: 存储库路径
    :return: __init__.py 文件是否存在并且返回文件 LIST
    """
    repo_url = urlparse(repo_url).geturl()
    if exists(repo_path):
        if listdir(repo_path):
            # 如果目录存在且非空，则执行 pull 操作
            print(f"{TimeStamp()} [GITS] 拉取最新: {repo_url}")
            run_git_command(["git", "-C", repo_path, "pull"])
        else:
            # 如果目录存在但为空，则执行 clone 操作
            print(f"{TimeStamp()} [GITS] 克隆仓库: {repo_url}")
            run_git_command(["git", "clone", repo_url, repo_path])
    else:
        # 如果目录不存在，则执行 clone 操作
        # makedirs(repo_path)
        print(f"{TimeStamp()} [GITS] 克隆仓库: {repo_url}")
        run_git_command(["git", "clone", repo_url, repo_path])
    return FindFile(repo_path,'__init__.py')

def remove_newlines(text):
    """
    删除文本中的换行符
    :param text: 要处理的文本
    :return: 删除换行符后的文本
    """
    return text.replace('\n', '').replace('\r', '')

def search_github_repositories(repo_name, per_page=10, page=1,config=None):
    """
    根据存储库名称在 GitHub 上搜索公开存储库
    :param repo_name: 存储库名称
    :param per_page: 每页显示的结果数量
    :param page: 页码
    :return: 搜索结果的 JSON 数据
    """
    config['retry_ints'] -= 1
    if config['retry_ints'] < 0:
        return {
            'name' : repo_name,
            'html_url' : "",
            'full_name' : ""
        }
    url = "https://api.github.com/search/repositories"
    params = {
        "q": repo_name,
        "per_page": per_page,
        "page": page
    }
    try:
        print(f'{TimeStamp()} [GITS] 仓库搜索:',url,params,config)
        response = requests.get(url, params=params)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"{TimeStamp()} [ERRO] 搜索错误: {e}")
        sleep(config['retry_interval'])
        return search_github_repositories(repo_name, per_page=10, page=1,config=config)
    return response.json()

def get_url_from_dict(name):
    """
    获取存储库 URL
    :param name: 存储库名称
    :return: 存储库 URL
    """
    from . import CONFIG
    if name in CONFIG.addons:
        return CONFIG.addons[name]['path']
    else:
        name = name.replace('-', '_')
        try:
            return CONFIG.addons[name]['path']
        except KeyError as e:
            print(f'{TimeStamp()} [ERRO] 查找失败: NMAE: {name} FULL_NAME: {e}')
            return None

def run_git_command(command):
    """
    执行 git 命令
    :param command: 要执行的 git 命令
    :return: 无
    """
    try:
        result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        print(f"{TimeStamp()} [GITS] 执行命令: {' '.join(command)}")
    except subprocess.CalledProcessError as e:
        print(f"{TimeStamp()} [ERRO] 执行错误: {remove_newlines(e.stderr)}")

def SerachGit(variable,config=None):
    """
    搜索存储库
    :param variable: 搜索关键字
    :return: 包含存储库名称和 URL 的字典
    """
    out_name = variable
    variable = variable.replace(' ', '-')
    words = ["blender", "addon"]
    serach_name = [f"{variable} {word}" for word in words] + [f"{word} {variable}" for word in words] + [variable]
    for item in serach_name:
        out_git = search_github_repositories(item,config=config)
        for git_data in out_git.get('items', []):
            if  variable.lower() in git_data['name'].lower():
                print(f'{TimeStamp()} [GITS] 搜索成功: NMAE: {git_data['name']} HTML_URL: {git_data['html_url']}')
                return {'name':out_name,'html_url':git_data['html_url'],'full_name':git_data['full_name']}
            elif not variable.lower() in git_data['name'].lower():
                return SerachGit(variable.replace('_', ' '),config)
            else:
                continue
        sleep(config['retry_interval'])
    print(f'{TimeStamp()} [ERRO] 搜索失败: NMAE: {out_name} FULL_NAME: None')
    return {'name':out_name,'html_url':"",'full_name':""} # if not out_data['full_name'] else out_data
