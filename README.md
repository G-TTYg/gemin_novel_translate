# Translate novel with gemini-pro

## 運行環境 
Python 3.9+

## web頁面程序
`gradio_translate_gemini.py`

## 翻譯小説儲存位置
`./novel/{novel_id}.cn/`

## 抓取原文
`get_kakuyomu.py ${id}` for kakuyomu
`get_ncode.py ${id}` for ncode

## 进行翻译
`auto_translate_gemini.py ${id} ${range_start} ${range_end}`
## 設置
`config.ini` 
請設置好API_KEY
## LICENSE
MIT


  
