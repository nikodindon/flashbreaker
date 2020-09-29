#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pyscreenshot as ImageGrab
import pytesseract
import webbrowser
import random
import re
import string
import mss
import mss.tools
import ConfigParser
import sys
from unidecode import unidecode
from HTMLParser import HTMLParser
from PIL import ImageEnhance, ImageFilter
from PIL import Image as ImageScreen
from time import sleep, time, strftime
from requests import get
from bs4 import BeautifulSoup as Soup
from nltk.corpus import stopwords
from datetime import datetime
#from tkinter import *

def run_cash_show_assistant():

	#Fonction de grab V2
	def grab_part(left, top, right, bottom):
		width = right - left
		height = bottom - top
		with mss.mss() as sct:
			# The screen part to capture
			monitor = {'top': top, 'left': left, 'width': width, 'height': height}
			# Grab the data
			sct_img = sct.grab(monitor)
			# Create an Image
			img = ImageScreen.frombytes('RGB', sct_img.size, sct_img.bgra, 'raw', 'BGRX')
			#img.show()  #debug pour afficher l'image découpée
			return img

	#Fonction de preprocessing de l'image
	def pre_process_image(img):
		img = img.convert('L')
		enhancer = ImageEnhance.Contrast(img)
		img = enhancer.enhance(2)
		enhancer = ImageEnhance.Sharpness(img)
		img = enhancer.enhance(2)
		img = img.resize(tuple([2*x for x in img.size]),ImageScreen.LANCZOS) #LANCZOS ou ANTIALIAS
		#img.show()      #debug pour afficher l'image après traitement
		return img

	#Fonction de lecture OCR
	def convert_image_to_text(img,file):
		img.save('temp.png')
		#img.save(file+".tiff")   #debug pour afficher l'image avant traitement OCR
		text = pytesseract.image_to_string(ImageScreen.open('temp.png'),config='--psm 6 --lang fra+deu+eng') # --oem 0
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
		for word in answer_arr:
			counter = counter + html_str.count(word)
		return counter

	#Fonction de lecture des coordonnées des Q/R
	def lect_info_jeu():
		for i in range(5):   #On part sur 1 question + 4 reponses max, soit 5 coordonnees
			coord.append([0] * 4) #Ajoute 4 colonnes de 5 entiers(int) ayant pour valeurs 0
		#coordonnées question
		coord[0][0] = int(cfg.get(nom_jeu, 'q_x1'))   #x1
		coord[0][1] = int(cfg.get(nom_jeu, 'q_y1'))   #y1
		coord[0][2] = int(cfg.get(nom_jeu, 'q_x2'))   #x2
		coord[0][3] = int(cfg.get(nom_jeu, 'q_y2'))   #y2
		#print(coord[0])  #debug Affichage des coordonnées lues pour la question
		#coordonnées réponses
		for ind in list_rep:
			coord[ind][0] = int(cfg.get(nom_jeu, 'r'+str(ind)+'_x1'))
			coord[ind][1] = int(cfg.get(nom_jeu, 'r'+str(ind)+'_y1'))
			coord[ind][2] = int(cfg.get(nom_jeu, 'r'+str(ind)+'_x2'))
			coord[ind][3] = int(cfg.get(nom_jeu, 'r'+str(ind)+'_y2'))
			#print(coord[ind])  #debug Affichage des coordonnées lues pour les réponses

	"""def lect_ini_liste_jeux():
		cfg = ConfigParser.ConfigParser()
		cfg.read('param_games.ini')
		fenetre = Tk()  #fenetre
		# liste des jeux
		liste = Listbox(fenetre)
		mylist = [1,2,3,4,5,6,7,8,9]
		for ind in mylist:
			try:
				jeu = cfg.get('JEUX', 'jeu'+str(ind))
				jeu_lib = cfg.get(jeu,'libelle')
				liste.insert(ind, str(ind)+' - '+jeu_lib)
			except:
				break;
			print(jeu_lib)
		
		liste.pack()
		fenetre.mainloop()
		print(liste.curselection())"""

	#Début effectif du programme
	reload(sys)
	sys.setdefaultencoding("UTF-8")
	
	#Ouverture du fichier de log (au moins pour les debut/fin)
	text_file = open("Output.txt", "a")
	text_file.write("\n==== lancement "+str(datetime.now())+" ====\n")      #log
	f_debug = 1 #activation du log
	
	#nom_jeu = 'CS_FR'
	nom_jeu = 'FLASHBREAK'
	#nom_jeu = 'QUIDOL'
	#nom_jeu = 'HQ'
	#lect_ini_liste_jeux()

	coord = []    #Cette liste contiendra les coordonnées des différentes Q/R
	csAnswer = [] #Liste des images des réponses
	answer = []   #Liste des textes des réponses (après passage OCR)
	count = []    #Liste des scores
	
	#Ouverture et lecture du fichier de paramétrage
	cfg = ConfigParser.ConfigParser()
	cfg.read('param_games.ini')
	nb_rep = int(cfg.get(nom_jeu, 'nb_rep'))
	list_rep = range(1,nb_rep+1)
	print("Jeu en Cours : "+ cfg.get(nom_jeu, 'libelle')+"\n")
	lect_info_jeu()

	#Screenshots
	if f_debug == 1:
		text_file.write("===== debut grab V2 "+str(datetime.now())+" ====\n")      #log
	csQuestion = grab_part(coord[0][0],coord[0][1],coord[0][2],coord[0][3])
	csAnswer.append(ImageScreen.new('RGB',(1,1)))   #Image vide pour ne pas utiliser l'index 0
	for ind in list_rep:
		csAnswer.append(grab_part(coord[ind][0],coord[ind][1],coord[ind][2],coord[ind][3]))
	if f_debug == 1:
		text_file.write("===== fin grab V2 "+str(datetime.now())+" ====\n")      #log

	#Preprocessing des images
	if f_debug == 1:
		text_file.write("===== debut preprocess "+str(datetime.now())+" ====\n")      #log
	csQuestion = pre_process_image(csQuestion)
	for ind in list_rep:
		csAnswer[ind] = pre_process_image(csAnswer[ind])
	if f_debug == 1:
		text_file.write("===== fin preprocess "+str(datetime.now())+" ====\n")      #log

	#Lecture OCR
	if f_debug == 1:
		text_file.write("===== debut OCR "+str(datetime.now())+" ====\n")      #log
	question = convert_image_to_text(csQuestion,"q1")
	question = unidecode(question.split("?", 1)[0])
	print("Q : "+question)
	answer.append(" ")   #enregistrement vide pour ne pas utiliser l'index 0
	for ind in list_rep:
		temp = convert_image_to_text(csAnswer[ind],"r"+str(ind)).strip().lower()
		temp = unidecode(temp)
		temp = re.sub(r'[^\w\s]', ' ',temp)
		answer.append(temp)
		print("R"+str(ind)+": "+answer[ind])
	
	if f_debug == 1:
		text_file.write("Q : "+question+"\n")  #log
		for ind in list_rep:
			text_file.write("R"+str(ind)+": "+answer[ind]+"\n")   #log
		text_file.write("===== fin OCR "+str(datetime.now())+" ====\n")      #log

	#exit() #pour ne pas faire la recherche web
		
	# -------------- Testing -----------------
	"""
	question = "Comment s'appelle le Schtroumpf qui offre des cadeaux qui explosent au visage de leurs destinataires"
	answer[1] = "schtroumpf terroriste"
	answer[2] = "schtroumpf rigolo"
	answer[3] = "schtroumpf farceur"
	answer[4] = "schtroumpf blagueur"
	"""
	# ---------------------------------------

	question = question.replace(" ", "+")
	question = question.replace("&", "%26")

	responseFromQuestion = get("https://google.com/search?q=" + question)
	h = HTMLParser()
	html = responseFromQuestion.text.lower()
	html = clean_html(html)

	# Count instances of answer and lower-case answer
	count.append(int(0))   #enregistrement vide pour ne pas utiliser l'index 0
	total = 0
	for ind in list_rep:
		count.append(html.count(answer[ind]))
		count[ind] = count[ind] + hash_count(html, answer[ind])
		if count[ind] > 2000:
			count[ind] = 0
		total = total + count[ind]  #comptage total 

	# Write to logfile to see HTML
	#if f_debug == 1:
		#text_file.write(html+"\n")

	#Affichage des scores des différentes réponses
	print("=============================")
	for ind in list_rep:
		print("Score pour R"+str(ind)+" : "+str(count[ind]))
	print("ATTENTION SI QUESTION AVEC NEGATION PRIVILEGIER LE SCORE LE PLUS BAS OU A ZERO")
	print("=============================")
	if f_debug == 1:
		for ind in list_rep:
			text_file.write("Score pour R"+str(ind)+" : "+str(count[ind])+"\n")   #log
	
	#Affichage de la meilleure réponse
	if total == 0:
		print("Il n'y a aucune reponse trouvee. Probleme de lecture Q/R ?")
		if f_debug == 1:
			text_file.write("Il n'y a aucune réponse trouvée. Problème de lecture Q/R ? "+str(datetime.now())+" ====\n")        #log
	else:
		minCount = min(count)
		maxCount = max(count)
		#Test d'une négation
		if question.find("+not+") != -1 or question.find("+NOT+") != -1 or \
		   question.find("+n'est+pas+") != -1 or question.find("+n'a+pas+") != -1 or \
		   question.find("+n'a+jamais+") != -1 or question.find("+n'existe+pas+") != -1 :
			for ind in list_rep:
				if minCount == count[ind]:
					print("NEGATION DETECTEE, A CONFIRMER")
					print("La reponse est : "+str(ind)+" - " + answer[ind])
					if f_debug == 1:
						text_file.write("NEGATION DETECTEE, A CONFIRMER")   #log
						text_file.write("La reponse est : "+str(ind)+" - " + answer[ind]+"\n")        #log
		else:
			for ind in list_rep:
				if maxCount == count[ind]:
					print("La reponse est : "+str(ind)+" - " + answer[ind])
					if f_debug == 1:
						text_file.write("La reponse est : "+str(ind)+" - " + answer[ind]+"\n")        #log

	#Fermeture du fichier de log
	text_file.write("===== fermeture "+str(datetime.now())+" ====\n")      #log
	text_file.close

if __name__ == '__main__':
	run_cash_show_assistant()
