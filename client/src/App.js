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
    </div>
  );
}

export default App;