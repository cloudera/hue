import axios from 'axios';


export default {
  verifyAuthToken: function(token) {
    return axios.post('/auth/verify-token/', {token: token});
  },
  login: function(credentials) {
    return axios.post('/auth/', credentials);
  },
}
