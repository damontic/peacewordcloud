# -*- coding: utf-8 -*-

# Standard library imports
import sys
import getopt
import re
import string
from os import path

# PDFMiner imports
from pdfminer.pdfparser import PDFParser, PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LAParams, LTTextBox, LTTextLine

# NLTK imports
from nltk import FreqDist
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize

# PIL imports
from PIL import Image

# numpy imports
import numpy as np

# matplotlib imports
import matplotlib.pyplot as plt

# wordcloud imports
from wordcloud import WordCloud, STOPWORDS

def usage():
	print("""
USAGE:
\tpython""", sys.argv[0], """[OPTIONS] -p input_file.pdf -b base_image.png

OPTIONS:
\t-p, --pdf=FILE
\t\tSpecifies the name of the pdf input file to be processed. This option is mandatory.

\t-b, --base=FILE
\t\tSpecifies the name of the image file to be used. This option is mandatory.

\t-o, --output=FILE
\t\tSpecifies the name of the generated image. If the option is not specified the default filename wordcloud.png is used.

\t-f, --filter=FILE
\t\tSpecifies a file with filters If no file is specified, no filters are used.
\t\tThe filters file defines a filter per line. Each filter must be a word in LOWERCASE.

\t-h, --help
\t\tPrints the usage and exits.

	""")

class PeaceWordCloud():
	"""
	This class processes a PDF file and generates a Wordcloud using PDFMiner.
	"""

	def __init__(self, pdf_file, filters_file, base_image, output_file, verbose):
		"""
		This function creates the PeaceWordCloud object and begins the processing.
		"""
		self.verbose = verbose
		filters = self.read_filters_file(filters_file)
		text = self.read_pdf_file(pdf_file)
		#(frecuencies, tokens) = self.frequency_analysis(text)
		curated_text = self.remove_punctuation(text)
		self.create_image(base_image, text, output_file, filters)

	def read_filters_file(self, filters_file):
		"""
		This function reads a file that defines a list of regex.
		"""
		filters = []
		if filters_file != None:
			fp = open (filters_file,'r')
			filters = fp.readlines()
			fp.close()
		self.printv("FILTERS: ", filters)
		return filters
	
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
		file_contents = ""
		for page in pdf_doc.get_pages():
			interpreter.process_page(page)
			layout = pdf_page_aggregator.get_result()
			for lt_obj in layout:
				if isinstance(lt_obj, LTTextBox) or isinstance(lt_obj, LTTextLine):
					file_contents += lt_obj.get_text()

		fp.close()
		self.printv("FILE_CONTENTS_LENGTH in CHARACTERS: ", str(len(file_contents)))
		return file_contents

	def frequency_analysis(self, file_contents):
		"""
		This function uses the NLTK library to make a frecuency analisis.
		"""
		pdf_string = remove_punctuation(file_contents)

		# Return a tokenized copy of "pdt_string", using NLTK's recommended word tokenizer
		tokens = word_tokenize(pdf_string)

		# Filters the spanish stopwords (hemos, están, estuvimos, etc.)
		stopwords_esp = stopwords.words('spanish')
		tokens = [w for w in tokens if w not in stopwords_esp]

		# Gets the most common words
		frecuencies = FreqDist(tokens).most_common()
		return (frecuencies, tokens)

	def create_image(self, base_image, text, output_file, filters):
		# Read the mask image
		acuerdo_mask = np.array(Image.open(base_image))

		wc = WordCloud(background_color="white", max_words=2000, mask=acuerdo_mask, stopwords=set(stopwords.words("spanish")+filters))

		# Generate word cloud
		wc.generate(text)

		# Store to file
		wc.to_file(output_file)

	def remove_punctuation(self, text):
		# The punctuation variable has the following caracters: !"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~¡¿”“•\r´
		punctuation = string.punctuation + '¡¿”“•\r´'
		# Filters the punctuation marks and lowers all the words
		transtable = text.maketrans('', '', punctuation)
		pdt_string = text.translate(transtable)
		return pdt_string.lower()

	def printv(self, *text):
		if self.verbose == True:
			print(text)

if __name__ == "__main__":
	# Process all the program arguments
	try:
		opts, args = getopt.getopt(sys.argv[1:], "vho:f:p:b:", ["help", "output=", "filters="])
	except getopt.GetoptError as err:
		# print help information and exit:
		print(str(err))  # will print something like "option -a not recognized"
		usage()
		sys.exit(2)

	# Defines the necessary variables
	verbose = False
	output_file = "wordcloud.png"
	filter_file = None
	base_image = None
	pdf_file = None
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
		else:
			assert False, "unhandled option"

	# Checks the pdf name and the base image
	if pdf_file == None or base_image == None:
		print("The options -b and -p are mandatory.")
		usage()
		sys.exit(2)

	# Begins the program
	PeaceWordCloud(pdf_file, filter_file, base_image, output_file, verbose)