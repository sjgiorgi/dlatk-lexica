import json
import os
import re
import shutil
from collections import Counter
from pathlib import Path

from utils.happierfuntokenizing import Tokenizer


class TextWorker(object):

    def __init__(self):
        self.multSpace = re.compile(r'\s\s+')
        self.startSpace = re.compile(r'^\s+')
        self.endSpace = re.compile(r'\s+$')
        self.multDots = re.compile(r'\.\.\.\.\.+')
        self.newlines = re.compile(r'\s*\n\s*')
        self.handle = re.compile(r"(?<![A-Za-z0-9_!@#\$%&*])@(([A-Za-z0-9_]){20}(?!@))|(?<![A-Za-z0-9_!@#\$%&*])@(([A-Za-z0-9_]){1,19})(?![A-Za-z0-9_]*@)")
        self.url = re.compile(r"http\S+")
    
    def shrinkSpace(self, text):
        """
        Turns multiple spaces into 1
        """
        text = self.multSpace.sub(' ', text)
        text = self.multDots.sub('....', text)
        text = self.endSpace.sub('', text)
        text = self.startSpace.sub('', text)
        text = self.newlines.sub(' <NEWLINE> ', text)
        return text
    
    def remove_handles(self, text):
        """
        Remove Twitter username handles from text
        """
        text = self.handle.sub('<USER>', text)
        return text
    
    def remove_urls(self, text):
        """
        Remove URLs from text
        """
        text = self.url.sub('<URL>', text)
        return text

    def extractNgramPerDoc(self, document, n=1):
        """
        Extract n-grams from document after standardizing
        """
        document = self.shrinkSpace(document)
        document = self.remove_handles(document)
        document = self.remove_urls(document)
        tokens = self.tok.tokenize(document)

        ngrams = Counter([" ".join(x) for x in zip(*[tokens[n:]])])
        total_ngrams = float(sum(ngrams.values()))
        ngrams = {gram: value / total_ngrams for gram, value in ngrams.items()}
        return ngrams

    
class LexiconExtractor(TextWorker):
    # TODO
    ### Binary ngram encoding for affect
    ### Lex Norm
    ### LIWC Norm

    def __init__(self, lexicon_name):
        super(LexiconExtractor, self).__init__()
        self._lex_dir = os.path.dirname(os.path.realpath(__file__)) + "/lexica/"
        self.tok = Tokenizer()
        self.lex = self.load_lexicon(lexicon_name)
        self.available_lexica = self._get_available_lexica()
        

    def _get_available_lexica(self):
        all_lex = []
        for file in os.listdir(self._lex_dir):
            if file.endswith(".json"):
                all_lex.append(file.replace(".json", ""))
        return sorted(all_lex)

    def upload_lexicon(self, json_file):
        
        jf = Path(json_file)

        if jf.is_file():
            with open(json_file) as json_file:  
                data = json.load(json_file)
            if not isinstance(data, dict):
                print("The file must be a Python dictionary. Unable to upload.")
                return False
            shutil.copyfile(json_file, self._lex_dir)
            return True
        else:
            print("The file {json_file} does not exist".format(json_file=json_file))
            return False

    def load_lexicon(self, lexicon_name):
        try:
            with open(self._lex_dir + lexicon_name + ".json") as json_file:  
                data = json.load(json_file)
        except:
            print("The lexica {lexicon_name} is not available.".format(lexicon_name=lexicon_name))
            print("Please use LexiconExtractor.available_lexica to see the available lexica.")
            return None
        return data 

    def get_scores(self, document_list):
        """
        """
        if not isinstance(document_list, list):
            document_list = [document_list]
        
        results = []
        for document in document_list:
            ngrams = self.extractNgramPerDoc(document)
            pLex = {} # prob of lex given user
            for term, cats in self.lex.items():
                try:
                    gn = ngrams[term]
                    for cat, weight in cats.items():
                        try:
                            pLex[cat] += float(gn)*weight
                        except KeyError:
                            pLex[cat] = float(gn)*weight
                except KeyError:
                    pass #not in lex

            if "_intercept" in self.lex:
                for cat, intercept in self.lex["_intercept"].items():
                    pLex[cat] += intercept
            results.append(pLex)
        return results

