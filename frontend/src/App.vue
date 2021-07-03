<template>
  <div id="app">
    <Header @start="start" @change_algorithm="($event) => {algorithm = $event; clear_result()}"/>
    <div class="row m-0">
      <div class="col-5 col-xl-2 col-md-4 border-right pt-2 left-menu">
        <WordSelection ref="word_selection" :gaps="gaps" :cache_gaps="cache_gaps"
                       @add_gap="(new_gap) => {$refs.text_editor.add_gap(new_gap)}"
                       @clear_result="clear_result"/>
      </div>
      <div class="col-5 col-xl-10 col-md-8 pt-2">
        <TextEditor ref="text_editor" :gaps="gaps" :cache_gaps="cache_gaps"
                    @add_gap="() => $refs.word_selection.add()"
                    @clear_result="clear_result"/>
      </div>
    </div>
    <transition name="global" mode="out-in" appear>
      <Loading v-if="is_show_loading" :times="300"/>
    </transition>
    <b-modal title="An error occurred" v-model="error.is_show">
      <template v-slot:default>
        <span v-for="(e, index) in error.payload" :key="index" class="text_error">
          {{ e }}
        </span>
      </template>

      <template v-slot:modal-footer="{ok}">
        <div>
          <button class="btn btn-outline-danger" @click="ok">Ok</button>
        </div>
      </template>
    </b-modal>
  </div>
</template>

<script>
import Vue from 'vue'

// Import Bootstrap
import BootstrapVue from 'bootstrap-vue'
import 'bootstrap/dist/css/bootstrap.css'
import 'bootstrap-vue/dist/bootstrap-vue.css'

Vue.use(BootstrapVue);

// Import Icons
import './js/fa.config'

// Import components
import Header from "@/components/Header";
import TextEditor from "@/components/TextEditor";
import WordSelection from "@/components/WordSelection";
import Loading from "@/components/Loading";

// Import axios and notify from const
import {default_algorithm, notify, percent_min_range, send} from "@/js/const";

export default {
  name: 'App',
  components: {
    Loading,
    WordSelection,
    TextEditor,
    Header
  },
  data: function () {
    return {
      algorithm: default_algorithm,
      is_show_loading: false,
      gaps: [],
      cache_gaps: [],
      is_show_result: false,
      error: {
        is_show: false,
        payload: {}
      }
    }
  },
  methods: {
    clear_result: function () {
      if (!this.is_show_result)
        return;
      this.is_show_result = false;
      this.cache_gaps.forEach(g => {
        g.set_text(`GAP ${g.id}`);
        g.candidates.forEach(c => {
          c.is_show_percent = false;
        });
      });
    },
    start: function () {
      let is_invalid_candidate = this.gaps.findIndex(g => g.candidates.findIndex(c => c.is_invalid) !== -1);
      if (is_invalid_candidate !== -1) {
        notify("Please, correct the errors in filling the gaps", 'error');
        return;
      }

      let is_empty_candidate = this.gaps.findIndex(g => g.candidates.length === 0);
      if (is_empty_candidate !== -1) {
        notify("List of candidates shouldn't be empty", 'error');
        return;
      }

      let form_text = this.$refs.text_editor.get_text();
      if (form_text.length === 0) {
        notify("Text field is empty", 'error');
        return;
      } else if (this.gaps.length === 0) {
        notify("There are no gaps in the text", 'error');
        return;
      }
      let query = {
        text_parts: [],
        candidates: []
      };

      let gaps_list = [];

      form_text.forEach(w => {
        if (typeof w === 'string')
          query.text_parts.push(w);
        else {
          query.candidates.push(w.candidates.map(c => c.word));
          gaps_list.push(w);
        }
      });
      if (query.candidates.length === query.text_parts.length)
        query.text_parts.push('');

      this.is_show_loading = true;
      send.post(this.algorithm, query).then((response) => {
        response.data.forEach((candidates, i) => {
          let gap = gaps_list[i];
          let max_candidate = null;
          candidates.forEach((percent, j) => {
            let candidate = gap.candidates[j];
            candidate.percent = Math.round(percent * 100);
            candidate.is_show_percent = true;
            if (!max_candidate || max_candidate.percent < candidate.percent)
              max_candidate = candidate;
          });
          if (max_candidate.percent >= percent_min_range)
            gap.set_text(max_candidate.word);
        })
        notify('Successful!');
        this.is_show_loading = false;
        this.is_show_result = true;
      }).catch(error => {
        this.is_show_loading = false;
        this.clear_result();
        if (error?.response?.status === 400) {
          let recursion_array_resolve = (item) => {
            let result = [];
            if (typeof item == 'object') {
              for (let i in item) {
                let part = recursion_array_resolve(item[i]);
                if (part.length > 0) {
                  if (typeof i == 'string' && Number.parseInt(i) != i)
                    part[0] = i + ": " + part[0];
                  Array.prototype.push.apply(result, part);
                }
              }
            } else {
              result.push(item);
            }
            return result;
          };
          this.error.payload = recursion_array_resolve(error.response.data);
          this.error.is_show = true;
        } else {
          notify("Backend response error", 'error');
        }
      });
    }
  }
}

</script>

<style lang="scss">
@import '~@/../node_modules/noty/lib/noty.css';
@import "~@/../node_modules/noty/lib/themes/metroui.css";

.radius-right-none {
  border-bottom-right-radius: 0;
  border-top-right-radius: 0;
  border-right: none;
}

.radius-left-none {
  border-bottom-left-radius: 0;
  border-top-left-radius: 0;
}

.radius-bottom-none {
  border-bottom-right-radius: 0;
  border-bottom-left-radius: 0;
}

.radius-top-none {
  border-top-left-radius: 0 !important;
  border-top-right-radius: 0 !important;
}

.global-enter-active, .global-leave-active {
  transition: opacity .3s ease;
}

.global-enter, .global-leave-to {
  opacity: 0 !important;
}

/*Animate Groups*/
.items {
  position: relative;
}

.list-item {
  transition: all 1s, color 0.3s, background-color 0.3s;
  display: inline-block;
  width: 100%;
  /*margin-right: 10px;*/
}

.row {
  flex-direction: row;
  display: flex;
}

.list-enter, .list-leave-to
  /* .list-complete-leave-active до версии 2.1.8 */
{
  opacity: 0;
  transform: translateY(30px);
}

.list-enter.list-right {
  transform: translateX(30px);
}

.list-leave-to.list-right {
  transform: translateY(30px);
}

.list-leave-active {
  position: absolute;
  left: 0;
  right: 0;
  z-index: 9999;
}

/*End*/

.animated {
  animation-duration: 0.3s;
}

select {
  cursor: pointer;
}

.left-menu {
  height: calc(100vh - 56px);
  overflow-x: hidden;
  overflow-y: auto;
}

.text_error {
  background-color: #ffc3ca;
  font-size: 1.1em;
  display: inline-block;
  width: 100%;
  padding: 0.2rem;
  margin-top: 0.2rem;
}
</style>
