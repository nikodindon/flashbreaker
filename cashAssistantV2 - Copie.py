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
import win32gui
import win32ui
import win32con
from unidecode import unidecode
from HTMLParser import HTMLParser
from PIL import ImageEnhance, ImageFilter
from PIL import Image as ImageScreen
from time import sleep, time, strftime
from requests import get
from bs4 import BeautifulSoup as Soup
from nltk.corpus import stopwords
from datetime import datetime
from tkinter import *
import webbrowser
import concurrent.futures
from colorama import init
from termcolor import colored
import socket
import multiprocessing
from contextlib import closing

#from __future__ import unicode_literals   #Pour simuler Python 3 qui gère les str en utf8// évite de faire des unicode blabla

def run_cash_show_assistant(nom_jeu,num_quest):    #num_quest pour ouvrir onglet avec la recherche de la question ouverte pour la dernière question de QUIDOL

	f_debug = 2 #activation du log 0/1/2 => 2 Détaillé avec horodatages
	
	#Fonction de récupération de la fenêtre
	def _get_windows_bytitle(title_text, exact = True):
		def _window_callback(hwnd, all_windows):
			all_windows.append((hwnd, win32gui.GetWindowText(hwnd)))
		windows = []
		win32gui.EnumWindows(_window_callback, windows)
		if exact:
			return [hwnd for hwnd, title in windows if title_text == title]
		else:
			return [hwnd for hwnd, title in windows if title_text in title]
	
	#Fonction de screenshot de la fenêtre complète
	def screenshot(hwnd = None):
		if not hwnd:
			hwnd=win32gui.GetDesktopWindow()

		l,t,r,b=win32gui.GetWindowRect(hwnd)

		win32gui.SetForegroundWindow(hwnd)
		sleep(0.1) #lame way to allow screen to draw before taking shot

		return grab_part(l,t,r,b)
		
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
			img.save('ecranfull.png')
			return img

	def crop_zones(image,coord):
		left,top,right,bottom = coord.replace(" ","").split(",")
		box = (int(left), int(top), int(right), int(bottom))
		im = image.crop(box)
		#zone.show()
		return im
		
	#Fonction de preprocessing de l'image
	def pre_process_image(img):
		img = img.convert('L')
		enhancer = ImageEnhance.Contrast(img)
		img = enhancer.enhance(2)
		if nom_jeu == 'FLASHBREAK':
			enhancer = ImageEnhance.Sharpness(img)
			img = enhancer.enhance(2.5)
			img = img.resize(tuple([3*x for x in img.size]),ImageScreen.LANCZOS) #LANCZOS ou ANTIALIAS
		else:
			enhancer = ImageEnhance.Sharpness(img)
			img = enhancer.enhance(2.5)
			img = img.resize(tuple([3*x for x in img.size]),ImageScreen.LANCZOS) #LANCZOS ou ANTIALIAS
		enhancer = ImageEnhance.Sharpness(img)
		img = enhancer.enhance(2)
		#img.show()      #debug pour afficher l'image après traitement
		return img
		
	#Fonction de lecture OCR
	def convert_image_to_text(img,file):
		img.save(file+".png")   #debug pour afficher l'image avant traitement OCR
		if langue == 'german':
			text = pytesseract.image_to_string(ImageScreen.open(file+".png"),config='--psm 6 -l deu')
		else:
			text = pytesseract.image_to_string(ImageScreen.open(file+".png"),config='--psm 6 -l fra+eng')
		text = text.replace("\n", " ")
		return text
		
	def trt_img(indice):
		csAnswer[indice] = pre_process_image(crop_zones(image,str(coord[indice])))
		temp = convert_image_to_text(csAnswer[indice],"r"+str(indice)).strip().lower()
		if langue != 'german':
			if indice == 0:
				temp = unidecode(temp.split("?", 1)[0])
			else:
				temp = unidecode(temp)
				temp = re.sub(r'[^\w\s]', ' ',temp)
		answer[indice] = temp
		
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
		stop_words = stopwords.words(langue)
		counter = 0
		answer_arr = answer.split()
		answer_arr = [w for w in answer_arr if not w in stop_words]
		for word in answer_arr:
			if len(word) == 1 and len(answer_arr) == 1:           #La réponse ne contient qu'un caractère, on recherche le caractère seul
				counter = counter + html_str.count(" "+word+" ")  #pour ne pas compter les fins de mots
				counter = counter + html_str.count("\n"+word+" ") #pour prendre en compte les débuts de lignes de la recherche HTML
			else:
				if len(word) != 1 :                               #La réponse contient plusieurs mots, on ne recherche pas les caractères seuls
					counter = counter + html_str.count(" "+word)  #pour ne pas compter les fins de mots
					counter = counter + html_str.count("\n"+word) #pour prendre en compte les débuts de lignes de la recherche HTML
					if len(word) > 3 and word[0] == 'l':          #cas d'une lecture erronée de l'apostrophe, on exclue le L de debut de la recherche
						if word[0:2] == "l'":
							counter = counter + html_str.count(word[2:])
						else:
							counter = counter + html_str.count(word[1:])	
		return counter

	#Fonction de recherche de négation
	def is_negative():
		if langue == 'french':
			#list_neg=["pas","est+pas","a+pas","a+jamais","existe+pas","sera+pas","on+pas","il+pas"]
			list_neg=["+pas","jamais","aucun"]
		
		if langue == 'english':
			list_neg=["+not","never","none"]
		
		if langue == 'german':
			list_neg=["kein","keine","nicht","niemals","+nie"]
		
		for i in list_neg:
			if answer[0].lower().find(i+'+') != -1:
				print("NEGATION DETECTEE AVEC '"+i+"' - A CONFIRMER")
				add_log("NEGATION DETECTEE AVEC '"+i+"' - A CONFIRMER\n",1)
				return True;

		return False   #pas de negation definie pour cette langue
	
	def is_which():
		#return False   #Comme ça ne marche pas terrible pour le moment, on désactive hors tests
		if langue == 'french':
			list_which=["lequel","laquelle","lesquels","lesquelles","aucun"]
		
		if langue == 'english':
			list_which=["which"]
		
		if langue == 'german':
			list_which=["welche"]
		
		for i in list_which:
			if answer[0].lower().find(i) != -1:
				return True;

		return False   #pas de negation definie pour cette langue
	
	#Fonction de log. Verbosité 1 = court, 2 = plus détaillé (si f_debug=2)
	def add_log(mess,verb):
		if f_debug > 0:
			if verb == 1 or (verb == 2 and f_debug == 2):
				text_file.write(mess)
			#if verb == 2 and f_debug == 2 :
		#		text_file.write(mess)
	
	#Fonction de lecture des coordonnées des Q/R
	def lect_info_jeu():
		#lecture des coordonnées
		for ind in list_full:
			csAnswer.append(" ")
			answer.append(" ")
			if ind == 0:  #c'est la question
				box = cfg.get(nom_jeu, 'quest')
			else:
				box = cfg.get(nom_jeu, 'r'+str(ind))
			coord.append(box)

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
	
	if nom_jeu == 'bidon':    #bidouille pour permettre le lancement de cashAssistant en solo sans passer par le menu
		nom_jeu = 'CS_FR'
		#nom_jeu = 'FLASHBREAK'
		#nom_jeu = 'QUIDOL'
		#nom_jeu = 'WLQ'
		#nom_jeu = 'CCL'
		#nom_jeu = 'HQ'
		#nom_jeu = 'CS_DE'
		nom_jeu = 'CS_EN'    #Cash Show Anglophones (US/UK/AU)

	#Ouverture du fichier de log (au moins pour les debut/fin)
	if f_debug >= 1:
		text_file = open("Output"+nom_jeu+".txt", "a")
		add_log("\n==== lancement "+str(datetime.now())+" ====\n",1)      #log
			
	coord = []       #Cette liste contiendra les coordonnées des différentes Q/R
	csAnswer = []    #Liste des images des réponses
	answer = []      #Liste des textes des réponses (après passage OCR)
	count = []       #Liste des scores
	rep_exact = []   #Liste de nombre de réponses exactes
	#init(autoreset=True)
	
	#Ouverture et lecture du fichier de paramétrage
	cfg = ConfigParser.ConfigParser()
	cfg.read('param_games.ini')
	nb_rep = int(cfg.get(nom_jeu, 'nb_rep'))
	langue = cfg.get(nom_jeu, 'langue')
	list_full= range(0,nb_rep+1)  #liste avec la question en arg 0
	list_rep = range(1,nb_rep+1)  #liste de réponses seulement

	print("Jeu en Cours : "+ cfg.get(nom_jeu, 'libelle'))
	lect_info_jeu()
	
	#Screenshots
	start_time = time()
	add_log("===== debut screenshot "+str(datetime.now())+" ====\n",2)      #log
	window_handle = _get_windows_bytitle("ApowerMirror")[0]
	image = screenshot(window_handle)
	
	add_log("===== fin screenshot "+str(datetime.now())+" ====\n",2)      #log

	#Traitement des Q/R (decoupage+preprocess+lecture OCR)
	add_log("===== debut traitment Q/R "+str(datetime.now())+" ====\n",2)      #log

	NUM_WORKERS = nb_rep+1
	with concurrent.futures.ThreadPoolExecutor(max_workers=NUM_WORKERS) as executor:
		futures = {executor.submit(trt_img, ind) for ind in range(NUM_WORKERS)}
		concurrent.futures.wait(futures)
		
	"""with closing(multiprocessing.Pool(processes=NUM_WORKERS)) as pool:
		pool.map_async(trt_img, list_full)
		#results.wait()"""
	
	for ind in list_full:	
		if ind == 0:
			entete = 'Q : '
		else:
			entete = 'R'+str(ind)+': '

		print(entete+answer[ind])
		if f_debug >= 1:
			add_log(entete+answer[ind]+"\n",1)  #log
	
	end_time = time() 
	print("Duree grab + OCR concurrent : %ssecs" % (end_time - start_time))
	add_log("===== fin traitment Q/R "+str(datetime.now())+" ====\n",2)      #log
	
	#exit() #pour ne pas faire la recherche web
		
	# -------------- Testing -----------------
	"""
	question = "Which of these US states does NOT contain a town called Springfield"
	answer[1] = "montana"
	answer[2] = "maine"
	answer[3] = "michigan"
	#answer[4] = "don camillo contre peppone"
	"""
	# ---------------------------------------
    #Gérer les STOPWORDS sur la question pour simplifier la rechercher ?
	# Write to logfile to see HTML
	#add_log(question+"\n",2)    #log

	start_time2 = time()
	
	answer[0] = answer[0].replace("&", "%26")
	
	if is_which():   #Question du type "Lequel"
		print("question lequel")
		add_log("question lequel",1)
		stop_words = stopwords.words(langue)
		quest_arr = answer[0].split()
		quest_arr = [w for w in quest_arr if not w in stop_words]
		quest_light = '+'.join(quest_arr)

		answer[0] = answer[0].replace(" ", "+")
		#for ind in list_rep:
		#	responseFromQuestion = get("https://google.com/search?q=" + question + "&num=30")
		
		# Count instances of answer and lower-case answer
		count.append(int(0))   #enregistrement vide pour ne pas utiliser l'index 0
		rep_exact.append(int(0))
		total = 0
		for ind in list_rep:
			responseFromQuestion = get("https://google.com/search?q=" + quest_light + " " + answer[ind] + "&num=5")
			h = HTMLParser()
			html = responseFromQuestion.text.lower()
			html = clean_html(html)
			
			count.append(hash_count(html, answer[ind]))   #Si réponse exacte trouvée, on la met en avant !
			if count[ind] > 2000:                         #Si un gros score lors du hash_count, peut être un problème de recherche (réponse composée de plusieurs mots)
				count[ind] = 0
			rep_exact.append(html.count(answer[ind]))
			count[ind] = count[ind] + rep_exact[ind]
			total = total + count[ind]  #comptage total 
	else: #question classique
		answer[0] = answer[0].replace(" ", "+")
	
		#webbrowser.open("https://google.com/search?q=" + question,new=1)
		responseFromQuestion = get("https://google.com/search?q=" + answer[0] + "&num=25")
		h = HTMLParser()
		html = responseFromQuestion.text.lower()
		html = clean_html(html)
		#add_log("\n\n\n"+html+"\n\n\n",2)   #log
	
		# Count instances of answer and lower-case answer
		count.append(int(0))   #enregistrement vide pour ne pas utiliser l'index 0
		rep_exact.append(int(0))
		total = 0
		for ind in list_rep:
			count.append(hash_count(html, answer[ind]))   #Si réponse exacte trouvée, on la met en avant !
			if count[ind] > 2000:                         #Si un gros score lors du hash_count, peut être un problème de recherche (réponse composée de plusieurs mots)
				count[ind] = 0
			rep_exact.append(html.count(answer[ind]))
			count[ind] = count[ind] + rep_exact[ind]
			total = total + count[ind]  #comptage total 

	#Affichage des scores des différentes réponses
	print("=============================")
	for ind in list_rep:
		if rep_exact[ind] == 0:
			print("Score pour R"+str(ind)+" : "+str(count[ind]))
		else:
			print("Score pour R"+str(ind)+" : "+str(count[ind])+" dont "+str(rep_exact[ind])+" rep EXACTE(S) trouvee(s)")
	print("ATTENTION SI QUESTION AVEC NEGATION PRIVILEGIER LE SCORE LE PLUS BAS OU A ZERO")
	print("=============================")
	if f_debug >= 1:
		for ind in list_rep:
			if rep_exact[ind] == 0:
				add_log("Score pour R"+str(ind)+" : "+str(count[ind])+"\n",1)    #log
			else:
				add_log("Score pour R"+str(ind)+" : "+str(count[ind])+" dont "+str(rep_exact[ind])+" rep EXACTE(S) trouvee(s)\n",1) #log
	
	#Affichage de la meilleure réponse
	if total == 0:
		print("Il n'y a aucune reponse trouvee. Probleme de lecture Q/R ?")
		add_log("Il n'y a aucune réponse trouvée. Problème de lecture Q/R ? "+str(datetime.now())+" ====\n",1)        #log
	else:
		del count[0]      #suppression de l'index 0 le temps de récupérer le meilleur score
		minCount = min(count)
		maxCount = max(count)
		count.insert(0,0) #on remet l'index 0
		
		del rep_exact[0]      #suppression de l'index 0 le temps de récupérer le meilleur score exacte
		minCount_exact = min(rep_exact)
		maxCount_exact = max(rep_exact)
		rep_exact.insert(0,0) #on remet l'index 0
		
		#Test d'une négation
		if is_negative() :
			for ind in list_rep:
				if minCount_exact == rep_exact[ind] and minCount == count[ind] and maxCount_exact >= 0:  #Minimum exact ET Minimum hash c est la bonne réponse
					print(colored("La reponse est : "+str(ind)+" - " + answer[ind],'green'))
					add_log("La reponse est : "+str(ind)+" - " + answer[ind]+"\n",1)        #log
				else: 
					if minCount_exact == rep_exact[ind]:     #Minimum exact
						print(colored("La reponse est : "+str(ind)+" - " + answer[ind],'yellow'))
						add_log("La reponse est : "+str(ind)+" - " + answer[ind]+"\n",1)        #log
					else:
						if minCount == count[ind]:    #Minimum hash
							print(colored("La reponse est : "+str(ind)+" - " + answer[ind],'red'))
							add_log("La reponse est : "+str(ind)+" - " + answer[ind]+"\n",1)        #log
		else:
			for ind in list_rep:
				if maxCount_exact == rep_exact[ind] and maxCount == count[ind] and maxCount_exact >= 0:  #Maximum exact ET Maximum hash c est la bonne réponse
					print(colored("La reponse est : "+str(ind)+" - " + answer[ind],'green'))
					add_log("La reponse est : "+str(ind)+" - " + answer[ind]+"\n",1)        #log
				else:
					if maxCount_exact == rep_exact[ind] and maxCount_exact >= 0:     #Maximum exact
						print(colored("La reponse est : "+str(ind)+" - " + answer[ind],'yellow'))
						add_log("La reponse est : "+str(ind)+" - " + answer[ind]+"\n",1)        #log
					else:
						if maxCount == count[ind]:    #Maximum hash
							print(colored("La reponse est : "+str(ind)+" - " + answer[ind],'red'))
							add_log("La reponse est : "+str(ind)+" - " + answer[ind]+"\n",1)        #log

	end_time2 = time() 
	print("Duree recherche : %ssecs" % (end_time2 - start_time2))
	print("Duree totale    : %ssecs" % (end_time2 - start_time))
	
	#Fermeture du fichier de log
	if f_debug >= 1:
		add_log("===== fermeture "+str(datetime.now())+" ====\n",1)      #log
		text_file.close

if __name__ == '__main__':
	run_cash_show_assistant('bidon',0)
