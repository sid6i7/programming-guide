import React, { useState } from 'react';
import logo from './logo.svg';
import './App.css';
import { Banner } from './components/Banner';
import { Form } from './components/Form';
import { Recommendation } from './components/Recommendation';

function App() {
  const [recommendation, setRecommendation] = useState();

  const handleRecommendation = (stackoverflow, medium, question) => {
    setRecommendation({ stackoverflow, medium, question });
  };

  return (
    <div>
      <Banner />
      <Form onRecommendation={handleRecommendation} />
      {recommendation && (
        <div className="mt-5">
          <Recommendation
            stackoverflow={recommendation.stackoverflow}
            medium={recommendation.medium}
            question={recommendation.question}
          />
        </div>
      )}
    </div>
  );
}

export default App;