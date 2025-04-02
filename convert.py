import sys
import re

from bs4 import BeautifulSoup
import requests
from langchain.chat_models import init_chat_model

model = init_chat_model("gpt-4o-mini", model_provider="openai")


def html_to_markdown(html):
    soup = BeautifulSoup(html, 'html.parser')
    soup = soup.find('div', class_='post-content')

    # 提取代码块
    for figure in soup.find_all('figure'):
        try:
            lang = figure.get('class', ['', ''])[1]
        except IndexError:
            lang = ''
        figure.replace_with(f'```{lang}\n{figure.text}\n```')

    for figure in soup.find_all('figure'):
        try:
            lang = figure.get('class', ['', ''])[1]
        except IndexError:
            lang = ''
        figure.replace_with(f'```{lang}\n{figure.text}\n```')

    # 提取代码块
    for pre in soup.find_all('pre'):
        code = pre.find('code')
        if code:
            lang = code.get('class', [''])[0].replace('language-', '')  # 获取代码语言
            pre.replace_with(f'```{lang}\n{code.text}\n```')

    # 转换加粗、斜体、标题等
    for strong in soup.find_all('strong'):
        strong.replace_with(f'**{strong.text}**')
    for em in soup.find_all('em'):
        em.replace_with(f'*{em.text}*')
    for h in range(1, 7):
        for tag in soup.find_all(f'h{h}'):
            # 移除标题中的 <em> 或 <i> 斜体
            for em in tag.find_all(['em', 'i']):
                em.unwrap()
            tag.replace_with(f'{"#" * h} {tag.text}')

    # 处理无序列表
    for ul in soup.find_all('ul'):
        for li in ul.find_all('li'):
            li.replace_with(f'- {li.text}')
        ul.unwrap()  # 移除 <ul> 标签
    # 处理有序列表
    for ol in soup.find_all('ol'):
        for i, li in enumerate(ol.find_all('li'), start=1):
            li.replace_with(f'{i}. {li.text}')
        ol.unwrap()  # 移除 <ol> 标签

    # 处理 <a> 链接，去掉 web.archive.org 前缀
    for a_tag in soup.find_all('a', href=True):
        cleaned_href = re.sub(r'^https?://web\.archive\.org/web/\d+/', '', a_tag['href'])
        a_tag.replace_with(f'[{a_tag.text}]({cleaned_href})')

    # 处理段落
    for p in soup.find_all('p'):
        p.insert_before("\n")
        p.insert_after("\n")

    return soup.get_text()


def fetch(url):
    r = requests.get(url)
    r.encoding = r.apparent_encoding
    markdown_text = html_to_markdown(r.text)
    soup = BeautifulSoup(r.text, 'html.parser')
    date = soup.find('time', class_='time').text.strip()
    title = soup.find('h1', class_='title').text.strip()
    read = int(int(soup.find('span', class_='read').text.split(':')[1]) * 1.5)
    desc = soup.find('meta', property="og:description").attrs['content']
    tags = [i.text.strip() for i in soup.find_all('a', class_='article-tag-list-link')]
    slug = model.invoke(f"Please generate an English slug based on the following title: {title}, please only say the slug and do not use pinyin", temperature=0).content
    return title, slug, date, read, desc, tags, markdown_text


def main():
    for i in range(1, 133):
        ...

if __name__ == '__main__':
    url = sys.argv[1]
    print(fetch(url))
