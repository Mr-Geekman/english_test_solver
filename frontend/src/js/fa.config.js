import Vue from 'vue';
import {FontAwesomeIcon} from '@fortawesome/vue-fontawesome'
import {library} from '@fortawesome/fontawesome-svg-core'
import {
  faPlus,
  faTrash,
  faMinus
} from '@fortawesome/fontawesome-free-solid'

library.add(
  faPlus,
  faTrash,
  faMinus
);

Vue.component('icon', FontAwesomeIcon); // registered globally