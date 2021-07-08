from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
from werkzeug.datastructures import  FileStorage
from pdf2image import convert_from_path
import easyocr
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from nltk.stem import *
import PIL
import nltk
import os
import heapq
import re
import math
import operator
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize,word_tokenize
from PIL import ImageDraw
app = Flask(__name__)
UPLOAD_FOLDER = './uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER 

nltk.download('averaged_perceptron_tagger')
Stopwords = set(stopwords.words('english'))
wordlemmatizer = WordNetLemmatizer()

@app.route('/')
def homepage():
   return render_template('index.html')

@app.route('/login')
def loginpage():
    return render_template('login.html')
    
@app.route('/upload')
def upload_file():
    return render_template('upload.html')
	
@app.route('/upload', methods =['POST'])
def upload_files():
   if request.method == 'POST':
    f = request.files['file']
    len_summary = request.form['summary-length']
    filename = secure_filename(f.filename)
    f.save(filename)
    resultant_summary = main_funct(filename, int(len_summary))
      
    return jsonify({
        "status": 200,
        "message": "success",
        "data": {"summary": resultant_summary}
    })

def ocr_for_pdf(input_file):
    
    reader = easyocr.Reader(['en'])
    dir = os.path.dirname(__file__)
    filename = os.path.join(dir, r'poppler-0.68.0\bin')
    print(filename)
    images = convert_from_path(input_file,  poppler_path=filename)
    filename = "demofile.txt"
    f = open(filename, "w")

    text=''
    for i in range(len(images)):
        bounds = reader.readtext(np.array(images[i]), min_size=0, slope_ths=0.2, ycenter_ths=0.7, height_ths=0.6, width_ths=0.8,decoder='beamsearch', beamWidth=10)
    
        for j in range(len(bounds)):
            text = text + bounds[j][1] +'\n'
    
    f.write(text)
    f.close()
    return filename


def draw_boxes(image, bounds, color='yellow', width=2):
        draw = ImageDraw.Draw(image)
        for bound in bounds:
            p0, p1, p2, p3 = bound[0]


def draw_boxes(image, bounds, color='yellow', width=2):
        draw = ImageDraw.Draw(image)
        for bound in bounds:
            p0, p1, p2, p3 = bound[0]

def lemmatize_words(words):
    lemmatized_words = []
    for word in words:
       lemmatized_words.append(wordlemmatizer.lemmatize(word))
    return lemmatized_words

def stem_words(words):
    stemmed_words = []
    for word in words:
       stemmed_words.append(stemmer.stem(word))
    return stemmed_words

def remove_special_characters(text):
    regex = r'[^a-zA-Z0-9\s]'
    text = re.sub(regex,'',text)
    return text

def freq(words):
    words = [word.lower() for word in words]
    dict_freq = {}
    words_unique = []
    for word in words:
       if word not in words_unique:
           words_unique.append(word)
    for word in words_unique:
       dict_freq[word] = words.count(word)
    return dict_freq

def pos_tagging(text):
    pos_tag = nltk.pos_tag(text.split())
    pos_tagged_noun_verb = []
    for word,tag in pos_tag:
        if tag == "NN" or tag == "NNP" or tag == "NNS" or tag == "VB" or tag == "VBD" or tag == "VBG" or tag == "VBN" or tag == "VBP" or tag == "VBZ":
             pos_tagged_noun_verb.append(word)
    return pos_tagged_noun_verb

def tf_score(word,sentence):
    freq_sum = 0
    word_frequency_in_sentence = 0
    len_sentence = len(sentence)
    for word_in_sentence in sentence.split():
        if word == word_in_sentence:
            word_frequency_in_sentence = word_frequency_in_sentence + 1
    tf =  word_frequency_in_sentence/ len_sentence
    return tf

def idf_score(no_of_sentences,word,sentences):
    no_of_sentence_containing_word = 0
    for sentence in sentences:
        sentence = remove_special_characters(str(sentence))
        sentence = re.sub(r'\d+', '', sentence)
        sentence = sentence.split()
        sentence = [word for word in sentence if word.lower() not in Stopwords and len(word)>1]
        sentence = [word.lower() for word in sentence]
        sentence = [wordlemmatizer.lemmatize(word) for word in sentence]
        if word in sentence:
            no_of_sentence_containing_word = no_of_sentence_containing_word + 1
    idf = math.log10(no_of_sentences/no_of_sentence_containing_word)
    return idf

def tf_idf_score(tf,idf):
    return tf*idf

def word_tfidf(dict_freq,word,sentences,sentence):
    word_tfidf = []
    tf = tf_score(word,sentence)
    idf = idf_score(len(sentences),word,sentences)
    tf_idf = tf_idf_score(tf,idf)
    return tf_idf

def sentence_importance(sentence,dict_freq,sentences):
     sentence_score = 0
     sentence = remove_special_characters(str(sentence)) 
     sentence = re.sub(r'\d+', '', sentence)
     pos_tagged_sentence = [] 
     no_of_sentences = len(sentences)
     pos_tagged_sentence = pos_tagging(sentence)
     for word in pos_tagged_sentence:
          if word.lower() not in Stopwords and word not in Stopwords and len(word)>1: 
                word = word.lower()
                word = wordlemmatizer.lemmatize(word)
                sentence_score = sentence_score + word_tfidf(dict_freq,word,sentences,sentence)
     return sentence_score

def text_to_summary(input_file, length):
    file = input_file
    file = open(file , 'r')
    text = file.read()
    tokenized_sentence = sent_tokenize(text)
    text = remove_special_characters(str(text))
    text = re.sub(r'\d+', '', text)
    tokenized_words_with_stopwords = word_tokenize(text)
    tokenized_words = [word for word in tokenized_words_with_stopwords if word not in Stopwords]
    tokenized_words = [word for word in tokenized_words if len(word) > 1]
    tokenized_words = [word.lower() for word in tokenized_words]
    tokenized_words = lemmatize_words(tokenized_words)
    word_freq = freq(tokenized_words)
    input_user = length
    no_of_sentences = int((input_user * len(tokenized_sentence))/100)
    print(no_of_sentences)
    c = 1
    sentence_with_importance = {}
    for sent in tokenized_sentence:
        sentenceimp = sentence_importance(sent,word_freq,tokenized_sentence)
        sentence_with_importance[c] = sentenceimp
        c = c+1
    sentence_with_importance = sorted(sentence_with_importance.items(), key=operator.itemgetter(1),reverse=True)
    cnt = 0
    summary = []
    sentence_no = []
    for word_prob in sentence_with_importance:
        if cnt < no_of_sentences:
            sentence_no.append(word_prob[0])
            cnt = cnt+1
        else:
          break
    sentence_no.sort()
    cnt = 1
    for sentence in tokenized_sentence:
        if cnt in sentence_no:
           summary.append(sentence)
        cnt = cnt+1
    return " ".join(summary)

def text_to_summary_for_audio(file_path, len_summary = 10):
    f=open(file_path,'r')
    data=f.read().split(".")
    f.close()
    print("done")
    bow_transformer=CountVectorizer(analyzer='word').fit(data)
    message_bow=bow_transformer.transform(data)
    tfidf_transformer=TfidfTransformer().fit(message_bow)
    message_tfidf=tfidf_transformer.transform(message_bow)
    value={}
    j=0
    for i in data:
        value[i]=sum(list(message_tfidf[j].A[0]))
        j+=1
    summary_sentences = heapq.nlargest(len_summary, value, key=value.get)
    return " ".join(summary_sentences) 
    

def text_generator_for_audio(input_file):
    import requests
    import time
    import json

    secret_key = "7bb3250db66f4c92af754460ec7cf107"

# retrieve transcription results for the task
    def get_results(config):
  # endpoint to check status of the transcription task
      endpoint = "https://api.speechtext.ai/results?"
  # use a loop to check if the task is finished
      while True:
        results = requests.get(endpoint, params=config).json()
        if "status" not in results:
          break
        print("Task status: {}".format(results["status"]))
        if results["status"] == 'failed':
          print("The task is failed: {}".format(results))
          break
        if results["status"] == 'finished':
          break
    # sleep for 15 seconds if the task has the status - 'processing'
        time.sleep(15)
      return results

# loads the audio into memory
    with open(input_file, mode="rb") as file:
      post_body = file.read()

# endpoint to start a transcription task
    endpoint = "https://api.speechtext.ai/recognize?"
    header = {'Content-Type': "application/octet-stream"}

# transcription task options
    config = {
      "key" : secret_key,
      "language" : "en-US",
      "punctuation" : True,
      "format" : "mp3"
    }

# send an audio transcription request
    r = requests.post(endpoint, headers = header, params = config, data = post_body).json()

# get the id of the speech recognition task
    task = r["id"]


# get transcription results, summary, and highlights
    config = {
      "key" : secret_key,
      "task" : task,
      "summary" : True,
      "summary_size" : 15,
      "highlights" : True,
      "summary_words" : 50,
      "max_keywords" : 10
    }

    transcription = get_results(config)


# export your transcription in SRT or VTT format
    config = {
      "key" : secret_key,
      "task" : task,
      "output" : "srt",
      "max_caption_words" : 15
    }
    filename = "audio_text.txt"
    subtitles = get_results(config)

    sub = subtitles.split('\n')
    f = open('audio_text.txt','w')
    for i in range(2,len(sub),4):
        f.write(sub[i])
    f.close()
    fr=open('audio_text.txt','r')
    return filename

def main_funct(input_file, summ_length):
    input_file_ext = ''
    
    input_file_ext = input_file[-3:]
    
    print(input_file_ext)
   
    if(input_file_ext == 'pdf'):
        pdf_to_text = ocr_for_pdf(input_file)
        str1 = text_to_summary(pdf_to_text,summ_length)
        return str1
    elif(input_file_ext == "mp3" or input_file_ext == "wav" or input_file_ext == "m4a"):
        audio_to_text = text_generator_for_audio(input_file)
        summary_of_audio = text_to_summary_for_audio(audio_to_text,summ_length )
        return summary_of_audio
    elif(input_file_ext == 'txt'):
        summary_of_txt = text_to_summary(input_file, summ_length)
        return summary_of_txt

if __name__ == '__main__':
   app.run(debug = True)