#!/usr/bin/env python
# coding: utf-8

import pyscreenshot as ImageGrab
import pytesseract
import webbrowser
import random
import re
import string
import mss
import mss.tools
import requests
from unidecode import unidecode
from HTMLParser import HTMLParser
from PIL import Image, ImageEnhance, ImageFilter
from time import sleep, time, strftime
from requests import get
from bs4 import BeautifulSoup as Soup
from nltk.corpus import stopwords
from datetime import datetime

def run_cash_show_assistant():

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

	#Fonction de preprocessing de l'image
	def pre_process_image(img):
		enhancer = ImageEnhance.Sharpness(img)
		img = enhancer.enhance(2.5)
		#enhancer = ImageEnhance.Contrast(img)
		#img = enhancer.enhance(3)
		img = img.convert('L')
		#img.show()      #Pour afficher l image decoupee
		return img

	#Fonction de lecture OCR
	def convert_image_to_text(img):
		img.save('temp.png')
		text = pytesseract.image_to_string(Image.open('temp.png'))
		text = text.replace("\n", " ")
		return text

	#Fonction du suppression des caractères superflus
	def clean_html(html):
		# Change HTML to punctuation encoding to actul punctuation
		html = h.unescape(html)
		html = clean_me(html)

		# Get rid of HTML tags in HTML output
		cleanr = re.compile('<.*?>')
		html = re.sub(cleanr, '', html)
		html = re.sub(r'[^\w\s]', '',html)
		return html

	#Fonction de netoyage des informations reçues
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

	#Fonction de comptage des réponses dans le flux reçu
	def hash_count(html_str, answer):
		#filter out stop words in answers
		stop_words = stopwords.words('french')
		counter = 0
		answer_arr = answer.split()
		answer_arr = [w for w in answer_arr if not w in stop_words]
		#print(answer_arr)
		for word in answer_arr:
			counter = counter + html_str.count(word)
		return counter
	
	#Début effectif du programme
	
	f_debug = 1 #activation du log
	
	#Ouverture du fichier de log (au moins pour les debut/fin)
	text_file = open("Output.txt", "a")
	text_file.write("\n==== lancement "+str(datetime.now())+" ====\n")      #log



	#if f_debug == 1:
	#	text_file.write("===== debut grab V2 "+str(datetime.now())+" ====\n")      #log
	csQuestion = grab_part(45,350, 410, 470)
	csAnswer1 = grab_part(70,510,390,560)
	csAnswer2 = grab_part(70,595,390,640)
	csAnswer3 = grab_part(70,670,390,715)
	#if f_debug == 1:
	#	text_file.write("===== fin grab V2 "+str(datetime.now())+" ====\n")      #log

	#Preprocessing des images
	#if f_debug == 1:
	#	text_file.write("===== debut preprocess "+str(datetime.now())+" ====\n")      #log
	csQuestion = pre_process_image(csQuestion)
	csAnswer1 = pre_process_image(csAnswer1)
	csAnswer2 = pre_process_image(csAnswer2)
	csAnswer3 = pre_process_image(csAnswer3)
	#if f_debug == 1:
	#	text_file.write("===== fin preprocess "+str(datetime.now())+" ====\n")      #log
	
	question = convert_image_to_text(csQuestion)
	question = unidecode(question.split("?", 1)[0])
	answer1 = unidecode(convert_image_to_text(csAnswer1).strip().lower())
	answer2 = unidecode(convert_image_to_text(csAnswer2).strip().lower())
	answer3 = unidecode(convert_image_to_text(csAnswer3).strip().lower())
	answer1 = re.sub(r'[^\w\s]', '',answer1)
	answer2 = re.sub(r'[^\w\s]', '',answer2)
	answer3 = re.sub(r'[^\w\s]', '',answer3)
	
	question = question.replace(" ", "+")
	question = question.replace("&", "%26")
	
	

	if f_debug == 1:
		text_file.write("Q : "+question+"\n")  #log
		text_file.write("R1: "+answer1+"\n")   #log
		text_file.write("R2: "+answer2+"\n")   #log
		text_file.write("R3: "+answer3+"\n")   #log
		#text_file.write("===== fin OCR "+str(datetime.now())+" ====\n")      #log




	responseFromQuestion = get("https://google.com/search?q=" + question)
	h = HTMLParser()
	html = responseFromQuestion.text.lower()
	html = clean_html(html)

	count1 = html.count(answer1)
	count2 = html.count(answer2)
	count3 = html.count(answer3)

	count1 = count1 + hash_count(html, answer1)
	count2 = count2 + hash_count(html, answer2)
	count3 = count3 + hash_count(html, answer3)


	print ""
	print count1
	print count2
	print count3
	print ""

	if f_debug == 1:
		text_file.write(str(count1)+"\n")   #log
		text_file.write(str(count2)+"\n")   #log
		text_file.write(str(count3)+"\n")   #log

	if count1 == count2 and count2 == count3 and (count1 == 0 or count1 >2000):
		print("Il n'y a aucune réponse trouvée. Problème de lecture Q/R ?")
		if f_debug == 1:
			text_file.write("Il n'y a aucune réponse trouvée. Problème de lecture Q/R ? "+str(datetime.now())+" ====\n")        #log		
	else:
		if question.find("+not+") != -1 or question.find("+NOT+") != -1 or question.find("+n'est+pas+") != -1 or question.find("+n'a+pas+") != -1:
			minCount = min(count1, count2, count3)
			if minCount == count1:
				print("La reponse est : 1 - " + answer1)
				if f_debug == 1:
					text_file.write("La reponse est : 1 - "+answer1)        #log
			if minCount == count2:
				print("La reponse est : 2 - " + answer2)
				if f_debug == 1:
					text_file.write("La reponse est : 2 - "+answer2)        #log
			if minCount == count3:
				print("La reponse est : 3 - " + answer3)
				if f_debug == 1:
					text_file.write("La reponse est : 3 - "+answer3)        #log
		else:
			maxCount = max(count1, count2, count3)
			if maxCount == count1:
				print("La reponse est : 1 - " + answer1)
				if f_debug == 1:
					text_file.write("La reponse est : 1 - "+answer1)        #log
			if maxCount == count2:
				print("La reponse est : 2 - " + answer2)
				if f_debug == 1:
					text_file.write("La reponse est : 2 - "+answer2)        #log
			if maxCount == count3:
				print("La reponse est : 3 - " + answer3)
				if f_debug == 1:
					text_file.write("La reponse est : 3 - "+answer3)        #log
					

	answer1 = answer1.replace(" ", "+")
	answer1 = answer1.replace("&", "%26")
	
	answer2 = answer2.replace(" ", "+")
	answer2 = answer2.replace("&", "%26")
	
	answer3 = answer3.replace(" ", "+")
	answer3 = answer3.replace("&", "%26")
	
	print ""
	print("Q : "+question)
	print ""
	print("R1: "+answer1)
	print("R2: "+answer2)
	print("R3: "+answer3)
	
	print ""
	print "nombres de resultats : "
	print ""
	
	r1 = requests.get("https://www.google.com/search", params={'q':question+ " " + answer1 })
	r2 = requests.get("https://www.google.com/search", params={'q':question+ " " + answer2 })
	r3 = requests.get("https://www.google.com/search", params={'q':question+ " " + answer3 })

	soup = Soup(r1.text, "lxml")
	res1 = soup.find("div", {"id": "resultStats"})
	soup = Soup(r2.text, "lxml")
	res2 = soup.find("div", {"id": "resultStats"})
	soup = Soup(r3.text, "lxml")
	res3 = soup.find("div", {"id": "resultStats"})
	
	
	print "Q+R1 : "+res1.text
	print "Q+R2 : "+res2.text
	print "Q+R3 : "+res3.text
	text_file.write("===== fermeture "+str(datetime.now())+" ====\n")      #log
	text_file.close

if __name__ == '__main__':
	run_cash_show_assistant()
