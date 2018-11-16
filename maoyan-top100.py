import requests
from requests.exceptions import RequestException
import re
import json
import os
from multiprocessing import Pool
#from fake_useragent import UserAgent
# from selenium import webdriver

def get_one_page(url):
    try:
        # ua = UserAgent()
        headers = {"User-Agent": "Mozilla/5.0 (Macintosh;Intel Mac OS X 10_13_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36"}
        # headers = {"User-Agent": ua.random}
        response = requests.get(url=url, headers=headers)
        if response.status_code == 200:
            return response.text
        return None
    except RequestException:
        return None
# 解析一页的html
def parse_one_page(html):
    # 正则表达式进行解析
    pattern = re.compile('<dd>.*?board-index.*?>(\d+)</i>.*?data-src="(.*?)".*?name">'
                         + '<a.*?>(.*?)</a>.*?"star">(.*?)</p>.*?releasetime">(.*?)</p>'
                         + '.*?integer">(.*?)</i>.*?fraction">(.*?)</i>.*?</dd>', re.S)

    #根据正则表达式匹配其中的内容
    items = re.findall(pattern, html)
    # 导入数组里面
    for i in items:
        yield {
            'index': i[0],
            'image': i[1],
            'moive-name': i[2],
            'actor': i[3].strip()[3:], #这里strip代表删除，语法str.strip([chars]); 不带参数则参数/n，/t等。[3:]切片，代表去除前三个字符
            'time': i[4].strip()[5:],
            'douban-score': i[5]+i[6]
        }
# 保存电影到txt文本
def write_file(content):
    # 'a' 代表open for writing, appending to the end of the file if it exists
    with open('/Users/pasca/Desktop/猫眼-crawler/maoyan.txt', mode='a', encoding='utf-8')  as f:
        f.write(json.dumps(content, ensure_ascii=False) + '\n')
        f.close()

# 保存封面到文件夹
def save_img_file(url ,path):
    ir = requests.get(url)
    if ir.status_code == 200:
        with open(path, 'wb') as f:
            f.write(ir.content)
            f.close()


def main(offset):
    url = 'http://maoyan.com/board/4?offset={}'.format(offset)
    html = get_one_page(url)
    parse_one_page(html)
    # 判断封面文件是否存在
    if not os.path.exists('maoyan'):
        os.mkdir('maoyan')
    for i in parse_one_page(html):
        print(i)
        write_file(i)
        save_img_file(i['image'], 'maoyan/' + '%03d'%int(i['index']) + i['moive-name'] + '.jpg')

if __name__ == '__main__':
    P = Pool()
    P.map(main, [i*10 for i in range(10)])   # 循环翻页



