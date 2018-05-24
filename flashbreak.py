import pyscreenshot as ImageGrab
import pytesseract
import webbrowser
import random
import re
import string
from unidecode import unidecode
from HTMLParser import HTMLParser
from PIL import Image, ImageEnhance, ImageFilter
from time import sleep, time
from requests import get
from bs4 import BeautifulSoup as Soup
from nltk.corpus import stopwords

def run_cash_show_assistant():
	#if __name__ == '__main__':
	csQuestion = ImageGrab.grab(bbox=(45,326, 411, 482))
	csAnswer1 = ImageGrab.grab(bbox=(71,508,384,547))
	csAnswer2 = ImageGrab.grab(bbox=(74,576,385,618))
	csAnswer3 = ImageGrab.grab(bbox=(72,644,387,686))
	csAnswer4 = ImageGrab.grab(bbox=(72,644,387,686))
	#csQuestion.show()	

	# load the example image and pre-process to reduce noise
	# and increase contrast
	def pre_process_image(img):
		#img = img.filter(ImageFilter.MedianFilter())
		#enhancer = ImageEnhance.Contrast(img)
		#img = enhancer.enhance(2)
		#img = img.convert('1')
		#img.show()      #Pour afficher l image decoupee
		return img

	def convert_image_to_text(img):
		img.save('temp.bmp')
		text = pytesseract.image_to_string(Image.open('temp.bmp'))
		text = text.replace("\n", " ")
		return text

	def clean_html(html):
		# Change HTML to punctuation encoding to actul punctuation
		html = h.unescape(html)
		html = clean_me(html)

		# Get rid of HTML tags in HTML output
		cleanr = re.compile('<.*?>')
		html = re.sub(cleanr, '', html)
		html = re.sub(r'[^\w\s]', '',html)
		return html

	def clean_me(html):
	    soup = Soup(html, "html.parser") # create a new bs4 object from the html data loaded
	    for script in soup(["script", "style"]): # remove all javascript and stylesheet code
	        script.extract()
	    # get text
	    text = soup.get_text()
	    # break into lines and remove leading and trailing space on each
	    lines = (line.strip() for line in text.splitlines())
	    # break multi-headlines into a line each
	    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
	    # drop blank lines
	    text = '\n'.join(chunk for chunk in chunks if chunk)
	    return text

	"""def hash_count(html_str, answer):
		#filter out stop words in answers
		stop_words = ['the', 'a', 'an', 'is', 'are', 'to', 'from', 'in', 
		'and', 'as', 'at', 'be', 'by', 'for', 'from', 'has', 'he', 'it', 
		'its', 'of', 'on', 'that', 'to', 'was', 'were', 'will', 'with']
		counter = 0
		answer_arr = answer.split()
		answer_arr = [w for w in answer_arr if not w in stop_words]
		for word in answer_arr:
			counter = counter + html_str.count(word)
		return counter"""

	def hash_count(html_str, answer):
		#filter out stop words in answers
		stop_words = stopwords.words('english')
		counter = 0
		answer_arr = answer.split()
		answer_arr = [w for w in answer_arr if not w in stop_words]
		print(answer_arr)
		for word in answer_arr:
			counter = counter + html_str.count(word)
		return counter
		
	csQuestion = pre_process_image(csQuestion)
	question = convert_image_to_text(csQuestion)
	question = unidecode(question.split("?", 1)[0])
	print(question)

	csAnswer1 = pre_process_image(csAnswer1)
	csAnswer2 = pre_process_image(csAnswer2)
	csAnswer3 = pre_process_image(csAnswer3)
	csAnswer4 = pre_process_image(csAnswer4)
	answer1 = unidecode(convert_image_to_text(csAnswer1).strip().lower())
	answer2 = unidecode(convert_image_to_text(csAnswer2).strip().lower())
	answer3 = unidecode(convert_image_to_text(csAnswer3).strip().lower())
	answer4 = unidecode(convert_image_to_text(csAnswer4).strip().lower())
	answer1 = re.sub(r'[^\w\s]', '',answer1)
	answer2 = re.sub(r'[^\w\s]', '',answer2)
	answer3 = re.sub(r'[^\w\s]', '',answer3)
	answer4 = re.sub(r'[^\w\s]', '',answer4)

	print(answer1)
	print(answer2)
	print(answer3)
	print(answer4)

	# -------------- Testing -----------------

	# question = "Approximately when was the Bust of Nefertiti created"
	# answer1 = "1789 bc"
	# answer2 = "1345 bc"
	# answer3 = "62 ad"

	# ---------------------------------------

	question = question.replace(" ", "+")
	question = question.replace("&", "%26")

	responseFromQuestion = get("https://google.com/search?q=" + question)
	h = HTMLParser()
	html = responseFromQuestion.text.lower()
	html = clean_html(html)

	# Count instances of answer and lower-case answer
	count1 = html.count(answer1)
	count2 = html.count(answer2)
	count3 = html.count(answer3)
	count4 = html.count(answer4)

	# Count instances of answer using hash method
	count1 = count1 + hash_count(html, answer1)
	count2 = count2 + hash_count(html, answer2)
	count3 = count3 + hash_count(html, answer3)
	count4 = count4 + hash_count(html, answer4)

	# Write to file to see HTML
	#text_file = open("Output.txt", "w")
	#text_file.write(html)
	#text_file.close()

	"""if count1 == 0 and count2 == 0 and count3 == 0 and count4 == 0:
		print(" --------------------- ")
		print("RE-ATTEMPTING")
		count1 = hash_count(html, answer1)
		count2 = hash_count(html, answer2)
		count3 = hash_count(html, answer3)
		count4 = hash_count(html, answer4)"""

	print(count1)
	print(count2)
	print(count3)
	print(count4)

	if question.find("+not+") != -1 or question.find("+NOT+") != -1:
		minCount = min(count1, count2, count3 , count4)
		if minCount == count1:
			print("Answer is: 1 - " + answer1)
		if minCount == count2:
			print("Answer is: 2 - " + answer2)
		if minCount == count3:
			print("Answer is: 3 - " + answer3)
		if minCount == count4:
			print("Answer is: 3 - " + answer4)	
	else:
		maxCount = max(count1, count2, count3, count4)
		if maxCount == count1:
			print("Answer is: 1 - " + answer1)
		if maxCount == count2:
			print("Answer is: 2 - " + answer2)
		if maxCount == count3:
			print("Answer is: 3 - " + answer3)
		if maxCount == count4:
			print("Answer is: 3 - " + answer4)	

if __name__ == '__main__':
	run_cash_show_assistant()
