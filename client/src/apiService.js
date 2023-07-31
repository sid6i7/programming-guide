/**
 * Submits a form with a question and selected tags to the backend API for recommendations.
 *
 * @param {string} question - The user's question to be submitted for recommendations.
 * @param {Array} selectedTags - An array of selected tags associated with the question.
 * @param {number} nOfRecommendations - The number of recommendations to be returned.
 * @returns {Promise<Object>} - A promise that resolves to the response body containing the recommendations.
 * @throws {Error} - If an error occurs during the API call.
 */
const submitForm = async (question, selectedTags, nOfRecommendations) => {
    const recommendEndpoint = process.env.REACT_APP_RECOMMEND_ENDPOINT;
    const apiUrl = process.env.REACT_APP_API_URL;
    console.log(`${apiUrl}${recommendEndpoint}`)
    try {
      const response = await fetch(`${apiUrl}${recommendEndpoint}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          question: question,
          tags: selectedTags,
          n: nOfRecommendations
        })
      });
      const responseBody = await response.json()
      console.log(responseBody)
      return responseBody;
    } catch (error) {
        console.log(`some error occured: ${error}`)
    }
  };
  
  export default submitForm;
  
