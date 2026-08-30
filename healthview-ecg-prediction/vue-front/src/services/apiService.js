import axios from "axios";
import { useToast } from "vue-toastification";

// The API runs in a separate container. `localhost` is intentional here: this
// code executes in the user's browser, where the Docker service name is not
// resolvable. Deployments behind a reverse proxy can still set VITE_API_URL.
const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

const apiClient = axios.create({
  baseURL: API_URL,
});

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    const toast = useToast();
    console.error("API Error:", error);
    if (error.response && error.response.data && error.response.data.detail) {
      toast.error(`Error: ${error.response.data.detail}`);
    } else {
      toast.error("A network error occurred. Please try again.");
    }
    return Promise.reject(error);
  }
);

const analyzeECG = (formData) => apiClient.post(`/analyze`, formData).then((response) => response.data);
const getRandomPlot = () => apiClient.get(`/get-random-plot`).then((response) => response.data);
const saveScore = (score) => apiClient.post(`/score?value=${score}`).then((response) => response.data);
const getAverageScore = () => apiClient.get(`/score/stats`).then((response) => response.data);

export { analyzeECG, getRandomPlot, saveScore, getAverageScore };
