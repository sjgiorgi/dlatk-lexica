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
        self.tok = Tokenizer()
    
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
    ### TODO
    ### Lex Norm for NRC
    ### LIWC Norm
    ### multi-word lexica (n>1)

    def __init__(self, lexicon_name):
        super(LexiconExtractor, self).__init__()
        self.lexicon_name = lexicon_name
        self._lex_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__))) + "/lexica/"
        self.lex = self.load_lexicon(self.lexicon_name)
        self.available_lexica = self._get_available_lexica()
        
    def _get_available_lexica(self):
        """
        """
        all_lex = []
        for file in os.listdir(self._lex_dir):
            if file.endswith(".json"):
                all_lex.append(file.replace(".json", ""))
        return sorted(all_lex)

    def upload_lexicon(self, json_file):
        jf = Path(json_file)

        if jf.is_file():
            with open(json_file) as this_json_file:  
                data = json.load(this_json_file)
            if not isinstance(data, dict):
                print("The file must be a Python dictionary. Unable to upload.")
            shutil.copyfile(json_file, self._lex_dir + os.path.basename(json_file))
        else:
            print("The file {json_file} does not exist".format(json_file=json_file))

    def combine_lexica(self, lexicon_name):
        new_lex = self.load_lexicon(lexicon_name)
        for k,v in self.lex.items():
            if k in new_lex:
                new_lex[k].update(v)
            else:
                new_lex[k] = v
        self.lex = new_lex

        if not isinstance(self.lexicon_name, list):
            self.lexicon_name = [self.lexicon_name]
        self.lexicon_name.append(lexicon_name)
        

    def remove_lexica(self, lexicon_name):
        this_lex = dict(self.lex)
        for k,v in this_lex.items():
            if lexicon_name in v:
                del self.lex[k][lexicon_name]
            if not self.lex[k]:
                del self.lex[k]
        if isinstance(self.lexicon_name, list):
            self.lexicon_name.remove(lexicon_name)
        else:
            if lexicon_name == self.lexicon_name:
                self.lexicon_name = ""


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
            n = 1
            if 'affect' in self.lexicon_name:
                n = 1
            ngrams = {}
            for ii in range(n):
                ngrams.update(self.extractNgramPerDoc(document, n=ii+1))
            pLex = {} # prob of lex given user
            for term, cats in self.lex.items():
                try:
                    gn = ngrams[term]
                    for cat, weight in cats.items():
                        try:
                            if cat == "affect":
                                pLex[cat] += float(1)*weight
                            else:
                                pLex[cat] += float(gn)*weight
                        except KeyError:
                            if cat == "affect":
                                pLex[cat] = float(1)*weight
                            else:
                                pLex[cat] = float(gn)*weight
                except KeyError:
                    pass #not in lex

            if "_intercept" in self.lex:
                for cat, intercept in self.lex["_intercept"].items():
                    pLex[cat] += intercept
            results.append(pLex)
        return results

