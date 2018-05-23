import pyscreenshot as ImageGrab
import pytesseract
import webbrowser
import random
import re
from unidecode import unidecode
from HTMLParser import HTMLParser
from PIL import Image, ImageEnhance, ImageFilter
from time import sleep
from requests import get
from bs4 import BeautifulSoup as Soup
from time import time
from flashbreak import run_flashbreak_assistant

while 1:
	print("Waiting for next question")
	sleep(1)
	csQuestion = ImageGrab.grab(bbox=(16,168, 342, 288))
	color = csQuestion.getpixel((20,20))
	if color == (255, 254, 255, 255):
		run_flashbreak_assistant()
		sleep(10)
