import axios from "axios";
import { getEnvVar } from "../utils/env";


export const api = axios.create({
    baseURL: getEnvVar('VITE_API_BASE_URL'),
    timeout: 1000, //ms
    headers: {}
});


export default api;