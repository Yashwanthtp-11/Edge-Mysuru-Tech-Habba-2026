import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 20000,
});

export const getHealth = async () => {
  const response = await api.get('/health');
  return response.data;
};

export const predictRainfall = async (latitude, longitude) => {
  const response = await api.post('/predict', { latitude, longitude });
  return response.data;
};

export const getExplanation = async (latitude, longitude) => {
  const response = await api.get('/predict/explanation', {
    params: { latitude, longitude }
  });
  return response.data;
};

export const geocodeLocation = async (cityName) => {
  try {
    const response = await axios.get('https://geocoding-api.open-meteo.com/v1/search', {
      params: { name: cityName, count: 5, language: 'en', format: 'json' }
    });
    return response.data.results || [];
  } catch (error) {
    console.error('Geocoding error:', error);
    return [];
  }
};
