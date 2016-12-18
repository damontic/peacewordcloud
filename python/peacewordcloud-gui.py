# -*- coding: utf-8 -*-

# Standard Library Imports
import os
import sys

# Tkinter imports
from tkinter import Tk
from tkinter.filedialog import askopenfilename
from tkinter.filedialog import asksaveasfilename
from tkinter.messagebox import showinfo
from tkinter.messagebox import showerror
from tkinter.messagebox import askyesno
from tkinter.simpledialog import askinteger

# peacewordcloud imports
import peacewordcloud

if __name__ == '__main__':

	Tk().withdraw() # we don't want a full GUI, so keep the root window from appearing

	showinfo("peacewordcloud-gui", "Welcome to peacewordcloud-gui.")

	showinfo("Select a PDF", "Please select the pdf you are going to work with.")
	pdf_file = askopenfilename() # show an "Open" dialog box and return the path to the selected file
	if len(pdf_file) == 0 or not os.path.isfile(pdf_file):
		showerror("Error", "Invalid PDF file selected.")
		sys.exit()
	print("PDF file:", pdf_file)

	showinfo("Select a Base Image", "Please select the image you want to use to generate the wordcloud.")
	base_file = askopenfilename() # show an "Open" dialog box and return the path to the selected file
	if len(base_file) == 0 or not os.path.isfile(base_file):
		showerror("Error", "Invalid Base Image file selected.")
		sys.exit()
	print("Base Image:", base_file)

	showinfo("Select a Destination", "Please select the name of the file you will create.")
	output_file = asksaveasfilename() # show an "Open" dialog box and return the path to the selected file
	print("Destination:", output_file)

	filter_file = None
	if askyesno("Select a Filters file", "Do you want to select a filters file?"):
		filter_file = askopenfilename() # show an "Open" dialog box and return the path to the selected file
		if len(filter_file) == 0 or not os.path.isfile(filter_file):
			showerror("Error", "Invalid Filter file selected.")
			sys.exit()
	print("Filter File:", filter_file)

	group_file = None
	if askyesno("Select a Groups file", "Do you want to select a groups file?"):
		group_file = askopenfilename() # show an "Open" dialog box and return the path to the selected file
		if len(group_file) == 0 or not os.path.isfile(group_file):
			showerror("Error", "Invalid Groups file selected.")
			sys.exit()
	print("Group File:", group_file)

	max_words = None
	if askyesno("Select a max_words number", "Do you want to set a maximum number of words?"):
		max_words = askinteger("Maximum number of Words","max_words =") # show an "Open" dialog box and return the path to the selected file
		if max_words < 0:
			showerror("Error", "Max Words cannot be negative. Using default value of 2000.")
			max_words = 2000
	print("Max Words:", max_words)

	peacewordcloud.PeaceWordCloud(pdf_file, filter_file, base_file, output_file, group_file, max_words, True)