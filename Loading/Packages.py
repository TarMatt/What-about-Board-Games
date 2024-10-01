#The Packages needed for the project

import xml.etree.ElementTree as ET 

## General 
from tqdm import tqdm 
import pandas as pd
import numpy as np
from scipy import stats
import math
import json
from sklearn.preprocessing import MinMaxScaler, MaxAbsScaler

## Words embedding
import gensim
from gensim.models import Word2Vec, KeyedVectors
from gensim.test.utils import datapath

## Tokenization
from spacy.displacy import render
from langdetect import detect
from nltk.tokenize import word_tokenize
from string import punctuation
import requests

## Feature engeneering
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.corpus import wordnet as wn
from nltk.corpus import sentiwordnet as swn



