#!/bin/env python3

import re
from nltk.corpus import stopwords
from dalspell import NorvigSpell

bow = dict()

with open('en_full.txt', 'r') as f:
    for line in f:
        a = line.strip().split(' ')
        bow[a[0]] = int(a[1])

stop_words = set(stopwords.words("english"))
spellcheck = NorvigSpell(bow, stopwords=stop_words)

with open('exemplo.csv', 'r') as f:
    for line in f:
        text = re.sub(r'[^a-zA-Z]', '', line.strip().lower())
        results = spellcheck.segment(text)
        print(results)
