from config import *
import os
from dotenv import load_dotenv
load_dotenv()
import kaggle
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from preprocess import PreProcessor

class DataHandler:
    def __init__(self, processed):
        self.__make_dirs()
        self.__download_data()
        self.__load_data(processed)
    
    def __make_dirs(self):
        if not os.path.exists(DATA_DIR):
            os.mkdir(DATA_DIR)
        self.glovePath = os.path.join(DATA_DIR, GLOVE_DIR)
        if not os.path.exists(self.glovePath):
            os.mkdir(self.glovePath)
        self.mediumPath = os.path.join(DATA_DIR, MEDIUM_DIR)
        if not os.path.exists(self.mediumPath):
            os.mkdir(self.mediumPath)
        self.stackoverflowPath = os.path.join(DATA_DIR, STACKOVERFLOW_DIR)
        if not os.path.exists(self.stackoverflowPath):
            os.mkdir(self.stackoverflowPath)

    def __download_data(self):
        self.gloveEmbeddingsFilePath = os.path.join(self.glovePath, GLOVE_EMBEDDINGS_FILE_NAME)
        if not os.path.exists(self.gloveEmbeddingsFilePath):
            kaggle.api.dataset_download_files(GLOVE_EMBEDDINGS_KAGGLE_ID, path=self.glovePath, unzip=True, quiet=False)
        self.mediumCsvFilePath = os.path.join(self.mediumPath, MEDIUM_CSV_NAME)
        if not os.path.exists(self.mediumCsvFilePath):
            kaggle.api.dataset_download_files(MEDIUM_ARTICLES_KAGGLE_ID, path=self.mediumPath, unzip=True, quiet=False)
        self.stackoverflowQuestionsCsvFilePath = os.path.join(self.stackoverflowPath, STACKOVERFLOW_QUESTIONS_CSV_NAME)
        self.stackoverflowTagsCsvFilePath = os.path.join(self.stackoverflowPath, STACKOVERFLOW_TAGS_CSV_NAME)
        if not os.path.exists(self.stackoverflowQuestionsCsvFilePath) and not os.path.exists(self.stackoverflowTagsCsvFilePath):
            kaggle.api.dataset_download_files(STACKOVERFLOW_KAGGLE_ID, path=self.stackoverflowPath, unzip=True, quiet=False)
    
    def remove_csvs(self):
        del self.articlesDataFrame
        del self.stackoverflowQuestionsDataFrame
        del self.stackoverflowTagsDataFrame
    
    def __load_data(self, processed):
        print("loading data")            
        try:
            if processed['medium']:
                self.articlesDataFrame = pd.read_csv(os.path.join(self.mediumPath, MEDIUM_PROCESSED_CSV_NAME))
            else:
                self.articlesDataFrame = pd.read_csv(self.mediumCsvFilePath)
            if processed['stackoverflow']:
                self.stackoverflowQuestionsDataFrame = pd.read_csv(os.path.join(self.stackoverflowPath, STACKOVERFLOW_PROCESSED_QUESTIONS_CSV_NAME), encoding = "ISO-8859-1")
            else:
                self.stackoverflowQuestionsDataFrame = pd.read_csv(self.stackoverflowQuestionsCsvFilePath, encoding = "ISO-8859-1")

            self.stackoverflowTagsDataFrame = pd.read_csv(self.stackoverflowTagsCsvFilePath, encoding = "ISO-8859-1")
        except Exception as e:
            print(f"ERROR: no csv found: {e}")

class RecommendationSystem:

    def __init__(self) -> None:
        self.stackDir = os.path.join(DATA_DIR, STACKOVERFLOW_DIR)
        self.mediumDir = os.path.join(DATA_DIR, MEDIUM_DIR)
        processed = self.__check_if_processed()
        self.dataHandler = DataHandler(processed)
        self.dataPreProcessor = PreProcessor()
        self.dataPreProcessor.preprocess(processed, self.dataHandler.stackoverflowQuestionsDataFrame, self.stackProcessedCsv, self.dataHandler.articlesDataFrame, self.mediumProcessedCsv)
        self.__load_glove_embeddings()
    
    def __check_if_processed(self):
        processed = {
            'stackoverflow': False,
            'medium': False
        }
        self.stackProcessedCsv = os.path.join(self.stackDir, STACKOVERFLOW_PROCESSED_QUESTIONS_CSV_NAME)
        if os.path.exists(self.stackProcessedCsv):
            processed['stackoverflow'] = True
        self.mediumProcessedCsv = os.path.join(self.mediumDir, MEDIUM_PROCESSED_CSV_NAME)
        if os.path.exists(self.mediumProcessedCsv):
            processed['medium'] = True
        print(processed)
        return processed
 
    def __load_glove_embeddings(self):
        print("loading embeddings")
        embeddingsMatrix = {}
        with open(self.dataHandler.gloveEmbeddingsFilePath, encoding='utf-8') as f:
            for line in f:
                values = line.split()
                word = values[0]
                embedding = np.asarray(values[1:], dtype='float32')
                embeddingsMatrix[word] = embedding
        self.embeddingsMatrix = embeddingsMatrix