import pytesseract
import time, datetime
from PIL import Image
from PIL import ImageGrab
import os
import requests
import urllib.request
from bs4 import BeautifulSoup

DATE_FORMAT = "%Y-%m-%d"
IMAGE_PATH = "answer.png"
BASE_URL = 'https://zhidao.baidu.com/search?ct=17&pn=0&tn=ikaslist&rn=10&fr=wwwt&word={}'

answerOne = ""
answerTwo = ""
answerThree = ""


def grabScreen():
    # 根据自己屏幕截取答案和问题
    # ApowerMirror 放置到桌面左上角
    # image = ImageGrab.grab(bbox=(20, 200, 680, 400)) #百万英雄
    image = ImageGrab.grab(bbox=(70, 500, 400, 815))  # 支付宝答答英雄
    # image = ImageGrab.grab(bbox=(50, 410, 750, 1100))

    image.save(IMAGE_PATH)


def recognition():
    global answerOne
    global answerTwo
    global answerThree

    image = Image.open(IMAGE_PATH)
    character = pytesseract.image_to_string(image, lang="chi_sim+eng")
    print(character)
    list = character.split('\n\n')
    try:

        question = list[0]
        answerOne = list[1]
        answerTwo = list[2]
        answerThree = list[3]
    except:
        print("===答案识别失败===")

    return character


def search(question):
    # question = "北京裹运会哪一年举办?"
    questionParm = urllib.request.quote(question)
    url = BASE_URL.format(questionParm)
    print(url)
    return url


# 按分数排序
def by_count(t):
    return -t[1]


def analysis(url):
    countAnswerOne = 0
    countAnswerTwo = 0
    countAnswerThree = 0

    html = requests.get(url)  # requests 请求页面内容 由于百科搜索没有限制爬取，所以不用设置伪请求头
    soup = BeautifulSoup(html.content, "html.parser")  # BeautifulSoup解析页面内容
    items = soup.find_all("dl", "dl")  # 获取所有的答案内容
    for i in items:
        firstResult = i.find("dd", "dd summary")
        secondresult = i.find("dd", "dd answer")
        if firstResult is not None:
            countAnswerOne += firstResult.text.count(answerOne)
            countAnswerTwo += firstResult.text.count(answerTwo)
            countAnswerThree += firstResult.text.count(answerThree)
            print(firstResult.text)
        if secondresult is not None:
            countAnswerOne += secondresult.text.count(answerOne)
            countAnswerTwo += secondresult.text.count(answerTwo)
            countAnswerThree += secondresult.text.count(answerThree)
            print(secondresult.text)

    print("答案A出现次数 ： %d" % countAnswerOne)
    print("答案B出现次数 ： %d" % countAnswerTwo)
    print("答案C出现次数 ： %d" % countAnswerThree)

    tuple = [('A', countAnswerOne), ('B', countAnswerTwo), ('C', countAnswerThree)]

    tupleRise = sorted(tuple, key=by_count)

    print("推荐答案 ： %s" % (tupleRise[0][0]))


def main():
    # 截取题目
    start = datetime.datetime.now()
    dir = start.strftime(DATE_FORMAT)
    if not os.path.exists(dir):
        os.makedirs(dir)



    grabScreen()

    # 文字识别
    question = recognition()

    # 百度知道搜索答案
    url = search(question)

    # 解析网页
    analysis(url)


if __name__ == '__main__':
    main()
