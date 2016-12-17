import sys
import getopt
import re
from pdfminer.pdfparser import PDFParser, PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LAParams, LTTextBox, LTTextLine

def usage(executable):
	print("Usage: python", executable, "[ -o file.png ] file.pdf")

class PeaceWordCloud():
	"""
	This class processes a PDF file and generates a Wordcloud using PDFMiner.
	"""
	def __init__(self, pdf_file):
		text = self.readfile(pdf_file)
		print(text[0:100])
	
	def readfile(self, pdf_file):
		fp = open (pdf_file,'rb')

		"""
		DFParser fetch PDF objects from a file stream.
		It can handle indirect references by referring to
		a PDF document set by set_document method.
		It also reads XRefs at the end of every PDF file.
		"""
		parser = PDFParser(fp)

		"""
		Since a PDF file can be very big, normally it is not loaded at
		once. So PDF document has to cooperate with a PDF parser in order to
		dynamically import the data as processing goes.
		"""
		doc = PDFDocument()
		parser.set_document(doc)
		doc.set_parser(parser)

		rsrcmgr = PDFResourceManager()
		device = PDFPageAggregator(rsrcmgr, laparams=LAParams())
		interpreter = PDFPageInterpreter(rsrcmgr, device)

		# Process each page contained in the document.
		file_contents = ""
		for page in doc.get_pages():
			interpreter.process_page(page)
			layout = device.get_result()
			for lt_obj in layout:
				if isinstance(lt_obj, LTTextBox) or isinstance(lt_obj, LTTextLine):
					if re.match(r"^Página", lt_obj.get_text()) == None:
						file_contents += lt_obj.get_text()
		return file_contents

if __name__ == "__main__":
	# Process all the program arguments
	try:
		opts, args = getopt.getopt(sys.argv[1:], "ho:v", ["help", "output="])
	except getopt.GetoptError as err:
		# print help information and exit:
		print(str(err))  # will print something like "option -a not recognized"
		usage(sys.argv[0])
		sys.exit(2)

	# Checks the pdf name
	if len(args) == 0:
		print("A pdf file should have been passed as an argument.")
		usage(sys.argv[0])
		sys.exit(2)

	# Defines the necessary variables
	output = None
	verbose = False
	for o, a in opts:
		if o == "-v":
			verbose = True
		elif o in ("-h", "--help"):
			usage(sys.argv[0])
			sys.exit()
		elif o in ("-o", "--output"):
			output = a
		else:
			assert False, "unhandled option"

	# Begins the program
	PeaceWordCloud(args[0])