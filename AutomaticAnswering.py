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
    "DDXQ", # 答答星球
    "ZXWD"  # 诸仙问道
]
DDXQ = 0


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

    def grabScreen(self,index):
        LOG.debug("Grab Question {0}".format(index))
        txt_name = str(index) + ".txt"
        image_name = str(index) + ".png"
        if self.activity == DDXQ:
            image = ImageGrab.grab(bbox=AutomaticAnswering.DDXQ_REGION)
            image.save(os.path.join(self.question_dir, image_name))

        character = pytesseract.image_to_string(image, lang="chi_sim+eng", config='--psm 4')
        LOG.debug("Read from image: \n{0}".format(character))
        if self.activity == DDXQ:
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

        url = AutomaticAnswering.search(question)
        LOG.debug("Search Url: {0}".format(url))

        # browser = webdriver.Chrome("C:\Program Files (x86)\Google\Chrome\Application\chrome.exe")
        # browser.get(url)
        # browser.find_element_by_id("kw").send_keys(u"{0}".format(question))
        # browser.find_element_by_id("su").click()
        # time.sleep(20)
        # browser.quit()

        webbrowser.open_new_tab(url)


if __name__ == "__main__":
    print("Automatic Answering")
    automaticAnswering = AutomaticAnswering(0)
    automaticAnswering.grabScreen(1)