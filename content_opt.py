#!/usr/bin/env python3
import re

def content_opt(content, count):
    pattern = r"([^0123456789-。._])\1{" + str(count + 1) + r",}"
    content = re.sub(pattern, lambda x: x.group(1) * count, content)
    pattern = r"([ァア]){" + str(count + 1) + r",}"
    content = re.sub(pattern, lambda x: (x.group(1) * count)[:count], content)
    pattern = r"([ィイ]){" + str(count + 1) + r",}"
    content = re.sub(pattern, lambda x: (x.group(1) * count)[:count], content)
    pattern = r"([ゥウ]){" + str(count + 1) + r",}"
    content = re.sub(pattern, lambda x: (x.group(1) * count)[:count], content)
    pattern = r"([ェエ]){" + str(count + 1) + r",}"
    content = re.sub(pattern, lambda x: (x.group(1) * count)[:count], content)
    pattern = r"([ォオ]){" + str(count + 1) + r",}"
    content = re.sub(pattern, lambda x: (x.group(1) * count)[:count], content)
    pattern = r"([ヮワ]){" + str(count + 1) + r",}"
    content = re.sub(pattern, lambda x: (x.group(1) * count)[:count], content)
    return content


if __name__ == '__main__':
    print(content_opt('「――ブモォオオオオッッ！！」', 4))
