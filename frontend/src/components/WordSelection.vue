<template>
  <div>
    <transition-group name="list" class="d-flex items flex-column">
      <div v-for="gap in gaps" :key="gap.id" class="d-flex list-item mb-2" :style="{'background-color': gap.color}">
        <transition-group name="list" tag="ul" class="list-group w-100 items">
          <li class="list-group-item d-flex justify-content-between list-item" :key="-1">
            <span class="font-weight-bold">GAP {{ gap.id }}</span>
            <button class="btn btn-outline-danger" @click="remove_gap(gap)">
              <icon icon="trash"></icon>
            </button>
          </li>
          <transition-group name="list" tag="li"
                            class="list-group-item d-flex justify-content-center align-items-center list-item list-right"
                            :class="{'is-show-percent': candidate.is_show_percent}"
                            v-for="candidate in gap.candidates" :key="candidate.id">
            <div class="list-item percent-indicator" :key="0"
                 :style="{'background-color': gradient(candidate.percent)}">
              <span>{{ candidate.percent }}%</span>
            </div>
            <input class="form-control radius-right-none list-item" style="transition: all 0.3s ease"
                   :class="{'is-invalid': candidate.is_invalid}" v-model="candidate.word" placeholder="Candidate"
                   @change="edit_candidate(candidate, gap)" :key="1">
            <button class="btn btn-outline-danger radius-left-none" @click="remove_candidate(gap, candidate)" :key="2">
              <icon icon="minus"></icon>
            </button>
          </transition-group>
          <li class="list-group-item d-flex list-item" :key="-2">
            <input class="form-control radius-right-none" :class="{'is-invalid': gap.temp_candidate_invalid}"
                   v-model="gap.temp_candidate"
                   @keydown.enter="add_candidate(gap)"
                   @input="gap.temp_candidate_invalid = false"
                   @click="gap.temp_candidate_invalid = false"
                   placeholder="New candidate">
            <button class="btn btn-outline-success radius-left-none"
                    :class="{'btn-outline-danger': gap.temp_candidate_invalid}"
                    @click="add_candidate(gap)">
              <icon icon="plus"></icon>
            </button>
          </li>
        </transition-group>
      </div>
      <button class="btn btn-outline-success list-item" :key="-1" @click="add">
        <icon icon="plus"></icon>
        <span class="ml-2">GAP</span>
      </button>
    </transition-group>
  </div>
</template>

<script>
import {notify} from "@/js/const";

const getRandom = (min, max) => Number.parseInt(Math.random() * (max - min) + min);

const validate_word = (word, gap, ignore_id = -1) => {
  if (word === '') {
    notify('You shouldn\'t use empty candidate in this algorithm. Try to change it.', 'error');
    return true;
  }
  let word_lower = word.toLowerCase();
  if (gap.candidates.findIndex(c => c.word.toLowerCase() === word_lower && c.id !== ignore_id) !== -1) {
    notify('You shouldn\'t repeat candidates.', 'error');
    return true;
  }

  if (word.split(' ').length > 3) {
    console.log(word.split(' '));
    notify('You shouldn\'t use candidate consists of more that 3 words in this algorithm, try to change the algorithm.', 'error');
    return true;
  }
  return false;
};

export default {
  name: "WordSelection",
  props: ['gaps', 'cache_gaps'],
  data: function () {
    return {
      local_gap_ids: 0
    }
  },
  methods: {
    gradient: function (t) {
      let max = 100;

      let fromR = 200;
      let fromG = 0;
      let fromB = 0;

      let toR = 100;
      let toG = 150;
      let toB = 0;

      let deltaR = Math.round((toR - fromR) / max);
      let deltaG = Math.round((toG - fromG) / max);
      let deltaB = Math.round((toB - fromB) / max);

      let R = fromR + t * deltaR;
      let G = fromG + t * deltaG;
      let B = fromB + t * deltaB;
      return `rgb(${R}, ${G}, ${B})`;
    },
    add: function () {
      let id = ++this.local_gap_ids
      let new_gap = {
        id: id,
        candidates: [],
        temp_candidate: "",
        temp_candidate_invalid: false,
        temp_candidate_id: 0,
        remove: () => {
          let index = this.gaps.findIndex(g => g.id === id);
          if (index !== -1)
            this.gaps.splice(index, 1);
        },
        color: `rgb(${getRandom(180, 255)}, ${getRandom(200, 255)}, ${getRandom(200, 255)})`
      };
      this.gaps.push(new_gap);
      this.cache_gaps.push(new_gap);
      this.$emit('add_gap', new_gap);
      this.$emit('clear_result');
    },
    add_candidate: function (gap) {
      if (validate_word(gap.temp_candidate, gap)) {
        gap.temp_candidate_invalid = true;
        return;
      }
      gap.candidates.push({
        id: ++gap.temp_candidate_id,
        word: gap.temp_candidate,
        is_invalid: false,
        is_show_percent: false,
        percent: null
      });
      gap.temp_candidate = '';
      this.$emit('clear_result');
    },
    remove_candidate: function (gap, candidate) {
      let index = gap.candidates.findIndex(c => c.id === candidate.id);
      if (index !== -1)
        gap.candidates.splice(index, 1);
      this.$emit('clear_result');
    },
    edit_candidate: function (candidate, gap) {
      candidate.is_invalid = validate_word(candidate.word, gap, candidate.id);
      this.$emit('clear_result');
    },
    remove_gap: function (gap) {
      gap.node.parentElement.removeChild(gap.node);
      gap.remove();
      gap.node.remove();
      this.$emit('clear_result');
    }
  }
}
</script>

<style scoped lang="scss">
ul, li {
  background: inherit;
}

li {
  padding: 0.2rem 0.5rem;
}

.percent-indicator {
  color: rgb(240, 240, 250);
  height: 100%;
  border-top-left-radius: 0.25rem;
  border-bottom-left-radius: 0.25rem;
  display: flex;
  justify-content: center;
  align-items: center;
  width: 0;
}

li.is-show-percent {
  input {
    border-top-left-radius: 0;
    border-bottom-left-radius: 0;
  }

  .percent-indicator {
    border: 1px solid #ced4da;
    border-right: none;
    width: 8rem;
  }
}
</style>