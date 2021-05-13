<template>
  <div class="loading" :style="{height: height}" v-if="is_show">
    <div class="d-flex flex-column justify-content-center align-items-center">
      <span class="font-weight-bold">Loading...</span>
      <div class="spinner-border text-info" :style="{height: _size, width: _size}" role="status">
        <span class="sr-only">Loading...</span>
      </div>
    </div>
  </div>
</template>

<script>
  export default {
    name: "Loading",
    props: ['height', 'times', 'size'],
    data: function () {
      return {
        is_show: (typeof this.times === 'undefined')
      }
    },
    computed: {
      _size: function () {
        return (this.size) ? this.size : '3rem';
      }
    },
    created: function () {
      if (typeof this.times !== 'undefined') {
        setTimeout(() => {
          this.is_show = true;
        }, Number.parseFloat(this.times));
      }
    }
  }
</script>

<style scoped>
  .loading {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100vh;
    width: 100vw;
    background-color: rgba(180, 180, 180, 0.7);
    position: fixed;
    top: 0;
    left: 0;
  }
</style>