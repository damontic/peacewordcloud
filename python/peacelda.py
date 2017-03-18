# -*- coding: utf-8 -*-

# Standard library imports
from __future__ import print_function
import os
import sys
import getopt

# numpy imports
import numpy as np

# text2ldac
import text2ldac
import lda

# NLTK stopwords
from nltk.corpus import stopwords


def usage():
    print("""
USAGE:

\tpython""", sys.argv[0], """[-h] -d directory

OPTIONS:
\t-d, --directory=FILE
\t\tSpecifies the name of the directory with al the txt files

\t-f, --filter=FILE
\t\tSpecifies a file with filters If no file is specified, no filters are used.
\t\tThe filters file defines a filter per line.

\t-h, --help
\t\tPrints the usage and exits.
	""")


class PeaceLDA():
    """
    This class processes a list of files and generates the LDA
    """

    def __init__(self, directory, filters_file, verbose):
        """
        This function creates the PeaceLDA Object
        """
        self.verbose = verbose
        self.directory = directory
        self.filters = self.read_file_as_lower(filters_file)

    def run(self):
        """
        This function does the Job. Just to separate the job from the construction of the object.
        Returns 0 if SUCCESS.
        Returns 1 if FAILS.
        """

        # store configuration
        config = dict()
        config['datname'] = 'data.ldac'
        config['vocabname'] = 'data.vocab'
        config['dmapname'] = 'data.dmap'
        config['minlength'] = 1
        config['minoccurrence'] = 1
        config['stopwords'] = stopwords.words('spanish') + self.filters
        filenames = os.listdir(self.directory)
        files = [ self.directory + os.sep + elem for elem in filenames ]
        text2ldac.generate_dat_and_vocab_files(files, config)

        # analyse with lda
        X = self.load_ldac(config["datname"])
        vocab = self.load_vocab(config["vocabname"])
        model = lda.LDA(n_topics=10, n_iter=1500, random_state=1, alpha=0.8, eta=0.2)
        model.fit(X)
        topic_word = model.topic_word_
        n_top_words = 8
        f = open("lda_result.txt", "w", encoding="utf-8")
        for i, topic_dist in enumerate(topic_word):
            topic_words = np.array(vocab)[np.argsort(topic_dist)][:-(n_top_words + 1):-1]
            res = ' '.join(topic_words)
            f.write('Topic' + str(i) + ':' + str(res) + "\n")

        doc_topic = model.doc_topic_
        for i in range(len(files)):
            f.write(str(filenames[i]) + " (topic %: " +str(doc_topic[i]) + ")\n")
            f.write(" (top topic: " + str(doc_topic[i].argmax()) + ")\n")
        f.close()
        return 0

    def load_ldac(self, filename):
        return lda.utils.ldac2dtm(open(filename, encoding="utf-8"), offset=0)

    def load_vocab(self, filename):
        with open(filename, encoding="utf-8") as f:
            vocab = tuple(f.read().split())
        return vocab

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

    def printv(self, *text):
        """
        This is an utility function to call print when the verbosity is on.
        """
        if self.verbose == True:
            print(text)

if __name__ == "__main__":
    # Process all the program arguments
    try:
        opts, args = getopt.getopt(sys.argv[1:], "vhd:f:",
                                   ["verbose", "help", "directory=", "filters="])
    except getopt.GetoptError as err:
        # print help information and exit:
        print(str(err))  # will print something like "option -a not recognized"
        usage()
        sys.exit(2)

    # Defines the necessary variables
    verbose = False
    directory = None
    filter_file = None
    for option, value in opts:
        if option in ("-h", "--help"):
            usage()
            sys.exit()
        elif option in ("-d", "--directory"):
            directory = value
        elif option in ("-f", "--filters"):
            filter_file = value
        elif option in ("-v", "--verbose"):
            verbose = True
        else:
            assert False, "unhandled option"

    # Checks the base image and output file
    if directory == None:
        print("You must specify a directory.")
        usage()
        sys.exit(3)

    # Begins the program
    plda = PeaceLDA(directory, filter_file, verbose)
    result = plda.run()
    if result == 0:
        print("SUCCESS!")
    else:
        print("FAILURE!")
