from model.config import *
import os
from dotenv import load_dotenv
load_dotenv()
import kaggle
import zipfile
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from model.preprocess import PreProcessor
import logging
import random

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', filename=LOG_FILE_PATH)
logger = logging.getLogger(__name__)

class DataHandler:
    """
    A class responsible for handling data download, preprocessing, and loading.

    Attributes:
        processed (dict): A dictionary indicating whether the data is processed for Stack Overflow and Medium.

    Methods:
        __init__(self, processed): Initializes the DataHandler object and downloads, preprocesses, and loads the data.
        __make_dirs(self): Creates necessary directories for data storage if they don't exist.
        __download_data(self): Downloads necessary data files if they don't exist.
        remove_csvs(self): Removes the loaded CSV data from memory.
        __load_data(self, processed): Loads the data from CSV files.
    """

    def __init__(self, processed):
        """
        Initializes the DataHandler object and downloads, preprocesses, and loads the data.

        Args:
            processed (dict): A dictionary indicating whether the data is processed for Stack Overflow and Medium.
        """
        self.__make_dirs()
        self.__download_data()
        self.__load_data(processed)
    
    def __make_dirs(self):
        """
        Creates necessary directories for data storage if they don't exist.
        """
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
        """
        Downloads necessary data files if they don't exist.
        """
        self.gloveEmbeddingsFilePath = os.path.join(self.glovePath, GLOVE_EMBEDDINGS_FILE_NAME)
        if not os.path.exists(self.gloveEmbeddingsFilePath):
            kaggle.api.dataset_download_files(GLOVE_EMBEDDINGS_KAGGLE_ID, path=self.glovePath, unzip=True, quiet=False)
        self.mediumCsvFilePath = os.path.join(self.mediumPath, MEDIUM_CSV_NAME)
        if not os.path.exists(self.mediumCsvFilePath):
            kaggle.api.dataset_download_files(MEDIUM_ARTICLES_KAGGLE_ID, path=self.mediumPath, unzip=True, quiet=False)
        self.stackoverflowQuestionsCsvFilePath = os.path.join(self.stackoverflowPath, STACKOVERFLOW_QUESTIONS_CSV_NAME)
        self.stackoverflowTagsCsvFilePath = os.path.join(self.stackoverflowPath, STACKOVERFLOW_TAGS_CSV_NAME)
        if not os.path.exists(self.stackoverflowQuestionsCsvFilePath) and not os.path.exists(self.stackoverflowTagsCsvFilePath):
            for csv in STACKOVERFLOW_DOWNLOAD_FILES:
                kaggle.api.dataset_download_file(STACKOVERFLOW_KAGGLE_ID, path=self.stackoverflowPath,quiet=False, file_name=csv)
                zipPath = f"{os.path.join(self.stackoverflowPath, csv)}.zip"
                with zipfile.ZipFile(zipPath, 'r') as zip_ref:
                    zip_ref.extractall(self.stackoverflowPath)
                os.remove(zipPath)

    def remove_csvs(self):
        """
        Removes the loaded CSV data from memory.
        """
        del self.articlesDataFrame
        del self.stackoverflowQuestionsDataFrame
        del self.stackoverflowTagsDataFrame
    
    def __load_data(self, processed):
        """
        Loads the data from CSV files.

        Args:
            processed (dict): A dictionary indicating whether the data is processed for Stack Overflow and Medium.
        """
        logger.info("loading data")
        try:
            if processed['medium']:
                self.articlesDataFrame = pd.read_csv(os.path.join(self.mediumPath, MEDIUM_PROCESSED_CSV_NAME))
            else:
                self.articlesDataFrame = pd.read_csv(self.mediumCsvFilePath, skiprows=lambda i: i > 0 and random.random() > PERCENTAGE_MEDIUM_DATA / 100)

            if processed['stackoverflow']:
                self.stackoverflowQuestionsDataFrame = pd.read_csv(os.path.join(self.stackoverflowPath, STACKOVERFLOW_PROCESSED_QUESTIONS_CSV_NAME), encoding="ISO-8859-1")
            else:
                self.stackoverflowQuestionsDataFrame = pd.read_csv(self.stackoverflowQuestionsCsvFilePath, encoding="ISO-8859-1", skiprows=lambda i: i > 0 and random.random() > PERCENTAGE_STACKOVERFLOW_DATA / 100)

            self.stackoverflowTagsDataFrame = pd.read_csv(self.stackoverflowTagsCsvFilePath, encoding="ISO-8859-1")
        except Exception as e:
            logger.info(f"ERROR: no csv found: {e}")

class RecommendationSystem:
    """
    A class representing the recommendation system.

    Methods:
        __init__(self): Initializes the RecommendationSystem object and sets up the necessary components.
        __check_if_processed(self): Checks if data for Stack Overflow and Medium is already processed.
        __load_glove_embeddings(self): Loads the pre-trained GloVe word embeddings.
        __sentence_to_embeddings(self, sentence): Converts a sentence to its word embeddings.
        __filter_df_using_tag(self, tags): Filters the dataframes based on input tags.
        __get_top_similar_stackoverflow(self, sentence, stackoverflowDf, n): Retrieves top similar Stack Overflow questions.
        __get_top_similar_medium(self, sentence, mediumDf, n): Retrieves top similar Medium articles.
        recommend(self, sentence, tags=None, n=1): Recommends Stack Overflow questions and Medium articles based on input.
    """

    def __init__(self) -> None:
        """
        Initializes the RecommendationSystem object and prepares the data.
        """
        self.stackDir = os.path.join(DATA_DIR, STACKOVERFLOW_DIR)
        self.mediumDir = os.path.join(DATA_DIR, MEDIUM_DIR)
        processed = self.__check_if_processed()
        self.dataHandler = DataHandler(processed)
        self.dataPreProcessor = PreProcessor()
        self.dataPreProcessor.preprocess(processed, self.dataHandler.stackoverflowQuestionsDataFrame, self.stackProcessedCsv, self.dataHandler.articlesDataFrame, self.mediumProcessedCsv)
        self.__load_glove_embeddings()
    
    def __check_if_processed(self):
        """
        Checks if the data is already preprocessed.

        Returns:
            dict: A dictionary indicating whether the data is processed for Stack Overflow and Medium.
        """
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
        """
        Loads the GloVe word embeddings into memory.
        """
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
        """
        Converts a sentence into word embeddings using the GloVe embeddings.

        Args:
            sentence (str): The input sentence to convert.

        Returns:
            numpy.array: The average word embeddings of the input sentence.
        """
        words = sentence.lower().split()
        embeddings = [self.embeddingsMatrix[word] for word in words if word in self.embeddingsMatrix]
        if len(embeddings) == 0:
            return None
        else:
            return np.mean(embeddings, axis=0)
    
    def __filter_df_using_tag(self, tags):
        """
        Filters the Stack Overflow and Medium dataframes based on the provided tags.

        Args:
            tags (list): A list of tags to filter the dataframes.

        Returns:
            pandas.DataFrame, pandas.DataFrame: Filtered dataframes for Stack Overflow and Medium.
        """
        logger.info("filtering now")

        tagIds = self.dataHandler.stackoverflowTagsDataFrame.loc[self.dataHandler.stackoverflowTagsDataFrame['Tag'].isin(tags)]['Id']
        filteredStackDf = self.dataHandler.stackoverflowQuestionsDataFrame[self.dataHandler.stackoverflowQuestionsDataFrame['Id'].isin(tagIds)]
        filteredMediumDf = self.dataHandler.articlesDataFrame[self.dataHandler.articlesDataFrame['tags'].apply(lambda x: any(tag in x for tag in tags))]
        filteredStackDf.dropna(subset=['Title_processed'], inplace=True)
        filteredMediumDf.dropna(subset = ['title'], inplace=True)
        return filteredStackDf, filteredMediumDf

    def __get_top_similar_stackoverflow(self, sentence, stackoverflowDf, n):
        """
        Finds the top-n similar Stack Overflow questions to the input sentence.

        Args:
            sentence (str): The input sentence to find similar questions to.
            stackoverflowDf (pandas.DataFrame): The dataframe containing Stack Overflow questions.
            n (int): The number of similar questions to return.

        Returns:
            list: A list of dictionaries containing top-n similar Stack Overflow questions with their ids, titles, and similarities.
        """
        sentence_embedding = self.__sentence_to_embeddings(sentence).reshape(1, -1)

        other_sentence_embeddings = stackoverflowDf['Title_processed'].apply(self.__sentence_to_embeddings)
        other_sentence_embeddings.dropna(inplace=True)
        sentence_embedding = sentence_embedding.reshape(1, -1)

        indices = other_sentence_embeddings.index
        other_sentence_embeddings = np.stack(other_sentence_embeddings.values)

        similarities = cosine_similarity(sentence_embedding, other_sentence_embeddings).squeeze()
        similarities = np.round(similarities * 100, 2)

        index_similarity_dict = dict(zip(indices, similarities))

        relevant_indices = [index for index, similarity in index_similarity_dict.items() if similarity > SIMILARITY_THRESHOLD]
        similar_questions_data = stackoverflowDf.loc[relevant_indices]

        similarQuestions = []
        for _, row in similar_questions_data.iterrows():
            similarity = float(index_similarity_dict[row.name])
            similarQuestions.append({
                'id': row['Id'],
                'title': row['Title'],
                'similarity': similarity
            })

        similarQuestions.sort(key=lambda x: x['similarity'], reverse=True)
        similarQuestions = similarQuestions[:n]

        return similarQuestions

    def __get_top_similar_medium(self, sentence, mediumDf, n):
        """
        Finds the top-n similar Medium articles to the input sentence.

        Args:
            sentence (str): The input sentence to find similar articles to.
            mediumDf (pandas.DataFrame): The dataframe containing Medium articles.
            n (int): The number of similar articles to return.

        Returns:
            list: A list of dictionaries containing top-n similar Medium articles with their titles, URLs, tags, and similarities.
        """
        logger.info("get similar medium")
        articleEmbedding = self.__sentence_to_embeddings(sentence).reshape(1, -1)
        other_article_embeddings = mediumDf['text'].apply(self.__sentence_to_embeddings)

        other_article_embeddings.dropna(inplace=True)
        indices = other_article_embeddings.index
        other_article_embeddings = np.stack(other_article_embeddings.values)

        similarities = cosine_similarity(articleEmbedding, other_article_embeddings).squeeze()
        similarities = np.round(similarities * 100, 2)

        index_similarity_dict = dict(zip(indices, similarities))

        relevant_indices = [index for index, similarity in index_similarity_dict.items() if similarity > SIMILARITY_THRESHOLD]

        similar_articles_data = mediumDf.loc[relevant_indices]

        similarArticles = []
        for _, row in similar_articles_data.iterrows():
            similarity = float(index_similarity_dict[row.name])
            similarArticles.append({
                'title': row['title'],
                'url': row['url'],
                'tags': row['tags'],
                'similarity': similarity
            })

        similarArticles.sort(key=lambda x: x['similarity'], reverse=True)
        similarArticles = similarArticles[:n]

        return similarArticles

    def recommend(self, sentence, tags=None, n=1):
        """
        Recommends similar content based on user input.

        Args:
            sentence (str): The input sentence to find similar content to.
            tags (list, optional): A list of tags to filter the content. Defaults to None.
            n (int, optional): The number of recommendations to return. Defaults to 1.

        Returns:
            tuple: A tuple containing two lists of recommended content from Stack Overflow and Medium, respectively.
        """
        logger.info(f"start recommendation for '{sentence}'")
        sentence = self.dataPreProcessor.clean_text(sentence)
        if tags:
            stackoverflowFilteredDf, mediumFilteredDf = self.__filter_df_using_tag(tags)
            stackoverflowSimilarData = self.__get_top_similar_stackoverflow(sentence, stackoverflowFilteredDf, n)
            mediumSimilarData = self.__get_top_similar_medium(sentence, mediumFilteredDf, n)
        else:
            stackoverflowSimilarData = self.__get_top_similar_stackoverflow(sentence, self.dataHandler.stackoverflowQuestionsDataFrame, n)
            mediumSimilarData = self.__get_top_similar_medium(sentence, self.dataHandler.articlesDataFrame, n)
        logger.info(f"finish recommendation for '{sentence}'")
        return stackoverflowSimilarData, mediumSimilarData