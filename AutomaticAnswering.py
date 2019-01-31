# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals

import pytesseract
from PIL import Image



if __name__ == "__main__":
    print("Automatic Answering")
    image = Image.open("Images\\c.png")
    code = pytesseract.image_to_string(image, lang="chi_sim", config="-psm 6")
    print(code)