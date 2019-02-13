# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals

import os
import time
import datetime
import requests
import pytesseract
import urllib.request
from PIL import Image
from PIL import ImageGrab
from bs4 import BeautifulSoup
from selenium import webdriver
from Utils.log import *
import webbrowser

DATE_FORMAT = "%Y-%m-%d"
BASE_URL = 'https://zhidao.baidu.com/search?ct=17&pn=0&tn=ikaslist&rn=10&fr=wwwt&word={}'

LOG = get_logger("AutomaticAnswering", path="logs/", level=logging.DEBUG, max_byte=1024*1024*50, backup_count=10)

ACTIVITYS = [
    "DDXQ",  # 答答星球
    "ZXWD"   # 诸仙问道
]
DDXQ = 0
ZXWD = 1

class AutomaticAnswering(object):
    DDXQ_REGION = (70, 500, 400, 815)  # 答答星球

    def __init__(self, activity):
        self.activity = activity
        start = datetime.datetime.now()
        _date = start.strftime(DATE_FORMAT)
        if activity > len(ACTIVITYS):
            LOG.error("Not support Activity,out of range(0, {0})".format(len(ACTIVITYS)))
            raise Exception("Not Support Activity")
        self.question_dir = os.path.join(ACTIVITYS[activity], _date)
        if not os.path.exists(self.question_dir):
            os.makedirs(self.question_dir)

    @staticmethod
    def search(question):
        # question = "北京裹运会哪一年举办?"
        questionParm = urllib.request.quote(question)
        url = BASE_URL.format(questionParm)
        print(url)
        return url

    @staticmethod
    def initTable(threshold=140):  # 二值化函数
        table = []
        for i in range(256):
            if i < threshold:
                table.append(0)
            else:
                table.append(1)

        return table

    def grabScreen(self,index):
        LOG.debug("Grab Question {0}".format(index))
        txt_name = str(index) + ".txt"
        image_name = str(index) + ".png"

        if self.activity == DDXQ:
            image = ImageGrab.grab(bbox=AutomaticAnswering.DDXQ_REGION)
            image.save(os.path.join(self.question_dir, image_name))

            character = pytesseract.image_to_string(image, lang="chi_sim+eng", config='--psm 4')
            LOG.debug("Read from image: \n{0}".format(character))

            list = character.split('\n\n')
            list[0] = list[0].replace("\n", "")
            question = list[0]
            LOG.debug("Question:\n{0}".format(question))
            answers = list[1]
            answers = answers.split('\n')
            LOG.debug("Answers:\n{0}\n{1}".format(answers[0], answers[1]))
            _list = [line + "\n" for line in list]
            with open(os.path.join(self.question_dir, txt_name), "w") as f:
                f.writelines(_list)
        elif self.activity == ZXWD:
            # Save Question
            ZXWD_REQION = (42, 210, 440, 570)
            image_all = ImageGrab.grab(bbox=ZXWD_REQION)

            # Get Question Number
            index_region = (50, 220, 165, 242)
            image_index = ImageGrab.grab(bbox=index_region)  # 1.截取图片
            im = image_index.convert('L')  # 2.将彩色图像转化为灰度图
            binaryImage = im.point(AutomaticAnswering.initTable(), '1')  # 3.降噪，图片二值化
            character_index = pytesseract.image_to_string(binaryImage, lang="chi_sim+eng", config='--psm 7')
            LOG.debug("Read index from image: \n{0}".format(character_index))

            try:
                image_all.save(os.path.join(self.question_dir, character_index + ".png"))
            except Exception as e:
                LOG.error("Save Image error: {0}".format(str(e)))

            # Get Question
            question_region = (50, 245, 430, 325)
            image_question = ImageGrab.grab(bbox=question_region)

            character_question = pytesseract.image_to_string(image_question, lang="chi_sim+eng", config='--psm 4')
            LOG.debug("Read question from image: \n{0}".format(character_question))

            list = character_question.split('\n\n')
            list[0] = list[0].replace("\n", "")
            question = list[0]
            LOG.debug("Question:\n{0}".format(question))

            # Get Answer
            answers_region = (40, 370, 440, 570)
            image_answers = ImageGrab.grab(bbox=answers_region)
            image_answers = image_answers.convert('L')
            binaryAnswerImage = image_answers.point(AutomaticAnswering.initTable(), '1')

            character_answers = pytesseract.image_to_string(binaryAnswerImage, lang="chi_sim+eng", config='--psm 4')
            LOG.debug("Read question from image: \n{0}".format(character_answers))
        else:
            return

        url = AutomaticAnswering.search(question)
        LOG.debug("Search Url: {0}".format(url))

        webbrowser.open_new_tab(url)



if __name__ == "__main__":
    print("Automatic Answering")
    automaticAnswering = AutomaticAnswering(1)
    automaticAnswering.grabScreen(1)