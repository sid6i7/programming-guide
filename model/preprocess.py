from config import *
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

class PreProcessor:
    def __init__(self) -> None:
        self.stopWords = stopwords.words('english')
    
    def preprocess(self, processed, stackDf=None, stackPath = None, mediumDf=None, mediumPath = None):
        if not processed['stackoverflow']:
            self.preprocess_stackoverflow(stackDf, stackPath)
        if not processed['medium']:
            self.preprocess_medium(mediumDf, mediumPath)
        
    def preprocess_stackoverflow(self, stackDf, stackCsvPath):
        print("preprocessing stackoverflow")
        stackDf['Body_sentence'], stackDf['Body_code'] = zip(*stackDf['Body'].progress_apply(self.__parse_q_body))
        stackDf['Body_sentence'] = stackDf['Body_sentence'].progress_apply(self.clean_text)
        stackDf['Title'] = stackDf['Title'].progress_apply(self.clean_text)
        stackDf['question'] = stackDf['Title'] + ". " + stackDf['Body_sentence']
        stackDf[['Id', 'Title', 'question']].to_csv(stackCsvPath)

    def preprocess_medium(self, mediumDf, mediumCsvPath):
        print("preprocessing medium")
        mediumDf['text'] = mediumDf['text'].progress_apply(self.clean_text)
        mediumDf['tags'] = mediumDf['tags'].progress_apply(ast.literal_eval)
        mediumDf['tags'] = mediumDf['tags'].progress_apply(lambda tags: [tag.lower() for tag in tags])
        mediumDf[['title', 'text', 'url', 'tags']].to_csv(mediumCsvPath)

    def __parse_q_body(self, body):
        soup = BeautifulSoup(body, 'html.parser')
        # english part of the body
        sentenceBlocks = soup.find_all('p')
        sentences = ". ".join([sentenceBlock.get_text() for sentenceBlock in sentenceBlocks])
        # code part of the body
        codeBlocks = soup.find_all('code')
        codeTexts = "\n".join([code.get_text() for code in codeBlocks])

        return sentences, codeTexts

    def clean_text(self, text):
        text = re.sub(r'https?://\S+|www\.\S+', '', text)
        text = re.sub(r'<.*?>', '', text)

        for x in text.lower():
            if x in PUNCTUATIONS:
                text = text.replace(x, "")

        text = text.lower()
        text = ' '.join([word for word in word_tokenize(text) if word not in self.stopWords])
        text = re.sub(r'\s+', ' ', text).strip().replace('’', '')

        return text