from config import *
import os
from dotenv import load_dotenv
load_dotenv()
import kaggle
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from preprocess import PreProcessor
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', filename=LOG_FILE_PATH)
logger = logging.getLogger(__name__)

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
        logger.info("loading data")            
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
            logger.info(f"ERROR: no csv found: {e}")

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
        logger.info(f"status of preprocessed files: {processed}")
        return processed
 
    def __load_glove_embeddings(self):
        logger.info("loading embeddings")
        embeddingsMatrix = {}
        with open(self.dataHandler.gloveEmbeddingsFilePath, encoding='utf-8') as f:
            for line in f:
                values = line.split()
                word = values[0]
                embedding = np.asarray(values[1:], dtype='float32')
                embeddingsMatrix[word] = embedding
        self.embeddingsMatrix = embeddingsMatrix
    
    def __sentence_to_embeddings(self, sentence):
        words = sentence.lower().split()
        embeddings = [self.embeddingsMatrix[word] for word in words if word in self.embeddingsMatrix]

        return np.mean(embeddings, axis=0)
    
    def __filter_df_using_tag(self, tag):
        logger.info("filtering now")
        tagIds = self.dataHandler.stackoverflowTagsDataFrame.loc[self.dataHandler.stackoverflowTagsDataFrame['Tag'] == tag]['Id']
        filteredStackDf = self.dataHandler.stackoverflowQuestionsDataFrame[self.dataHandler.stackoverflowQuestionsDataFrame['Id'].isin(tagIds)]
        filteredMediumDf = self.dataHandler.articlesDataFrame[self.dataHandler.articlesDataFrame['tags'].apply(lambda x: tag in x)]

        return filteredStackDf, filteredMediumDf

    def __get_top_similar_stackoverflow(self, sentence, stackoverflowDf, n):
        logger.info("get similar stackoverflow")
        sentence_embedding = self.__sentence_to_embeddings(sentence).reshape(1, -1)
        similarQuestions = []
        for index, row in stackoverflowDf.iterrows():
            try:
                other_sentence_embedding = self.__sentence_to_embeddings(row['Title']).reshape(1, -1)
                similarity = cosine_similarity(sentence_embedding, other_sentence_embedding)[0]
                if similarity > SIMILARITY_THRESHOLD:
                    similarQuestions.append({
                        'id': row['Id'],
                        'title': row['Title'],
                        'similarity': similarity
                    })
            except Exception as e:
                logger.error(f"{e} no embeddings present for stackoverflow question: {row['Title']}")

        similarQuestions.sort(key=lambda x: x['similarity'], reverse=True)
        similarQuestions = similarQuestions[:n]

        return similarQuestions

    def __get_top_similar_medium(self, sentence, mediumDf, n):
        logger.info("get similar medium")
        sentenceEmbedding = self.__sentence_to_embeddings(sentence).reshape(1, -1)
        similarArticles = []
        for index, row in mediumDf.iterrows():
            try:
                articleContentEmbedding = self.__sentence_to_embeddings(row['text']).reshape(1, -1)
                similarity = cosine_similarity(sentenceEmbedding, articleContentEmbedding)[0]
                if similarity > SIMILARITY_THRESHOLD:
                    similarArticles.append({
                        'title': row['title'],
                        'url': row['url'],
                        'tags': row['tags'],
                        'similarity': similarity
                    })
            except Exception as e:
                logger.error(f"error: {e} for medium article: {row['title']}")

        similarArticles.sort(key=lambda x: x['similarity'], reverse=True)
        similarArticles = similarArticles[:n]

        return similarArticles

    def recommend(self, sentence, tag=None, n=1):
        logger.info(f"start recommendation for '{sentence}'")
        sentence = self.dataPreProcessor.clean_text(sentence)
        if tag:
            stackoverflowFilteredDf, mediumFilteredDf = self.__filter_df_using_tag(tag)
            stackoverflowSimilarData = self.__get_top_similar_stackoverflow(sentence, stackoverflowFilteredDf, n)
            mediumSimilarData = self.__get_top_similar_medium(sentence, mediumFilteredDf, n)
        else:
            stackoverflowSimilarData = self.__get_top_similar_stackoverflow(sentence, self.dataHandler.stackoverflowQuestionsDataFrame, n)
            mediumSimilarData = self.__get_top_similar_medium(sentence, self.dataHandler.articlesDataFrame, n)
        logger.info(f"finish recommendation for '{sentence}'")
        return stackoverflowSimilarData, mediumSimilarData