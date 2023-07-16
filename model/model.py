from config import *
import os
from dotenv import load_dotenv
load_dotenv()
import kaggle
import numpy as np
import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
nltk.download('stopwords')
nltk.download('punkt')
from scipy.spatial.distance import cosine

class DataHandler:
    def __init__(self):
        if not os.path.exists(DATA_DIR):
            os.mkdir(DATA_DIR)
        self.glovePath = os.path.join(DATA_DIR, GLOVE_DIR)
        if not os.path.exists(self.glovePath):
            os.mkdir(self.glovePath)
        self.mediumPath = os.path.join(DATA_DIR, MEDIUM_DIR)
        if not os.path.exists(self.mediumPath):
            os.mkdir(self.mediumPath)
        self.__download_data()

    def __download_data(self):
        self.gloveEmbeddingsFilePath = os.path.join(self.glovePath, GLOVE_EMBEDDINGS_NAME)
        if not os.path.exists(self.gloveEmbeddingsFilePath):
            kaggle.api.dataset_download_files(GLOVE_EMBEDDINGS_ID, path=self.glovePath, unzip=True, quiet=False)
        self.mediumCsvFilePath = os.path.join(self.mediumPath, MEDIUM_CSV_NAME)
        if not os.path.exists(self.mediumCsvFilePath):
            kaggle.api.dataset_download_files(MEDIUM_ARTICLES_ID, path=self.mediumPath, unzip=True, quiet=False)