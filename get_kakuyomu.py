#!/usr/bin/env python3
import os
import re
import requests
import json
from bs4 import BeautifulSoup

def is_valid_directory_name(directory_name):
    pattern = r'^[^\/:*?"<>|]+$'
    if re.match(pattern, directory_name):
        return True
    return False

def is_valid_file_name(file_name):
    pattern = r'^[^\/:*?"<>|]+\.txt$'
    if re.match(pattern, file_name):
        return True
    return False

def fix_file_name(file_name):
    pattern = r'[\/:*?"<>|]+'
    fixed_file_name = re.sub(pattern, '', file_name)
    return fixed_file_name + '.txt' if not fixed_file_name.endswith('.txt') else fixed_file_name


def add_chapter_number(file_name, chapter_number, padding_width):
    file_name = f"{str(chapter_number).zfill(padding_width)}_{file_name}"
    return file_name + '.txt' if not file_name.endswith('.txt') else file_name

def check_directory(directory_name):
    if os.path.exists(directory_name):
        print(f"目录 {directory_name} 已存在")
        return
    if not is_valid_directory_name(directory_name):
        print("目录名称不符合规范")
        return
    try:
        os.makedirs(directory_name)
        print(f"目录 {directory_name} 创建成功")
    except OSError as error:
        print(f"创建目录 {directory_name} 时出错: {error}")

def get_chapter(main_url):
    response = requests.get(f"https://kakuyomu.jp/works/{main_url}")
    response.encoding = "utf-8"
    html_content = response.text
    soup = BeautifulSoup(html_content, "html.parser")
    chapter_links = [a['href'] for a in soup.find_all("a", class_=re.compile("^WorkTocSection_link"))]
    if chapter_links == [] :
        return 0, ''
    title = soup.find('a', href=f"/works/{main_url}").text

    return chapter_links[0], title


def main(novel_dir):
    main_url = novel_dir
    #main_url = 'https://kakuyomu.jp/works/16817139556288291993/episodes/16817139556288389322'
    link, novel_title = get_chapter(main_url)

    if link == 0:
        return 200

    check_directory(novel_dir)

    #print(novel_title)

    with open("./title.json", 'r+',encoding="utf-8") as f :
        titles = json.load(f)
        titles[novel_dir] = novel_title
        f.seek(0)
        json.dump(titles, f, ensure_ascii=False)


    index = 0
    while True:
        chapter_url = f"https://kakuyomu.jp{link}"
        index += 1
        #print(link)
        response = requests.get(chapter_url)
        response.encoding = "utf-8"
        html_content = response.text
        soup = BeautifulSoup(html_content, "html.parser")

        chapter_title = soup.find("p", class_="widget-episodeTitle js-vertical-composition-item").text.strip()
        chapter_content = soup.find("div", class_="widget-episodeBody js-episode-body")

        # padding_width = len(str(len(chapter_links)))

        file_name = f"{chapter_title}.txt"

        if not is_valid_file_name(file_name):
            # print("文件名包含不符合规范的字符，修复中...")
            file_name = fix_file_name(file_name)
        # print("添加章节号及前导零到文件名中...")
        #print(index)
        file_name = add_chapter_number(file_name, index, 3)  # padding_width)
        #print(file_name)
        filename = f"{novel_dir}/{file_name}"

        # # 检查文件是否存在，如果存在则跳过
        # if os.path.exists(filename):
        #     continue

        with open(filename, "w", encoding="utf-8") as file:
            file.write(chapter_title + "\n")
            for paragraph in chapter_content.find_all("p"):
                file.write(paragraph.text + "\n")
        # print(f"文件已保存为：{filename}")

        link = soup.find("a", id="contentMain-readNextEpisode")

        if link is None :
            break
        else :
            link = link['href']


    return 400

if __name__ == '__main__':
    import sys
    main(sys.argv[1])
