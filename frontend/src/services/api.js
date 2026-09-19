import axios from 'axios';

const API_BASE_URL = '/api';

export const uploadSonarImage = async (formData) => {
  const response = await axios.post(`${API_BASE_URL}/upload`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });
  return response.data;
};

export const runDetection = async (imageId) => {
  const response = await axios.post(`${API_BASE_URL}/detect?image_id=${imageId}`);
  return response.data;
};

export const fetchAllDetections = async () => {
  const response = await axios.get(`${API_BASE_URL}/detections`);
  return response.data;
};

export const fetchAnalytics = async () => {
  const response = await axios.get(`${API_BASE_URL}/analytics`);
  return response.data;
};

export const seedDemoData = async () => {
  const response = await axios.post(`${API_BASE_URL}/demo/seed`);
  return response.data;
};

export const getJsonReportUrl = () => `${API_BASE_URL}/report/json`;
export const getCsvReportUrl = () => `${API_BASE_URL}/report/csv`;
