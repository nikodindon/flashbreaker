#import sys
import pyscreenshot as ImageGrab
import pytesseract
import webbrowser
import random
import re
import string
import mss
import mss.tools
from unidecode import unidecode
from HTMLParser import HTMLParser
from PIL import Image, ImageEnhance, ImageFilter
from time import sleep, time, strftime
from requests import get
from bs4 import BeautifulSoup as Soup
from nltk.corpus import stopwords
from datetime import datetime

def run_flashbreak_assistant():

        #Fonction de grab V2
	def grab_part(left, top, right, bottom):
		width = right - left
		height = bottom - top
		with mss.mss() as sct:
			# The screen part to capture
			monitor = {'top': top, 'left': left, 'width': width, 'height': height}
			#output = 'sct-{top}x{left}_{width}x{height}.png'.format(**monitor)
			# Grab the data
			sct_img = sct.grab(monitor)
			# Save to the picture file
			#mss.tools.to_png(sct_img.rgb, sct_img.size, output=output)
			#print(output)
			# Create an Image
			img = Image.new('RGB', sct_img.size)
			#Best solution: create a list(tuple(R, G, B), ...) for putdata()
			pixels = zip(sct_img.raw[2::4],
						 sct_img.raw[1::4],
						 sct_img.raw[0::4])
			img.putdata(list(pixels))
			#img.show()
			return img


	
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
		#text = pytesseract.image_to_string(Image.open('temp.png')).encode('utf8')
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

		
		
	"""reload(sys)
	sys.setdefaultencoding("UTF-8")"""
    
	#Ouverture du fichier de log
	f_debug = 1
	if f_debug == 1:
		text_file = open("Output.txt", "a")
		text_file.write("\n===== lancement "+str(datetime.now())+" ====\n")      #log


#Screenshots
	if f_debug == 1:
		text_file.write("===== debut grab V2 "+str(datetime.now())+" ====\n")      #log
	csQuestion = grab_part(34,327, 426, 420)
	csAnswer1 = grab_part(55,457,210,530)
	csAnswer2 = grab_part(250,450,410,530)
	csAnswer3 = grab_part(54,580,210,650)
	csAnswer4 = grab_part(250,575,410,650)

	if f_debug == 1:
		text_file.write("===== fin grab V2 "+str(datetime.now())+" ====\n")      #log


			
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

	print("Q : "+question)
	print("R1: "+answer1)
	print("R2: "+answer2)
	print("R3: "+answer3)
	print("R4: "+answer4)
                

	if f_debug == 1:
		text_file.write(question+"\n")  #log
		text_file.write(answer1+"\n")   #log
		text_file.write(answer2+"\n")   #log
		text_file.write(answer3+"\n")   #log
		text_file.write(answer4+"\n")   #log
		text_file.write("\n===== fin de l'ocr "+str(datetime.now())+" ====\n")      #log

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

	# Write to logfile to see HTML
	#if f_debug == 1:
		#text_file.write(html+"\n")

	"""if count1 == 0 and count2 == 0 and count3 == 0:
		print(" --------------------- ")
		print("RE-ATTEMPTING")
		count1 = hash_count(html, answer1)
		count2 = hash_count(html, answer2)
		count3 = hash_count(html, answer3)"""

	print(count1)
	print(count2)
	print(count3)
	print(count4)

	if f_debug == 1:
		text_file.write(str(count1)+"\n")   #log
		text_file.write(str(count2)+"\n")   #log
		text_file.write(str(count3)+"\n")   #log
		text_file.write(str(count4)+"\n")   #log

	
	if question.find("+not+") != -1 or question.find("+NOT+") != -1:
		minCount = min(count1, count2, count3, count4)
		if minCount == count1:
			print("La reponse est : 1 - " + answer1)
			if f_debug == 1:
                                text_file.write("La reponse est : 1 - "+answer1+" ====\n\n")        #log
		if minCount == count2:
			print("La reponse est : 2 - " + answer2)
			if f_debug == 1:
                                text_file.write("La reponse est : 1 - "+answer2+" ====\n\n")        #log
		if minCount == count3:
			print("La reponse est : 3 - " + answer3)
			if f_debug == 1:
                                text_file.write("La reponse est : 1 - "+answer3+" ====\n\n")        #log
		if minCount == count4:
			print("La reponse est : 4 - " + answer4)
			if f_debug == 1:
                                text_file.write("La reponse est : 1 - "+answer4+" ====\n\n")        #log
	else:
		maxCount = max(count1, count2, count3, count4)
		if maxCount == count1:
			print("La reponse est : 1 - " + answer1)
                        if f_debug == 1:
                                text_file.write("La reponse est : 1 - "+answer1+" ====\n\n")        #log
		if maxCount == count2:
			print("La reponse est : 2 - " + answer2)
			if f_debug == 1:
                                text_file.write("La reponse est : 1 - "+answer2+" ====\n\n")        #log
		if maxCount == count3:
			print("La reponse est : 3 - " + answer3)
			if f_debug == 1:
                                text_file.write("La reponse est : 1 - "+answer3+" ====\n\n")        #log
		if maxCount == count4:
			print("La reponse est : 4 - " + answer4)
			if f_debug == 1:
                                text_file.write("La reponse est : 1 - "+answer4+" ====\n\n")        #log

                if f_debug == 1:
                        text_file.write("===== fermeture "+str(datetime.now())+" ====\n\n")      #log
        		text_file.close()
			
if __name__ == '__main__':
	run_flashbreak_assistant()
