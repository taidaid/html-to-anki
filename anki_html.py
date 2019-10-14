#!/usr/local/bin/python
from bs4 import BeautifulSoup
from googletrans import Translator
import genanki
import os
import io
import sys
import json
import math
import re
import locale
from operator import itemgetter


# check encoding set by locale
# print(locale.getpreferredencoding())


# set proper encoding
# def read(path):
#     with io.open(path, mode='r', encoding='utf-8') as f:
#         return f.read()


# define path for input file
input_file = open(
    "/Users/Bryan/workspace/HTML-to-Anki/Duolingo_Viet_Vocab_List_file.html", 'rb').read()

anki_coll = "/Users/Bryan/workspace/HTML-to-Anki/Anki-Decks/viet.anki2"

# create a model for Anki Card
my_model = genanki.Model(
    1607398819,
    'Simple Model',
    fields=[
        {'name': 'Question'},
        {'name': 'Answer'},
    ],
    templates=[
        {
            'name': 'Card 1',
            'qfmt': '{{Question}}',
            'afmt': '{{FrontSide}}<hr id="answer">{{Answer}}',
        },
    ])

# name the Anki deck
my_deck = genanki.Deck(
    2059408810,
    'Vietnamese Duolingo Vocab')


# split array into number of wanted parts
def split_list(alist, wanted_parts=1):
    length = len(alist)
    return [alist[i*length // wanted_parts: (i+1)*length // wanted_parts]
            for i in range(wanted_parts)]


# extract the translated words from the list of lists provided
def extract_translations(translations):
    translations = translations.text
    print(translations)
    return translations


# PROBLEM: translate_words is only returning one word
# use google translate to get translation
def translate_words(words):
    trans = Translator()
    print('Translating...')
    # for a sublist in a list of lists of words:
    print('Words to translate: ', str(words))
    translations = []
    if (isinstance(words[0], list)):
        print('It\'s a list of lists alright...')
        translations = trans.translate(words[0])
        return extract_translations(translations)
    else:
        # for a list of words
        print('It\'s a list of words alright')
        translations = trans.translate(str(words))
        print('Here are the translations: ', str(translations))
        return extract_translations(translations)


# count characters in list and split list into X parts with max 15k characters
def char_check(words):
    [len(i) for i in words]
    total_char = sum(len(i) for i in words)
    if(total_char > 500):
        return split_list(words, int(math.ceil(total_char/500)))[0]
    else:
        return words


# extract target words
def get_cards(content):
    soup = BeautifulSoup(input_file, "lxml")
    question_rows = soup.select("._3BXNS")
    questions = []
    # print(translate_words('worden'))
    for q in question_rows:
        question = str(q.text)
        # answer = translate_words(question)
        questions.append(question)
        # answers.append(answer)
    if questions:
        print(str(len(questions)) + ' questions found')
    else:
        print('Didn\'t find anything')
        return None
    print('Checking for character limit')
    questions = char_check(questions)
    # print(questions)
    answers = translate_words(questions)
    answers = re.findall(r'\w+', answers)
    print(answers)
    i = 0
    results = []
    for q in questions:
        results.append((q, answers[i]))
        i += 1
        # print('created ' + str(i) + ' Question-Answer pairs')
    return results


# loop through target words to create anki cards and add to deck
def make_cards(cards):
    qas = get_cards(cards)
    print(qas)
    i = 0
    for qa in qas:
        my_note = genanki.Note(
            model=my_model,
            fields=[itemgetter(0)(qa), itemgetter(1)(qa)])
        my_deck.add_note(my_note)
        i += 1
        # print(str(i) + ' notes added to deck')

    genanki.Package(my_deck).write_to_file('Viet.apkg')


make_cards(input_file)
