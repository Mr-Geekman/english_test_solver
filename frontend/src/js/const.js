// Import Notify
import Noty from "@/../node_modules/noty/lib/noty.js"

export const notify = function (text, type = 'success') {
  new Noty({
    theme: 'metroui',
    text: '<b style="font-size: 1.2rem;">' + text + '</b>',
    type: type,
    timeout: 2000
  }).show();
};

// Import Axios
import axios from 'axios';

export const send = axios.create({
  baseURL: 'http://localhost:8000/api/choose_word/'
});

export const algorithms = [
  {value: 'bert/', text: 'BERT'},
  {value: 'other/', text: 'Other'}
];
export const percent_min_range = 85;

export const default_algorithm = 'bert/';
