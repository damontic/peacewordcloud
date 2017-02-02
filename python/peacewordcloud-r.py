# -*- coding: utf-8 -*-

# Standard library imports
import os
import sys
import getopt
import re
import string

# PIL imports
from PIL import Image

# numpy imports
import numpy as np

# wordcloud imports
from wordcloud import WordCloud

def usage():
	print("""
USAGE:
\tpython""", sys.argv[0], """[OPTIONS] -b base_image.png -o result.png

OPTIONS:

\t-f, --frecuency_file=FILE
\t\tSpecifies a file generated with the R program.

\t-b, --base=FILE
\t\tSpecifies the name of the image file to be used. This option is mandatory.

\t-o, --output=FILE
\t\tSpecifies the name of the generated image. This option is mandatory.

\t-m, --max=NUMBER
\t\tSpecifies a maximum number of words to be drawn on the wordcloud. Defaults to 2000.

\t-h, --help
\t\tPrints the usage and exits.

	""")

class PeaceWordCloudR():
	"""
	This class processes a PDF file and generates a Wordcloud using PDFMiner.
	"""

	def __init__(self, base_image, output_file, frecuency_file, max_words):
		"""
		This function creates the PeaceWordCloud object and begins the processing.
		"""
		self.base_image = base_image
		self.output_file = output_file
		self.frecuency_file = frecuency_file
		self.max_words = max_words

	def run(self):
		"""
		This function does the Job. Just to separate the job from the construction of the object.
		Returns 0 if SUCCESS.
		Returns 1 if FAILS.
		"""

		# abrir el archivo y guardar su contenido
		frecuency_file = open(self.frecuency_file, encoding="iso8859-1")
		frecuency_contents = frecuency_file.readlines()
		frecuency_file.close()

		# Eliminar el salto de línea
		frecuency_contents = [ content[:-1] for content in frecuency_contents ]

		# crear lista de listas
		frecuency_contents = [ content.split("\t") for content in frecuency_contents ]		

		# crear lista de tuplas		
		frecuencies = [ (content[0], int(content[1]) ) for content in frecuency_contents ]		

		# crear la imagen
		self.create_image(base_image, frecuencies, output_file, self.max_words)

		return 0


	def create_image(self, base_image, frecuencies, output_file, maximum_words):
		"""
		This function creates the image with the wordcloud.
		"""
		# Read the mask image
		base_image_mask = np.array(Image.open(base_image))

		wc = WordCloud(background_color="white", max_words=maximum_words, mask=base_image_mask)

		# Generate word cloud
		wc.generate_from_frequencies(frecuencies)

		# Store to file
		wc.to_file(output_file)

if __name__ == "__main__":
	# Process all the program arguments
	try:
		opts, args = getopt.getopt(sys.argv[1:], "ho:b:m:f:", ["help", "output=", "base=", "max=", "frecuency_file="])
	except getopt.GetoptError as err:
		# print help information and exit:
		print(str(err))  # will print something like "option -a not recognized"
		usage()
		sys.exit(2)

	# Defines the necessary variables
	output_file = None
	frecuency_file = None
	base_image = None
	pdf_file = None
	max_words = 2000

	for option, value in opts:
		if option in ("-h", "--help"):
			usage()
			sys.exit()
		elif option in ("-f", "--frecuency_file"):
			frecuency_file = value
		elif option in ("-b", "--base"):
			base_image = value
		elif option in ("-o", "--output"):
			output_file = value
		elif option in ("-m", "--max"):
			try:
				max_words = int(value)
			except ValueError:
				print("-m or --max must be a number. Taking 2000 as default.")
		else:
			assert False, "unhandled option"

	# Checks the pdf name and the base image
	if frecuency_file == None or base_image == None or output_file == None:
		print("The options -b, -f and -o are mandatory.")
		usage()
		sys.exit(2)

	# Begins the program
	pwc = PeaceWordCloudR(base_image, output_file, frecuency_file, max_words)
	result = pwc.run()
	if result == 0:
		print("SUCCESS!")
	else:
		print("FAILURE!")
