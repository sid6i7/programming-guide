from model.config import *
import re
from nltk.tokenize import word_tokenize
from bs4 import BeautifulSoup
import nltk
from tqdm import tqdm
tqdm.pandas()
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
nltk.download('stopwords')
nltk.download('punkt')
import ast
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', filename=LOG_FILE_PATH)
logger = logging.getLogger(__name__)

class PreProcessor:
    """
    A class responsible for preprocessing text data.

    Attributes:
        stopWords (list): A list of stop words used for text cleaning.

    Methods:
        __init__(self): Initializes the PreProcessor object and downloads necessary resources.
        preprocess(self, processed, stackDf=None, stackPath=None, mediumDf=None, mediumPath=None): Preprocesses the data for Stack Overflow and Medium.
        preprocess_stackoverflow(self, stackDf, stackCsvPath): Preprocesses the Stack Overflow data.
        preprocess_medium(self, mediumDf, mediumCsvPath): Preprocesses the Medium data.
        __parse_q_body(self, body): Parses the Stack Overflow question body to extract sentences and code blocks.
        clean_text(self, text): Cleans and tokenizes the input text.
    """
    def __init__(self) -> None:
        """
        Initializes the PreProcessor object and downloads necessary resources.
        """
        self.stopWords = stopwords.words('english')
    
    def preprocess(self, processed, stackDf=None, stackPath = None, mediumDf=None, mediumPath = None):
        """
        Preprocesses the data for Stack Overflow and Medium.

        Args:
            processed (dict): A dictionary indicating whether the data is processed for Stack Overflow and Medium.
            stackDf (pandas.DataFrame, optional): The dataframe containing Stack Overflow data. Defaults to None.
            stackCsvPath (str, optional): The file path to save the preprocessed Stack Overflow data. Defaults to None.
            mediumDf (pandas.DataFrame, optional): The dataframe containing Medium data. Defaults to None.
            mediumCsvPath (str, optional): The file path to save the preprocessed Medium data. Defaults to None.
        """
        if not processed['stackoverflow']:
            self.preprocess_stackoverflow(stackDf, stackPath)
            processed['stackoverflow'] = True
        if not processed['medium']:
            self.preprocess_medium(mediumDf, mediumPath)
            processed['medium'] = True
        return processed
        
    def preprocess_stackoverflow(self, stackDf, stackCsvPath):
        """
        Preprocesses the Stack Overflow data.

        Args:
            stackDf (pandas.DataFrame): The dataframe containing Stack Overflow data.
            stackCsvPath (str): The file path to save the preprocessed Stack Overflow data.
        """
        logger.info("preprocessing stackoverflow")
        stackDf['Body_sentence'], stackDf['Body_code'] = zip(*stackDf['Body'].progress_apply(self.__parse_q_body))
        stackDf['Body_sentence'] = stackDf['Body_sentence'].progress_apply(self.clean_text)
        stackDf['Title_processed'] = stackDf['Title'].progress_apply(self.clean_text)
        stackDf['question'] = stackDf['Title'] + ". " + stackDf['Body_sentence']
        stackDf[['Id', 'Title', 'Title_processed', 'question']].to_csv(stackCsvPath, escapechar='\\')

    def preprocess_medium(self, mediumDf, mediumCsvPath):
        """
        Preprocesses the Medium data.

        Args:
            mediumDf (pandas.DataFrame): The dataframe containing Medium data.
            mediumCsvPath (str): The file path to save the preprocessed Medium data.
        """
        logger.info("preprocessing medium")
        mediumDf['text'] = mediumDf['text'].progress_apply(self.clean_text)
        mediumDf['tags'] = mediumDf['tags'].progress_apply(ast.literal_eval)
        mediumDf['tags'] = mediumDf['tags'].progress_apply(lambda tags: [tag.lower() for tag in tags])
        mediumDf[['title', 'text', 'url', 'tags']].to_csv(mediumCsvPath)

    def __parse_q_body(self, body):
        """
        Parses the Stack Overflow question body to extract sentences and code blocks.

        Args:
            body (str): The HTML-formatted body of the Stack Overflow question.

        Returns:
            tuple: A tuple containing the extracted sentences and code blocks as strings.
        """
        soup = BeautifulSoup(body, 'html.parser')
        # english part of the body
        sentenceBlocks = soup.find_all('p')
        sentences = ". ".join([sentenceBlock.get_text() for sentenceBlock in sentenceBlocks])
        # code part of the body
        codeBlocks = soup.find_all('code')
        codeTexts = "\n".join([code.get_text() for code in codeBlocks])

        return sentences, codeTexts

    def clean_text(self, text):
        """
        Cleans and tokenizes the input text.

        Args:
            text (str): The input text to be cleaned.

        Returns:
            str: The cleaned and tokenized text.
        """
        text = re.sub(r'https?://\S+|www\.\S+', '', text)
        text = re.sub(r'<.*?>', '', text)

        for x in text.lower():
            if x in PUNCTUATIONS:
                text = text.replace(x, "")

        text = text.lower()
        text = ' '.join([word for word in word_tokenize(text) if word not in self.stopWords])
        text = re.sub(r'\s+', ' ', text).strip().replace('’', '')

        return text