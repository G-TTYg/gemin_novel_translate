import os
import re
import requests
import glob
from bs4 import BeautifulSoup
import json



def get_novel_data(main_url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }
    proxies = {
        'http': 'http://127.0.0.1:10809',
        'https': 'http://127.0.0.1:10809',
    }
    response = requests.get(main_url, headers=headers, proxies=proxies)
    response.encoding = "utf-8"
    html_content = response.text
    soup = BeautifulSoup(html_content, "html.parser")
    total_chapters = len(soup.find_all("dl", class_="novel_sublist2"))
    if total_chapters == 0 :
        return 0, ''
    novel_title = soup.find("p", class_="novel_title").text
    return total_chapters, novel_title



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


def main(novel_dir):
    main_url = f"https://ncode.syosetu.com/{novel_dir}"

    total_chapters, novel_title = get_novel_data(main_url)

    if total_chapters == 0 :
        return 200


    check_directory(novel_dir)

    with open("./title.json", 'r+',encoding="utf-8") as f :
        titles = json.load(f)
        titles[novel_dir] = novel_title
        f.seek(0)
        json.dump(titles, f, ensure_ascii=False)


    #print(f"该作品总共有 {total_chapters} 章。")
    
    start_chapter, end_chapter = 1, 10000

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }
    proxies = {
        'http': 'http://127.0.0.1:10809',
        'https': 'http://127.0.0.1:10809',
    }

    for index in range(start_chapter, end_chapter + 1):
        chapter_url = f"{main_url}/{index}/"
        if len(glob.glob(f"./{novel_dir}/{str(index).zfill(3)}_*.txt")) > 0 :
            continue

        response = requests.get(chapter_url, headers=headers, proxies=proxies)
        response.encoding = "utf-8"
        html_content = response.text
        soup = BeautifulSoup(html_content, "html.parser")

        nothing = soup.find("div", class_="nothing")
        if nothing is not None :
            break

        chapter_title = soup.find("p", class_='novel_subtitle').text.strip()
        chapter_content = soup.find("div", id='novel_honbun')

        #padding_width = len(str(total_chapters))
        file_name = f"{chapter_title}.txt"

        if not is_valid_file_name(file_name):
            #print("文件名包含不符合规范的字符，修复中...")
            file_name = fix_file_name(file_name)
        #print("添加章节号及前导零到文件名中...")
        file_name = add_chapter_number(file_name, index, 3)

        filename = f"{novel_dir}/{file_name}"

        if os.path.exists(filename):
            #print(f"文件已经存在，跳过：{filename}")
            continue

        with open(filename, "w", encoding="utf-8") as file:
            file.write(chapter_title + "\n")
            for paragraph in chapter_content.find_all("p"):
                file.write(paragraph.text + "\n")

        #print(f"文件已保存为：{filename}")
    return 400

if __name__ == '__main__':
    main('n9246fl')
