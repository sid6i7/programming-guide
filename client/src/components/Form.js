import React, { useState } from 'react';
import CreatableSelect from 'react-select/creatable';
import InputSlider from 'react-input-slider';

export const Form = ({ onRecommendation }) => {
  const [selectedOptions, setSelectedOptions] = useState([]);
  const [numRecommendations, setNumRecommendations] = useState(1);
  const [isLoading, setIsLoading] = useState(false);

  const handleSelectChange = (newValue) => {
    setSelectedOptions(newValue);
  };

  const handleSliderChange = (value) => {
    setNumRecommendations(value.x);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const form = e.currentTarget;
    if (form.checkValidity()) {
      onRecommendation(null);
      
      setIsLoading(true);
      try {
        
      } catch (error) {
        console.log(`Error occurred: ${error}`);
      } finally {
        setIsLoading(false);
      }
    } else {
      e.stopPropagation();
      form.classList.add('was-validated');
    }
  };

  return (
    <div className="d-flex justify-content-center">
      <form className="p-4 needs-validation" style={{ minWidth: '500px', maxWidth: '800px' }} onSubmit={handleSubmit} noValidate>
        <div className="form-group">
          <h2><label htmlFor="question">Question</label></h2>
          <input type="text" className="form-control" id="question" name="question" placeholder="Enter a question" required />
          <div className="invalid-feedback">Please enter a question.</div>
          <h2>Language</h2>
          <small>Associated with the question</small>
          <CreatableSelect
            options={[]}
            isMulti={true}
            onChange={handleSelectChange}
            value={selectedOptions}
          />
        </div>
        <h2>Count</h2>
        <small>No. of recommendations</small>
        <div className="form-group">
          <InputSlider
            axis="x"
            x={numRecommendations}
            xmin={1}
            xmax={10}
            onChange={handleSliderChange}
          />
          <div>{numRecommendations}</div>
        </div>
        <div className="text-center mt-3">
          <button type="submit" className="btn btn-success" disabled={isLoading}>
            {isLoading ? 'Loading...' : 'Submit'}
          </button>
        </div>
        {isLoading ? (
          <div className="text-center mt-3">
            <small>Please wait for results to be loaded</small>
          </div>
        ) : (
          <></>
        )}
      </form>
    </div>
  );
};
