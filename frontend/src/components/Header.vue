<template>
  <b-navbar toggleable="lg" type="dark" variant="info">
    <b-navbar-brand href="#">English Test Solver (logo?)</b-navbar-brand>

    <b-nav-form class="ml-auto">
      <b-nav-text class="mr-2">The algorithm: </b-nav-text>
      <b-select size="sm" :options="algorithms" v-model="select_algorithm" class="mr-2" />
      <b-button size="sm" @click="$emit('start')">Start!</b-button>
    </b-nav-form>
  </b-navbar>
</template>

<script>

import {algorithms, default_algorithm} from "@/js/const";

export default {
  name: "Header",
  data: function () {
    return {
      select_algorithm: default_algorithm
    }
  },
  computed: {
    algorithms: () => algorithms
  }
}
</script>

<style scoped>

</style>