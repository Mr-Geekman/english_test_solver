<template>
  <b-navbar toggleable="lg" type="dark" variant="info">
    <b-navbar-brand href="#">English Test Solver</b-navbar-brand>

    <b-nav-form class="ml-auto">
      <b-nav-text class="mr-2">The algorithm: </b-nav-text>
      <b-select size="sm" :options="algorithms" v-model="select_algorithm" class="mr-2" />
      <b-button class="pl-5 pr-5 mr-2" @click="$emit('start')">Start!</b-button>
      <b-button class="btn help-btn" variant="info" @click="is_show_help_box = true">
        <icon icon="question"></icon>
      </b-button>
    </b-nav-form>

    <b-modal size="lg" title="Help" v-model="is_show_help_box">
      <template v-slot:default>
        <h1>Manual</h1>
        <p>This manual can help you understand how to use this instrument.</p>
        <h2>Instruction</h2>
        <p>This app helps you to solve the task of choosing one of the given candidates for a gap. It can't guarantee the correct answer.</p>
        <p>You can place a gap in your text field using the button GAP or by pressing CTRL+Enter.</p>
        <h2>Algorithms</h2>
        <p>To the left of the button Start, there is a button to select algorithm for prediction.</p>
        <ol class="pl-3">
          <li>BERT. This algorithm is based on BERT Masked Language Model. You can't use it with candidates consists of many words and blanks.</li>
          <li>GPT-2. This algorithm is based on GPT-2 perplexity scoring. You can use it with bigger candidates and blanks, but it is slower.</li>
        </ol>
      </template>
      <template v-slot:modal-footer="{ok}">
        <button class="btn btn-outline-info" @click="ok">Close</button>
      </template>
    </b-modal>
  </b-navbar>
</template>

<script>

import {algorithms, default_algorithm} from "@/js/const";

export default {
  name: "Header",
  data: function () {
    return {
      select_algorithm: default_algorithm,
      is_show_help_box: false
    }
  },
  watch: {
    select_algorithm: function (val) {
      this.$emit('change_algorithm', val);
    }
  },
  computed: {
    algorithms: () => algorithms
  }
}
</script>

<style scoped lang="scss">
.help-btn {
  padding: 0;
  box-shadow: none;
  font-size: 1.1rem;
  width: 38px;
  height: 38px;
  color: white;
  background-color: #17a2b8;
  border-color: white !important;

  &:hover {
    color: #17a2b8;
    background-color: white;
  }
}
</style>