#!/usr/bin/env python3
#coding:utf-8

import os
import logging
import gradio as gr
from gemini_translate_api import gemini_api
import get_ncode
import get_kakuyomu
import auto_translate_gemini
from content_opt import content_opt
from configparser import ConfigParser

def inlog(text):
    safe_text = text.encode("utf-8", errors="ignore").decode("utf-8")
    logging.info(safe_text)
    print(safe_text)


def get_novel_list():
    return os.listdir("./novel")

def get_novel_cha(id):
    try :
        return [gr.update(choices=os.listdir(f"./novel/{id}"), visible=True, value=None), gr.update(visible=False)]
    except :
        return [gr.update(visible=False), gr.update(visible=False)]

def show_novel(id1,id2):
    try :
        with open(f"./novel/{id1}/{id2}", 'r', encoding="utf-8") as f :
            return gr.update(value=f.read(), visible=True)

    except :
        return gr.update(visible=False)



def main_translate(api_key, content, strong_prompts, proprietary, timeout, temperature, topK, topP) :
    if api_key == '' :
        api_key = API_KEY
    inlog(f"收到請求")
    content = content_opt(content, 4)[:7005]
    inlog(content)
    novel_translated = gemini_api(api_key, content, strong_prompts, proprietary, timeout, temperature, topK, topP)
    if novel_translated.get('candidates') is not None :
        inlog(novel_translated['candidates'][0]['content']['parts'][0]['text'])
        return novel_translated['candidates'][0]['content']['parts'][0]['text']
    elif novel_translated == {'promptFeedback': {'blockReason': 'OTHER'}} :
        return "被谷歌屏蔽...請嘗試分段發送"
    return str(novel_translated)


def auto_translate(novel_url,novel_id) :
    yield '已受理\n開始爬取...'
    if novel_url == 'ncode' :
        state = get_ncode.main(novel_id)
    elif novel_url == 'kakuyomu' :
        state = get_kakuyomu.main(novel_id)
    if state != 400 :
        yield 'Error'
        return
    yield '開始翻譯...\n可以到已翻譯的小説查看'

    auto_translate_gemini.main(novel_id)

    return


#讀取設置
config = ConfigParser()
config.read('config.ini')
API_KEY = config.get('database','API_KEY')
server_name = config.get('database','server_name')
server_port = config.getint('database','server_port')

fyxg = ''


show_rule = {'ncode':'應該是英文數字組合','kakuyomu':'應該是一連串數字'}



with gr.Blocks() as web:
    with gr.Tab("翻譯日文"):
        #gr.Markdown("把小說粘貼進來，點擊開始翻譯即可", )
        novel_content = gr.Textbox(label='日文原文', placeholder='把小説粘貼這...\n單次最長7000字，否則會自動切掉',lines=10)
        gr.Markdown("使用谷歌gemini-pro進行翻譯")
        gr.Markdown("翻譯5000字大約要一分鐘")
        gr.Markdown("過於血腥暴力或未知原因的可能會被谷歌屏蔽")
        run_button = gr.Button("開始翻譯")
    with gr.Tab("翻译结果"):
        #output = gr.Markdown()
        output = gr.Textbox(label='譯文', placeholder='還沒有開始翻譯', show_copy_button=True, max_lines=9999, container=False)
    with gr.Tab("設置"):
        with gr.Row():
            temperature = gr.Slider(minimum=0.0, maximum=1.0, value=0.1, label='温度', step=0.05)
            top_p = gr.Slider(minimum=0.0, maximum=1.0, value=0.1, label='Top P', step=0.05)

        with gr.Row():
            top_k = gr.Slider(minimum=1, maximum=32, value=1, label='Top K', step=1)
            timeout = gr.Slider(minimum=60, maximum=1000, value=120, label='超時時間', step=10)

        with gr.Row():
            strong_prompts = gr.Textbox(label='加强Prompts', value='',placeholder='加强提示詞，修正結果')

        with gr.Row():
            proprietary = gr.Textbox(label='特殊名詞及翻譯習慣',value=fyxg, placeholder='範例:\n日文:中文\n母さん：老媽\nうずまきナルト:漩渦鳴人',lines=5)

        with gr.Row():
            gemini_api_key = gr.Textbox(label='API_KEY',value='', placeholder='留空使用公共api_key，或使用自己的API_KEY')
        gr.Markdown("注意，設置不做用於批量翻譯")
    with gr.Tab("批量翻譯") :

        novel_url = gr.Dropdown(choices=['ncode','kakuyomu'], label="選擇網站", value='ncode', interactive=True)
        novel_id = gr.Textbox(label='小説id', placeholder='應該是英文數字組合', interactive=True)
        gr.Markdown("只支持從ncode和kakuyomu翻譯")
        gr.Markdown("選擇其一然後輸入小説id")
        gr.Markdown("如:")
        gr.Markdown("kakuyomu.jp/works/16817330650266014506 這個id就是 16817330650266014506")
        gr.Markdown("ncode.syosetu.com/n7575gq 這個id為 n7575gq")
        batch_run = gr.Button("開始翻譯")
        gr.Markdown("批量小説翻譯會在伺服器上進行，並保存在伺服器上，任何人都可以查看")
        gr.Markdown("可以在 已翻譯的小説 中查看已發送請求的小説")
        gr.Markdown("注意，某些章節可能因爲某些原因被谷歌屏蔽無法翻譯，會自動跳過")
        batch_out = gr.Textbox(label="日志")


    with gr.Tab("已翻譯的小説") as translated_block :
        choose_novel = gr.Dropdown(label="選擇小説", choices=get_novel_list(), interactive=True)
        choose_cha = gr.Dropdown(label="選擇章節", choices=[], visible=False, interactive=True)
        novel_text = gr.Textbox(label='譯文', show_copy_button=True, visible=False, max_lines=9999, container=False)

    #update

    novel_url.change(lambda x:gr.update(placeholder=show_rule[x]), novel_url, novel_id)

    choose_novel.change(lambda :gr.update(choices=get_novel_list()), outputs=choose_novel, concurrency_limit=10)
    choose_cha.change(lambda id:gr.update(choices=os.listdir(f"./novel/{id}")), choose_novel, outputs=choose_cha, concurrency_limit=10)

    choose_novel.change(get_novel_cha, choose_novel, [choose_cha, novel_text], concurrency_limit=10)
    choose_cha.change(show_novel, [choose_novel, choose_cha], novel_text, concurrency_limit=10)

    translated_block.select(lambda :gr.update(choices=get_novel_list()), outputs=choose_novel, concurrency_limit=30)
    #run



    batch_run.click(auto_translate, [novel_url, novel_id], batch_out, concurrency_limit=10)

    run_button.click(main_translate, [gemini_api_key, novel_content, strong_prompts, proprietary, timeout, temperature, top_k, top_p], output, concurrency_limit=10)


web.title = "使用Gemini來翻譯日輕小説"
web.queue()
web.launch(server_name=server_name, server_port=server_port, show_error=True, share=True)

