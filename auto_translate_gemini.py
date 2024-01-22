#!/usr/bin/env python3
import logging
import os
import glob
import time
from gemini_translate_api import api as gemini
from gemini_translate_api import memo_api
from content_opt import content_opt
from configparser import ConfigParser

# 配置日志
logging.basicConfig(filename='log.txt', filemode='a', level=logging.INFO, format='%(asctime)s - %(message)s')

#讀取設置
config = ConfigParser()
config.read('config.ini')
API_KEY = config.get('database','API_KEY')

def inlog(text):
    safe_text = text.encode("utf-8", errors="ignore").decode("utf-8")
    logging.info(safe_text)
    print(safe_text)


def load_novel_chapter(novel_id, chapter_range):
    # 读取小说的某个章节
    file_pattern = os.path.join(novel_id, f"{str(chapter_range).zfill(3)}_*.txt")

    file_list = glob.glob(file_pattern)
    if not file_list:
        return None

    chapter_file_name = file_list[0]

    with open(chapter_file_name, "r", encoding="utf-8") as f:
        novel_content = f.read()

    return novel_content


def make_novel_dir(novel_id):
    translated_novel_dir = f"./novel/{novel_id}_cn"
    head = ' | 日文原文 | 繁體中文 |\n|---|---|'
    if os.path.exists(translated_novel_dir):
        # print(f"目录 {translated_novel_dir} 已存在")
        pass
    else:
        os.makedirs(translated_novel_dir)
        print(f"目录 {translated_novel_dir} 创建成功")
        open(f"./novel/{novel_id}_cn/memo.txt",'w', encoding="utf-8").write(head)

def save_translated_novel(novel_id, chapter_range, novel_translated):

    translated_novel_dir = f"./novel/{novel_id}_cn"

    file_pattern = os.path.join(novel_id, f"{str(chapter_range).zfill(3)}_*.txt")
    file_list = glob.glob(file_pattern)

    if file_list:
        original_file_name = os.path.basename(file_list[0])
        translated_file_path = os.path.join(translated_novel_dir, original_file_name)

        novel_translated = novel_translated.replace('\r', ' ')

        with open(translated_file_path, "w", encoding="utf-8") as f:
            f.write(novel_translated)
        print(f"翻译后的小说已保存到：{translated_file_path}")
    else:
        raise FileNotFoundError("未找到指定前缀的原始文件。")

def istranslated(novel_id, chapter_range):
    translated_novel_dir = f"./novel/{novel_id}_cn"

    file_pattern = os.path.join(novel_id, f"{str(chapter_range).zfill(3)}_*.txt")
    file_list = glob.glob(file_pattern)

    if file_list:
        original_file_name = os.path.basename(file_list[0])
        translated_file_path = os.path.join(translated_novel_dir, original_file_name)

        return os.path.exists(translated_file_path)

    else :
        return False


def add_memo(novel_id, novel_content="") :


    memo_file = open(f"./novel/{novel_id}_cn/memo.txt",'r+',encoding='utf-8')
    memo = memo_file.read()

    memo_file.seek(0)
    if novel_content != '' :
        temp_memo = memo_api(API_KEY,content=novel_content)

        if temp_memo.get('candidates') is not None:

            temp_memo = temp_memo['candidates'][0]['content']['parts'][0]['text'].split('\n')[2:]

            for amemo in temp_memo :
                if len(amemo) > 23 :
                    continue
                if amemo.split('|')[1].strip() in memo :
                    continue
                if amemo.split('|')[1].strip() not in novel_content :
                    continue

                memo = memo + '\n' + amemo

    #print(memo)

    memo_file.write(memo)
    memo_file.close()

    out = ''
    cnt = 0
    for amemo in memo.split('\n')[2:]:
        #print(amemo.split('|')[1])
        if len(amemo) > 23:
            continue
        if amemo.split('|')[1].strip() in novel_content:
            cnt += 1
            out = out + '\n' + amemo
        if cnt > 40 :
            break
    return out

#main-------------------------

def main(novel_id, chapter_range_start = 1, chapter_range_end=999):

    make_novel_dir(novel_id)


    for chapter_range in range(chapter_range_start, chapter_range_end + 1):
        if istranslated(novel_id,chapter_range) :
            continue
        novel_content = load_novel_chapter(novel_id, chapter_range)
        if novel_content is None :
            break
        novel_content = novel_content[:novel_content.find("作品紹介")]
        novel_content = content_opt(novel_content, 3)
        memo = add_memo(novel_id, novel_content)

        inlog(f"开始翻译 {novel_id}_{chapter_range}")
        cnt = 0
        while cnt<3:
            cnt += 1
            novel_translated = gemini(API_KEY=API_KEY, content=novel_content, proprietary=memo, timeout=180, temperature=0.1, topK=1, topP=0.1)

            error = novel_translated.get('error')

            if error is not None:
                if 'Read timed out' in str(novel_translated) :
                    inlog(f"未知錯誤:{novel_translated}")
                    break
                inlog(f"發生錯誤，重新嘗試:{novel_translated}")
                time.sleep(5)
            elif novel_translated.get('candidates') is not None:
                novel_translated = novel_translated['candidates'][0]['content']['parts'][0]['text']
                save_translated_novel(novel_id, chapter_range, novel_translated)
                break
            else:
                if novel_translated == {'promptFeedback': {'blockReason': 'OTHER'}}:
                    inlog(f"被谷歌屏蔽:{novel_translated}")
                    break
                inlog(f"未知情況:{novel_translated}")
                break


        # 保存翻译好的小说


        inlog(f"{chapter_range}已完成")

    inlog(f"{novel_id}的翻譯受理已完成")
    return 400



if __name__ == '__main__' :
    import sys
    #main('n0388ee',1)
    #main('n4744ia', 161)
    main(sys.argv[1], sys.argv[2], sys.argv[3])
    #add_memo('n7575gq', novel_content)
