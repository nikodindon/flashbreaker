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
import webbrowser
import concurrent.futures
from colorama import init
from termcolor import colored
#from __future__ import unicode_literals   #Pour simuler Python 3 qui gère les str en utf8// évite de faire des unicode blabla

def run_cash_show_assistant(nom_jeu,num_quest):    #num_quest pour ouvrir onglet avec la recherche de la question ouverte pour la dernière question de QUIDOL

	f_debug = 1 #activation du log 0/1/2 => 2 Détaillé avec horodatages
	
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
		if nom_jeu == 'FLASHBREAK':
			enhancer = ImageEnhance.Sharpness(img)
			img = enhancer.enhance(2)
			img = img.resize(tuple([2*x for x in img.size]),ImageScreen.LANCZOS) #LANCZOS ou ANTIALIAS
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
		img.save('temp.png')
		#img.save(file+".tiff")   #debug pour afficher l'image avant traitement OCR
		if langue == 'german':
			text = pytesseract.image_to_string(ImageScreen.open('temp.png'),config='--psm 6 -l deu')
		else:
			text = pytesseract.image_to_string(ImageScreen.open('temp.png'),config='--psm 6 -l fra+eng')
		text = text.replace("\n", " ")
		return text

		
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
			
			
	reload(sys)
	sys.setdefaultencoding("UTF-8")
	
	nom_jeu = 'CS_EN'
	
	coord = []       #Cette liste contiendra les coordonnées des différentes Q/R
	csAnswer = []    #Liste des images des réponses
	answer = []      #Liste des textes des réponses (après passage OCR)
	count = []       #Liste des scores
	rep_exact = []   #Liste de nombre de réponses exactes
	
	
	cfg = ConfigParser.ConfigParser()
	cfg.read('param_games.ini')
	
	nb_rep = int(cfg.get(nom_jeu, 'nb_rep'))
	langue = cfg.get(nom_jeu, 'langue')
	
	list_rep=range(1,nb_rep+1)

	print("Jeu en Cours : "+ cfg.get(nom_jeu, 'libelle'))
	
	lect_info_jeu()
	
	csQuestion = grab_part(coord[0][0],coord[0][1],coord[0][2],coord[0][3])
	
	csAnswer.append(ImageScreen.new('RGB',(1,1)))   #Image vide pour ne pas utiliser l'index 0
	
	for ind in list_rep:
		csAnswer.append(grab_part(coord[ind][0],coord[ind][1],coord[ind][2],coord[ind][3]))
	

if __name__ == '__main__':
	run_cash_show_assistant('bidon',0)
	
	
	
	
