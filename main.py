# !/usr/bin/env python3
# -*- coding: UTF-8 -*-
# 模型文件：https://github.com/danielgatis/rembg/releases/download/v0.0.0/u2net.onnx 放在”C:\Users\Administrator\.u2net\u2net.onnx:
# 官方文档：https://github.com/danielgatis/rembg
"""
apikey面板：https://www.remove.bg/dashboard#api-key
临时邮箱：https://www.linshiyouxiang.net 可用域名：@bestdefinitions.com

安装cv2，pip install opencv-contrib-python==4.5.5.64
适用于:python3.7 python3.8 python3.9 解释器
"""
from pathlib import Path

import requests
from rembg import remove, new_session


def api_key():
    f = open('tokens.txt', mode="r", encoding="utf-8")
    f.seek(0)
    token = f.readline().strip()
    f.seek(0)
    tokens = f.read()
    f.seek(0)
    f.close()
    f = open('tokens.txt', mode="w", encoding="utf-8")
    tokens = tokens.replace(token, "").strip() + "\n" + token
    f.write(tokens)
    f.close()
    return token


def main(rebg_type):
    # color Ex:red,green / hex:81d4fa ?  "
    bgcolor = "white"
    # bgcolor = ""  # 留空为空白背景
    api = api_key()
    if not Path("out_img").exists():
        Path("out_img").mkdir()
    p = Path('in_img')
    # 获取in_img目录下所有.png,.jpg文件
    for file in p.glob('*.[pj][np]g'):
        input_path = str(file)
        output_path = str(p.parent / ("out_img/" + file.name))
        if Path(output_path).exists():
            continue
        with open(input_path, 'rb') as i:
            with open(output_path, 'wb') as o:
                photo_data = i.read()
                if rebg_type == "web":
                    output = rebg_web(photo_data, api, bgcolor)
                    while not output:
                        api = api_key()
                        output = rebg_web(photo_data, api, bgcolor)
                    if output == 400:
                        output = rebg_cpu(photo_data)
                elif rebg_type == "onnx":
                    output = rebg_cpu(photo_data)
                o.write(output)


def rebg_web(photo_data, api, bgcolor=None):
    """
    借助https://www.remove.bg网站免费用户每个月50额度处理
    :param photo_data:
    :param api:
    :param bgcolor:
    :return:
    """
    # 官方API教程：https://www.remove.bg/api#sample-code
    response = requests.post(
        'https://api.remove.bg/v1.0/removebg',
        files={'image_file': photo_data},
        data={'size': 'auto', 'bg_color': bgcolor},
        headers={'X-Api-Key': api})
    if response.status_code == 200:
        return response.content
    elif response.status_code == 400:
        print("抠图失败，Could not identify foreground in image")
        return 400
    elif response.status_code == 402:
        print("额度已用尽，Insufficient credits")
    elif response.status_code == 403:
        print("Api Key出错，Api Key fail")
        print(api)
    elif response.status_code == 429:
        print("超过速度限制，Rate limit exceeded")
    else:
        print("未知错误")
        print(response.status_code, response.text)


def rebg_cpu(photo_data):
    # 选择模型
    session = new_session(model_name="u2net")
    return remove(photo_data, session=session)


if __name__ == "__main__":
    main(rebg_type="web")
    # main(rebg_type="onnx")
