
  <a name="readme-top"></a>

  <p align="center">
    <h1>Programming Guide</h1>
  </p>

  <h2>Table of Contents</h2>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#motivation">Motivation</a></li>
        <li><a href="#flow">Flow</a></li>
        <li><a href="#built-with">Built With</a></li>
        <li><a href="#data-source">Data Source</a></li>
        <li><a href="#project-structure">Project Structure</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <ul>
        <li>App</li>
        <li>Output</li>
    </ul>
    <li><a href="#references">References</a></li>
  </ol>

## About The Project

This is a project that aims to provide you with answers for your programming questions by finding and displaying similar questions from stackoverflow and any similar articles from medium.

It uses stackoverflow data as well as medium articles data available on kaggle for the recommendations.

The sentences are embedded using GloVe embeddings, data is filtered on the basis of tags provided and then cosine similarity is used to get top n most similar stackoverflow questions and medium articles.

### Motivation
Instead of doing multiple searches on stackoverflow, medium, geeksforgeeks etc, I have always wanted a one-stop solution for any programming related question that I have had like "how to reverse a string in javascript".

Even though, a simple google search already achieves this but I still wanted to understand how it does that. Ever since I started programming, I have always had a dream to create a search engine/recommendation engine only for programming. This project is a very small proof of concept that its indeed possible to achieve that.

### Flow
<div style="display: flex; justify-content: center;">
  <img src="./src/images/flow.png" alt="App">
</div>

### Built With

- **Frontend**: [ReactJS](https://react.dev/)
- **Backend**: [FastAPI](https://fastapi.tiangolo.com/)
- **Model**: [GloVe](https://nlp.stanford.edu/projects/glove/) + [Cosine Similarity](https://www.sciencedirect.com/topics/computer-science/cosine-similarity)
- **Web Server**: [Nginx](https://www.nginx.com/)

### Data Source
Both the datasets were sourced from kaggle.
- **Stackoverflow**: [StackSample: 10% of Stack Overflow Q&A](https://www.kaggle.com/datasets/stackoverflow/stacksample)
- **Medium**: [190k+ Medium Articles](https://www.kaggle.com/datasets/fabiochiusano/medium-articles)

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Project Structure
```
├── backend/
│   ├── model/
│   │   ├── config.py
│   │   ├── model.py
│   │   └── preprocess.py
│   ├── server/
│   │   └── api.py
│   ├── .dockerignore
│   ├── .gitignore
│   ├── Dockerfile
│   └── requirements.txt
├── client/
│   ├── nginx/
│   │   ├── default.conf
│   │   └── Dockerfile
│   ├── node_modules
│   ├── public
│   ├── src
│   ├── .dockerignore
│   ├── .gitignore
│   ├── Dockerfile
│   ├── package-lock.json
│   └── package.json
├── nginx/
│   ├── default.conf
│   └── Dockerfile
├── src/
│   ├── app.png
│   ├── banner.png
│   ├── medium_demo.png
│   └── stackoverflow_demo.png
├── .gitignore
├── docker-compose.yml
└── README.md
```

## Getting Started

The project is dockerized and makes use of docker compose. Therefore the only thing that you need in order to run the project is docker.

### Prerequisites

* Docker: [How to install docker?](https://docs.docker.com/get-docker/)
  
### Installation

1. Get kaggle API key. [How to get a kaggle API key?](https://christianjmills.com/posts/kaggle-obtain-api-key-tutorial/)
   
2. Store kaggle API credentials as an .env file in the root directory. It should be in the following format
    ```
    KAGGLE_USERNAME = your_kaggle_username
    KAGGLE_KEY = your_api_key
    ```
3. Run docker compose in the root directory.
   ```sh
   docker compose up
   ```
The project should be up when you visit localhost.

**Note**: First run **might take time** because it downloads the data, loads it in memory, pre-processes it and finally stores it for further use.


### About Config
Following variables can hugely affect the quality of recommendations. These can be changed in the **config.py**.

**SIMILARITY_THRESHOLD**: Is used to compare how similar the input question should be to the title of the related stackoverflow questions as well as title of the medium articles.
- It can range from 0 to 100
- Increase this to increase quality of recommendation
- Increasing it too much might lead to no results in some cases.

**PERCENTAGE_MEDIUM_DATA**: Amount of medium articles data to use. If you wish to change this, don't forget to delete the preprocessed csv file for medium articles found in ./backend/model/data/medium_articles/medium_processed.csv
- It can range from 0 to 100
- Increasing this might lead to increase in quality of recommendations but willwill also increase the computation in terms of RAM and CPU.

**PERCENTAGE_STACKOVERFLOW_DATA**: Amount of stackoverflow data to use. If you wish to change this, don't forget to delete the preprocessed csv file for stackoverflow questions found in ./backend/model/data/stackoverflow/stack_questions_processed.csv
- It can range from 0 to 100
- Increasing this might lead to increase in quality of recommendations but will also increase the computation in terms of RAM and CPU.

**GLOVE_EMBEDDINGS_FILE_NAME**: The type of GloVe embeddings to use. There are four options available for this. The varying number (50, 100, 200, 300) indicates the size/length of the vector that each word gets represented by.

Choosing a higher dimensional embeddings might lead to better recommendations but will again require more computation in terms of RAM and CPU.

**Options are:**
- glove.6B.50d.txt
- glove.6B.100d.txt
- glove.6B.200d.txt
- glove.6B.300d.txt

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Usage

### App
<div style="display: flex; justify-content: center;">
  <img src="./src/images/app.png" alt="App">
</div>
<hr>

**Question**: Any programming question.

**Language**: Programming language associated with the question.

**Count**: Number of recommendations to get each for stackoverflow and medium.

<hr>

### Output

#### Stackoverflow
<div style="display: flex; justify-content: center;">
  <img src="./src/images/stackoverflow_demo.png" alt="App">
</div>
<hr>

#### Medium
<div style="display: flex; justify-content: center;">
  <img src="./src/images/medium_demo.png" alt="App">
</div>
<hr>

## References

* [GloVe Embeddings](https://nlp.stanford.edu/pubs/glove.pdf)
* [Docker Documentation](https://docs.docker.com/reference/)
* [React JS Documentation](https://react.dev/reference/react)
* [Pandas Documentation](https://pandas.pydata.org/docs/)
* [Numpy Documentation](https://numpy.org/doc/)
* [NLTK Documentation](https://www.nltk.org/api/nltk.html)
* [Nginx Documentation](http://nginx.org/en/docs/)
  
<p align="right">(<a href="#readme-top">back to top</a>)</p>