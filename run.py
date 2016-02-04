#!/usr/bin/env python
# -*- coding: utf-8 -*-

__all__ = ["run", "compute_tfidf"]

import re
import json
import string
import html2text
import feedparser
from collections import Counter

from nltk import word_tokenize
from nltk.corpus import stopwords

program = re.compile(r"\(arXiv:.*?\)")
stops = set(stopwords.words("english"))
punkt = set(string.punctuation)
strip = "0123456789" + string.punctuation
upper = set(string.ascii_uppercase)


def _casefix(w):
    if sum(l in upper for l in w) == 1:
        return w.lower()
    return w


def run(url="http://arxiv.org/rss/astro-ph"):
    tree = feedparser.parse(url)
    tf = Counter()
    df = Counter()
    for e in tree.entries:
        txt = html2text.html2text(e.title + " " + e.title + " " + e.summary)
        txt = txt.replace("[Donate to arXiv](http://arxiv.org)", "")
        txt = program.sub("", txt)
        txt = txt.strip()
        tokens = [_casefix(w) for w in word_tokenize(txt)
                  if (len(w) >= 3 and len(w.strip(strip)) and
                      w.lower() not in stops and
                      not len(set(w) & punkt))]
        tf.update(tokens)
        df.update(set(tokens))

    for k in list(tf.keys()):
        if df[k] == 1:
            del tf[k]

    return len(tree.entries), df, tf


def compute_tfidf(N, df, tf):
    tfidf = Counter()
    for k, n in tf.items():
        tfidf[k] = n / (1 + df[k])
    return tfidf


if __name__ == "__main__":
    import os
    import random
    import argparse

    parser = argparse.ArgumentParser(description="what kinda day is it?")
    parser.add_argument("-u", "--url", default="http://arxiv.org/rss/astro-ph",
                        help="the RSS URL")
    parser.add_argument("-c", "--cache", default="cache",
                        help="the cache directory")
    parser.add_argument("--no-update", action="store_true",
                        help="don't update the saved values")
    args = parser.parse_args()

    # Make the cache directory if it doesn't exist.
    cache = args.cache
    os.makedirs(cache, exist_ok=True)

    # Load the cached frequencies.
    files = dict(info=Counter(N=0), df=Counter())
    for k in files.keys():
        fn = os.path.join(cache, "{0}.json".format(k))
        if os.path.exists(fn):
            with open(fn, "r") as f:
                files[k] = Counter(json.load(f))

    # Parse the current listing.
    N, df, tf = run(url=args.url)

    # Update the frequencies.
    files["info"]["N"] += N
    files["df"].update(df)
    if not args.no_update:
        for k in files.keys():
            fn = os.path.join(cache, "{0}.json".format(k))
            with open(fn, "w") as f:
                json.dump(files[k], f)

    # Compute the most "special" words.
    tfidf = compute_tfidf(files["info"]["N"], files["df"], tf)
    words, rates = zip(*(tfidf.most_common(40)))
    u = random.random() * sum(rates)
    x = 0.0
    for w, r in zip(words, rates):
        x += r
        if x >= u:
            print("It's a '{0}' kind of day".format(w))
            break
