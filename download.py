import requests
from lxml import etree
import re
import json
import os
import subprocess
from DecryptLogin import login
url = "https://www.bilibili.com/video/BV1qL411X7km"
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36 Edg/111.0.1661.62",
    "referer": url,
    # "cookie": "buvid3=3B115D6B-CA98-4923-2ACE-B322CB94B91455889infoc; i-wanna-go-back=-1; _uuid=2E5AD73A-6748-CEA4-7172-64CE97E3987D57363infoc; buvid_fp=f4816ca0e96c5e3ac0fa8e57c960bd5d; home_feed_column=5; b_nut=1681093358; header_theme_version=CLOSE; CURRENT_FNVAL=4048; SESSDATA=91d8f4d4%2C1696645468%2C7b853%2A42; bili_jct=09f01cdb4ad1f0cb0b4224d79ca7a4e4; DedeUserID=235725074; DedeUserID__ckMd5=27e52022f4bd895c; CURRENT_PID=d5096a40-d746-11ed-adb6-87a2ab07afb8; rpdid=|(k|Jukmmk|Y0J'uY)u|mJR~J; b_ut=5; nostalgia_conf=-1; hit-new-style-dyn=1; hit-dyn-v2=1; b_lsid=93CA10B74_1876A48FB02; sid=5vyr434r; bsource=search_baidu; buvid4=3C7168E0-1995-385D-C813-BB48FBF47B2256713-023041010-NN2LV+JlEhyK6Lnbp/BlXg%3D%3D; innersign=1; bp_video_offset_235725074=782872538543816700; CURRENT_QUALITY=120; PVID=5"
}


def my_login(username, password):
    """
    调用大佬的登录库实现bilibili登录
    :param username:
    :param password:
    :return:
    """
    _, session = login.Login().bilibili(username, password)
    return session


def splicing(file_name, title):
    """
    合并下载得到的视频和音频文件
    :param file_name:
    :param title:
    :return:
    """
    command = f'ffmpeg -i {file_name}.mp4 -i {file_name}.mp3 -c copy {title}.mp4'
    print(command)
    os.system(command)
    os.remove(f'{file_name}.mp4')
    os.remove(f'{file_name}.mp3')


def main():
    # 这一行代码是为了登录并拿到session 当我们拿到session之后 才能得到包含高清下载链接的html文件
    # 否则我们只能拿到只有360p和480p下载链接的html文件
    session = my_login("13849857524", "cwb68582818")
    resp = session.get(url)
    # 如果只想要下载低清的视频 那就不用登录 直接用下面这行代码就行
    # resp = requests.get(url, headers=headers)
    resp.encoding = "utf-8"
    page_text = resp.text
    pattern = "<script>window.__playinfo__=(?P<url_dict>.*?)</script><script>window.__INITIAL_STATE__"
    s = re.search(pattern, page_text).group("url_dict")

    url_json = json.loads(s)
    video_list = url_json["data"]["dash"]["video"]
    audio_list = url_json["data"]["dash"]["audio"]
    # 我们只下载最清晰的版本 应该没人下载低分辨率版本吧
    video_url = video_list[0]["baseUrl"]
    audio_url = audio_list[0]["baseUrl"]
    id = video_list[0]["id"]
    # 请求视频和音频 拿到m4s文件 但是我们发现m4s文件并未加密 直接改成mp4 或者mp3文件就可以播放
    # 因此直接保存为mp4 或者mp3文件
    file_name = str(video_url).split("?")[0].split(".")[-2].split("/")[-1]
    title = url.split("/")[-1] + f"-{id}"
    print("开始下载...请慢慢等待")
    if not os.path.exists(f"{file_name}.mp4"):
        video = requests.get(video_url, headers=headers)
        audio = requests.get(audio_url, headers=headers)
        with open(f"{file_name}.mp4", "wb") as f1, open(f"{file_name}.mp3", "wb") as f2:
            f1.write(video.content)
            f2.write(audio.content)
    splicing(file_name, title)
    print(f"下载完成,文件名为{title}.mp4")


if __name__ == '__main__':
    main()
