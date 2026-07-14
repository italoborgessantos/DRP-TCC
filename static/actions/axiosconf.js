const api = axios.create({
  baseURL: window.API_URL, // ou sua URL da AWS
  timeout: 5000,
  headers: {
    "Content-Type": "application/json",
  },
});
console.log("API_URL:", window.API_URL);
export default api;