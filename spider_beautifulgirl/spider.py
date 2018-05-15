import codecs
import json
from _md5 import md5
from urllib.parse import urlencode

import re
import requests
from bs4 import BeautifulSoup
from requests import RequestException


def get_target_data(offect, noun):
    """
    获取目标链接的网页数据
    :param offect: 指定
    :param noun:关键字
    :return:返回网页的html
    """
    data = {
        "offset": offect,
        "format": "json",
        "keyword": noun,
        "autoload": "true",
        "count": 20,
        "cur_tab": 1,
        "from": "search_tab"
    }
    target_url = 'https://www.toutiao.com/search_content/?' + urlencode(data)
    try:
        response = requests.get(target_url)
        response.encoding = 'utf-8'
        if response.status_code == 200:
            return response.text
        return None
    except RequestException:
        print('目标页请求错误', target_url)
        return None


def parse_target_url(html):
    html = json.loads(html)
    if html and 'data' in html.keys():
        for item in html.get('data'):
            yield item.get('article_url')


def get_detail_url(listurl):
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36'}
    try:
        response = requests.get(listurl, headers=headers)
        if response.status_code == 200:
            return response.text
        return None
    except RequestException:
        print('详情页请求错误', listurl)
        return None


def parse_detail_data(html, detail_url):
    soup = BeautifulSoup(html, 'html.parser')
    title = soup.select('title')[0].text
    images_pattern = re.compile(r'gallery: JSON.parse\("(.*?)"\),', re.S)
    result = re.search(images_pattern, html)
    if result:
        data_str = codecs.getdecoder('unicode_escape')(result.group(1))[0]
        data_detail = json.loads(data_str)
        if data_detail and 'sub_images' in data_detail.keys():
            sub_image = data_detail.get('sub_images')
            url = [item.get('url') for item in sub_image]
            for image in url: down_image(image)


def down_image(url):
    print('下载',url)
    try:
        response = requests.get(url)
        if response.status_code == 200:
            save_image(response.content)
        return None
    except RequestException:
        print('下载图片出错', url)
        return None


def save_image(content):
    file_path = '{0}.{1}'.format(r'C:\Users\98725\Desktop\beautiful_girl\\', md5(content).hexdigest() + '.jpg')
    with open(file_path, 'wb') as f:
        f.write(content)


def main():
    """
    主函数，程序的入口
    :return:
    """
    html = get_target_data(0, '街拍')
    list_url = parse_target_url(html)
    for url in list_url:
        if url:
            detail_data = get_detail_url(url)
            if detail_data:
                result = parse_detail_data(detail_data, url)


if __name__ == '__main__':
    main()
