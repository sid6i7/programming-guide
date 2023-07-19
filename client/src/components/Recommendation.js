import React from 'react';
import stackoverflowBanner from '../images/stackoverflow.png';
import mediumBanner from '../images/medium.png';

export const Recommendation = ({ stackoverflow, medium, question }) => {
  if (!stackoverflow && !medium) {
    return null;
  }

  return (
    <div className='text-center'>
      <h1>Recommendations</h1>
      <h3>Q) {question}</h3>
      <div className="d-flex justify-content-center align-items-center mb-4">
        <img src={stackoverflowBanner} alt="Stackoverflow Posts" className="img-fluid" style={{ maxHeight: '100px' }} />
      </div>

      <div className="row row-cols-1 row-cols-md-4 g-4 justify-content-center">
        {stackoverflow?.map((question) => (
          <div key={question.id} className="col">
            <div className="card">
              <div className="card-body">
                <h5 className="card-title">{question.title}</h5>
                <p className="card-text">Similarity: {question.similarity}%</p>
                <a href={`https://stackoverflow.com/questions/${question.id}`} target='_blank' className="btn btn-warning">Read More</a>
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="d-flex justify-content-center align-items-center mb-4"> {/* Add mb-4 for margin-bottom */}
        <img src={mediumBanner} alt="Medium Articles" className="img-fluid" style={{ maxHeight: '100px' }} />
      </div>

      <div className="row row-cols-1 row-cols-md-2 g-4 justify-content-center"> {/* Add justify-content-center */}
        {medium?.map((article) => (
          <div key={article.title} className="col">
            <div className="card">
              <div className="card-body">
                <h5 className="card-title">{article.title}</h5>
                <p className="card-text"><strong>Similarity: </strong>{article.similarity}%</p>
                <p className="card-text"><strong>Tags:</strong> {article.tags.slice(1, -1).replace(/'/g, '')}</p>
                <a href={article.url} target='_blank' className="btn btn-dark">Read More</a>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
