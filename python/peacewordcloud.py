# -*- coding: utf-8 -*-

# Standard library imports
from __future__ import print_function
import os
import sys
import getopt
import re
import string

# PDFMiner imports
from pdfminer.pdfparser import PDFParser, PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LAParams, LTTextBox, LTTextLine

# NLTK imports
from nltk import FreqDist
from nltk.corpus import stopwords
from nltk.tokenize import MWETokenizer, word_tokenize

# PIL imports
from PIL import Image

# numpy imports
import numpy as np

# matplotlib imports
import matplotlib.pyplot as plt

# wordcloud imports
from wordcloud import WordCloud

def usage():
	print("""
USAGE:
\tpython""", sys.argv[0], """[OPTIONS] [-s input_file.txt] [-p input_file.pdf] -b base_image.png -o result.png

OPTIONS:
\t-p, --pdf=FILE
\t\tSpecifies the name of the pdf input file to be processed.

\t-b, --base=FILE
\t\tSpecifies the name of the image file to be used. This option is mandatory.

\t-o, --output=FILE
\t\tSpecifies the name of the generated image. This option is mandatory.

\t-f, --filter=FILE
\t\tSpecifies a file with filters If no file is specified, no filters are used.
\t\tThe filters file defines a filter per line.

\t-g, --groups=FILE
\t\tSpecifies a file with groups of words. If no file is specified, no groups are used.
\t\tThe groups file defines a group of words per line.

\t-c, --csv=FILE
\t\tSpecifies an output file with the frecuencies.

\t-m, --max=NUMBER
\t\tSpecifies a maximum number of words to be drawn on the wordcloud. Defaults to 2000.

\t-s, --save-file
\t\tSpecifies the name of the file you want to save

\t-l, --load-file
\t\tSpecifies the name of the file you want to load

\t-h, --help
\t\tPrints the usage and exits.

	""")

class PeaceWordCloud():
	"""
	This class processes a PDF file and generates a Wordcloud using PDFMiner.
	"""

	def __init__(self, pdf_file, filters_file, base_image, output_file, groups_file, csv_file, max_words, load_file, save_file, verbose):
		"""
		This function creates the PeaceWordCloud object and begins the processing.
		"""
		self.verbose = verbose
		self.groups = self.read_file_as_lower(groups_file)
		self.printv("GROUPS:", self.groups)
		self.filters = self.read_file_as_lower(filters_file)
		self.printv("FILTERS:", self.filters)

		self.pdf_file = pdf_file
		self.base_image = base_image
		self.output_file = output_file
		self.csv_file = csv_file
		self.max_words = max_words
		self.load_file = load_file
		self.save_filename = save_file

	def run(self):
		"""
		This function does the Job. Just to separate the job from the construction of the object.
		Returns 0 if SUCCESS.
		Returns 1 if FAILS.
		"""
		if self.load_file == None:
			file_contents = self.read_pdf_file(self.pdf_file)
		else:
			file_contents = self.process_saved_file(self.load_file)

		if len(file_contents) == 0:
			print("Couldn't read text from the pdf file!")
			return 1

		# Begin with some word processing
		file_contents = [ self.remove_punctuation(word) for word in file_contents ]
		file_contents = self.remove_no_alpha(file_contents)
		file_contents = [ word.lower() for word in file_contents ]

		if len(file_contents) == 0:
			print("Couldn't remove no alpha")
			print("file_contents:", file_contents)
			return 1

		if self.save_filename != None:
			flatten = lambda l: [item for sublist in l for item in sublist]
			file_contents2 = flatten([i.split() for i in file_contents])
			file_contents2 = self.remove_filters(file_contents2, self.filters)
			filename = self.save_file(" ".join(file_contents2))

		frecuencies = self.frequency_analysis(file_contents, self.groups, self.filters)

		if len(frecuencies) == 0:
			print("Couldn't get frecuencies")
			print("file_contents:", file_contents)
			return 1

		self.create_image(self.base_image, frecuencies, self.output_file, self.max_words)
		if self.csv_file != None:
			self.export_csv(frecuencies)
		return 0

	def remove_filters(self, words, filters):
		return [ word for word in words if word not in filters ]

	def remove_no_alpha(self, text):
		return [ re.sub(r"[^a-zA-ZñÑáéíóúÁÉÍÓÚ ]","", word) for word in text]

	def read_file_as_lower(self, current_file):
		"""
		This function reads a file and returns a list of lines in lowercase.
		"""
		def lowers_removes_linesep(some_string):
			if some_string.endswith("\n"):
				some_string = some_string[:-1]
			return some_string.lower()

		lines = []
		if current_file != None:
			fp = open (current_file,'r', encoding="utf-8")
			lines = fp.readlines()
			fp.close()
			lines = [ lowers_removes_linesep(line) for line in lines ]
		return lines
	
	def read_pdf_file(self, pdf_file):
		"""
		This function reads the PDF, obtains the words and merges them into a single string.
		"""

		fp = open (pdf_file,'rb')

		"""
		DFParser fetch PDF objects from a file stream.
		It can handle indirect references by referring to
		a PDF document set by set_document method.
		It also reads XRefs at the end of every PDF file.
		"""
		pdf_parser = PDFParser(fp)

		"""
		Since a PDF file can be very big, normally it is not loaded at
		once. So PDF document has to cooperate with a PDF parser in order to
		dynamically import the data as processing goes.
		"""
		pdf_doc = PDFDocument()
		pdf_parser.set_document(pdf_doc)
		pdf_doc.set_parser(pdf_parser)

		"""
		ResourceManager facilitates reuse of shared resources
		such as fonts and images so that large objects are not
		allocated multiple times.
		"""
		rsrcmgr = PDFResourceManager()
		pdf_page_aggregator = PDFPageAggregator(rsrcmgr, laparams=LAParams())
		interpreter = PDFPageInterpreter(rsrcmgr, pdf_page_aggregator)

		# Process each page contained in the document and adds them to the file_contents string
		file_contents = []
		page_num = 0
		for page in pdf_doc.get_pages():
			interpreter.process_page(page)
			layout = pdf_page_aggregator.get_result()
			for lt_obj in layout:
				if isinstance(lt_obj, LTTextBox) or isinstance(lt_obj, LTTextLine):
					file_contents.append( lt_obj.get_text().replace('\t', ' ').replace('\n',' ') )
			page_num = page_num + 1
			print("Page Num:", page_num, file=sys.stderr, end="\r")

		fp.close()
		self.printv("FILE_CONTENTS_LENGTH in CHARACTERS: ", str(len(file_contents)))
		return file_contents

	def frequency_analysis(self, file_contents, groups, filters):
		"""
		This function uses the NLTK library to make a frecuency analisis.
		Uses groups as tokens.
		"""

		flatten = lambda l: [item for sublist in l for item in sublist]
		file_contents = flatten( [ i.split() for i in file_contents ] )
		file_contents = self.remove_filters(file_contents, filters)
		
		# Return a tokenized copy of "pdt_string", using NLTK's recommended word tokenizer
		tokenizer = MWETokenizer()
		for group in groups:
			tokenizer.add_mwe(group.split(" "))
		tokens = tokenizer.tokenize(file_contents)

		# Filters the spanish stopwords (hemos, están, estuvimos, etc.)
		stopwords_esp = stopwords.words('spanish')
		tokens = [w for w in tokens if w not in stopwords_esp]

		# Gets the most common words
		return FreqDist(tokens).most_common()

	def create_image(self, base_image, frecuencies, output_file, maximum_words):
		"""
		This function creates the image with the wordcloud.
		Returns frecuencies
		"""
		# Read the mask image
		base_image_mask = np.array(Image.open(base_image))

		wc = WordCloud(background_color="white", max_words=maximum_words, mask=base_image_mask)

		# Generate word cloud
		wc.generate_from_frequencies(frecuencies)

		# Store to file
		wc.to_file(output_file)

	def remove_punctuation(self, text):
		"""
		This function removes all the punctuation marks from text.
		"""
		# The punctuation variable has the following caracters: !"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~¡¿”“•\r´
		punctuation = string.punctuation + '¡¿”“•\r\n´'
		# Filters the punctuation marks and lowers all the words
		transtable = text.maketrans('', '', punctuation)
		return text.translate(transtable)

	def export_csv(self, frecuencies):
		"""
		This function creates a csv from the frecuencies.
		"""
		f = open(self.csv_file, "w", encoding="utf-8")
		for frecuency in frecuencies:
			f.write(frecuency[0] + "," + str(frecuency[1]) + "\n")
		f.close()

	def printv(self, *text):
		"""
		This is an utility function to call print when the verbosity is on.
		"""
		if self.verbose == True:
			print(text)

	def save_file(self, contents):
		new_file = open(self.save_filename, "w", encoding="utf-8")
		new_file.writelines(contents)
		new_file.close()

	def process_saved_file(self, saved_file):
		contents = []
		to_read_saved_file = open(saved_file, "r", encoding="utf-8")
		for line in to_read_saved_file.readlines():
			contents = contents + line.split(" ")
		to_read_saved_file.close()
		return contents

if __name__ == "__main__":
	# Process all the program arguments
	try:
		opts, args = getopt.getopt(sys.argv[1:], "vho:f:p:b:g:m:c:s:l:", ["verbose","help", "output=", "filters=", "pdf=", "base=", "groups=", "max=", "csv=", "save-file=","load-file="])
	except getopt.GetoptError as err:
		# print help information and exit:
		print(str(err))  # will print something like "option -a not recognized"
		usage()
		sys.exit(2)

	# Defines the necessary variables
	verbose = False
	output_file = None
	save_file = None
	filter_file = None
	group_file = None
	base_image = None
	pdf_file = None
	csv_file = None
	max_words = 2000
	load_file=None
	for option, value in opts:
		if option in ("-h", "--help"):
			usage()
			sys.exit()
		elif option in ("-b", "--base"):
			base_image = value
		elif option in ("-p", "--pdf"):
			pdf_file = value
		elif option in ("-o", "--output"):
			output_file = value
		elif option in ("-v", "--verbose"):
			verbose = True
		elif option in ("-f", "--filters"):
			filter_file = value
		elif option in ("-g", "--groups"):
			group_file = value
		elif option in ("-c", "--csv"):
			csv_file = value
		elif option in ("-l", "--load-file"):
			load_file = value
		elif option in ("-s", "--save-file"):
			save_file = value
		elif option in ("-m", "--max"):
			try:
				max_words = int(value)
			except ValueError:
				print("-m or --max must be a number. Taking 2000 as default.")
		else:
			assert False, "unhandled option"

	# Checks the base image and output file
	if base_image == None or output_file == None:
		print("The options -b and -o are mandatory.")
		usage()
		sys.exit(2)

	# Checks the base image and output file
	if pdf_file == None and load_file == None:
		print("You must specify a pdf or a txt file.")
		usage()
		sys.exit(3)

	# Begins the program
	pwc = PeaceWordCloud(pdf_file, filter_file, base_image, output_file, group_file, csv_file, max_words, load_file, save_file, verbose)
	result = pwc.run()
	if result == 0:
		print("SUCCESS!")
	else:
		print("FAILURE!")
