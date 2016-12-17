import sys
import getopt
import re
from pdfminer.pdfparser import PDFParser, PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LAParams, LTTextBox, LTTextLine

def usage(executable):
	print("""
USAGE:
\tpython""", executable, """[OPTIONS] input_file.pdf

OPTIONS:
\t-o, --output=FILE
\t\tSpecifies the name of the generated image. If the option is not specified the default filename wordcloud.png is used.

\t-f, --filter=FILE
\t\tSpecifies a file with filters If no file is specified, no filters are used.
\t\tThe filters file defines a filter per line. Each filter is a Regular Expression.
\te.g.:
\t\t1) The filter 'Página' filters all the lines that match EXACTLY the word 'Página'
\t\t2) The filter '^Página' filters all the lines that BEGINS with the word 'Página'
\t\t3) The filter '.*Página.*' filters all the lines that CONTAIN the word 'Página'
\t\t4) The filter 'Página$' filters all the lines that END with the word 'Página'

\t-h, --help
\t\tPrints the usage and exits.

	""")

class PeaceWordCloud():
	"""
	This class processes a PDF file and generates a Wordcloud using PDFMiner.
	"""

	def __init__(self, pdf_file, filters_file):
		"""
		This function creates the PeaceWordCloud object and begins the processing
		"""
		re_filters = self.read_filters_file(filters_file)
		text = self.read_pdf_file(pdf_file, re_filters)
		print(text[0:2000])

	def read_filters_file(self, filters_file):
		re_filters = []
		if filters_file != None:
			fp = open (filters_file,'r')
			string_filter = fp.readline()
			while string_filter != '':
				re_filters.append(re.compile(string_filter[:-1]))
				string_filter = fp.readline()
			fp.close()
		print("FILTERS: ", re_filters)
		return re_filters
	
	def read_pdf_file(self, pdf_file, re_filters):
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
				matches_filter = False
				if isinstance(lt_obj, LTTextBox) or isinstance(lt_obj, LTTextLine):
					for re_filter in re_filters:
						if re_filter.match(lt_obj.get_text()) != None:
							print("FILTERING:", lt_obj.get_text())
							matches_filter = True
							break
					if not matches_filter:
						file_contents += lt_obj.get_text()

		print("FILE_CONTENTS_LENGTH in CHARACTERS: ", str(len(file_contents)))
		return file_contents

if __name__ == "__main__":
	# Process all the program arguments
	try:
		opts, args = getopt.getopt(sys.argv[1:], "ho:f:", ["help", "output=", "filters="])
	except getopt.GetoptError as err:
		# print help information and exit:
		print(str(err))  # will print something like "option -a not recognized"
		usage(sys.argv[0])
		sys.exit(2)

	# Defines the necessary variables
	output_file = None
	filter_file = None
	for option, value in opts:
		if option in ("-h", "--help"):
			usage(sys.argv[0])
			sys.exit()
		elif option in ("-o", "--output"):
			output_file = value
		elif option in ("-f", "--filters"):
			filter_file = value
		else:
			assert False, "unhandled option"

	# Checks the pdf name
	if len(args) == 0:
		print("A pdf file should have been passed as an argument.")
		usage(sys.argv[0])
		sys.exit(2)

	# Begins the program
	PeaceWordCloud(args[0], filter_file)