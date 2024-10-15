import requests

def search_github_repositories(repo_name, per_page=10, page=1):
    """
    根据存储库名称在 GitHub 上搜索公开存储库
    :param repo_name: 存储库名称
    :param per_page: 每页显示的结果数量
    :param page: 页码
    :return: 搜索结果的 JSON 数据
    """
    url = "https://api.github.com/search/repositories"
    params = {
        "q": repo_name,
        "per_page": per_page,
        "page": page
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"An error occurred: {e}")
        return None
    return response.json()

def serach_git(variable):
    out_name = variable
    variable = variable.replace(' ', '-')
    words = ["blender", "addon"]
    serach_name = [f"{variable} {word}" for word in words] + [f"{word} {variable}" for word in words] + [variable]
    for item in serach_name:
        out_git = search_github_repositories(item)
        for git_data in out_git.get('items', []):
            if  variable.lower() in git_data['name'].lower():
                print('YES',git_data['name'],git_data['full_name'])
                return {'name':out_name,'html_url':git_data['html_url'],'full_name':git_data['full_name']}
            else:
                print('NO',git_data['name'],git_data['full_name'])
    return {'name':out_name,'html_url':"",'full_name':""}


x = serach_git("Utilities Gadget")
pass
# # 示例用法
# variable = "drop it"


# repo_name = "drop it blender".replace(' ', '-')
# results = search_github_repositories(repo_name)

# # 打印搜索结果
# for item in results.get('items', []):
#     print(f"Name: {item['name']}, URL: {item['html_url']}, Description: {item['description']}")