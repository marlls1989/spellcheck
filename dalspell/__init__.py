import re
from collections import Counter


def splits(text, start=0, L=10):
    "Return a list of all (first, rest) pairs; start <= len(first) <= L."
    return [(text[:i], text[i:]) 
            for i in range(start, min(len(text), L)+1)]

def product(nums):
    "Multiply the numbers together.  (Like `sum`, but with multiplication.)"
    result = 1
    for x in nums:
        result *= x
    return result

def memo(f):
    "Memoize function f, whose args must all be hashable."
    cache = {}
    def fmemo(*args):
        if args not in cache:
            cache[args] = f(*args)
        return cache[args]
    fmemo.cache = cache
    return fmemo

class NorvigSpell:

    def __init__(self, bow, alphabet = 'abcdefghijklmnopqrstuvwxyz'):
        N = sum(bow.values())
        self.alphabet = alphabet
        self.COUNTS = {k: float(i)/N for k, i in bow.items()}

    def Pword(self, word):
        "Returns the propbability of word to appear"

        if word in self.COUNTS:
            return self.COUNTS[word]

        return 0.01/(len(self.COUNTS)*len(word))

    @memo
    def correct(self, word):
        "Find the best spelling correction for this word."
        # Prefer edit distance 0, then 1, then 2; otherwise default to word itself.
        candidates = (self.known(self.edits0(word)) or
                      self.known(self.edits1(word)) or
                      self.known(self.edits2(word)) or
                      {word})
        return max(candidates, key=self.COUNTS.get)
    
    def known(self, words):
        "Return the subset of words that are actually in the dictionary."
        return {w for w in words if w in self.COUNTS}
    
    def edits0(self, word):
        "Return all strings that are zero edits away from word (i.e., just word itself)."
        return {word}
    
    def edits2(self, word):
        "Return all strings that are two edits away from this word."
        return {e2 for e1 in self.edits1(word) for e2 in self.edits1(e1)}
    
    def edits1(self, word):
        "Return all strings that are one edit away from this word."
        pairs      = self.splits(word)
        deletes    = [a+b[1:]           for (a, b) in pairs if b]
        transposes = [a+b[1]+b[0]+b[2:] for (a, b) in pairs if len(b) > 1]
        replaces   = [a+c+b[1:]         for (a, b) in pairs for c in self.alphabet if b]
        inserts    = [a+c+b             for (a, b) in pairs for c in self.alphabet]
        return set(deletes + transposes + replaces + inserts)
    
    def splits(self, word):
        "Return a list of all possible (first, rest) pairs that comprise word."
        return [(word[:i], word[i:]) 
                for i in range(len(word)+1)]

    def correct_text(self, text):
        "Correct all the words within a text, returning the corrected text."
        return re.sub('[a-zA-Z]+', self.correct_match, text)

    def correct_match(self, match):
        "Spell-correct word in match, and preserve proper upper/lower/title case."
        word = match.group()
        return self.case_of(word)(self.correct(word.lower()))
    
    def case_of(self, text):
        "Return the case-function appropriate for text: upper, lower, title, or just str."
        return (str.upper if text.isupper() else
                str.lower if text.islower() else
                str.title if text.istitle() else
                str)

    def Pwords(self, words):
        "Probability of words, assuming each word is independent of others."
        return product(self.Pword(w) for w in words)

    @memo
    def segment(self, text):
        "Return a list of words that is the most probable segmentation of text."
        if not text: 
            return []

        candidates = ([self.correct(first)] + self.segment(rest) for (first, rest) in splits(text, 1))
        return max(candidates, key=self.Pwords) 

