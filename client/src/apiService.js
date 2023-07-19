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
  
