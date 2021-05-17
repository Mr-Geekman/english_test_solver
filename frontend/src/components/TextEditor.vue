<template>
  <div class="text-editor-container">
    <div contenteditable="true" class="input" id="text_editor"
         :class="{transparent: is_input_transparent}" ref="input"
         @input="is_input_transparent = $refs.input.textContent === ''"
         @keydown.exact="$emit('clear_result')"
         @paste.prevent="paste"
         @keydown.ctrl.z="undo"
         @keydown.ctrl.enter.prevent="$emit('add_gap')"
         @keydown.shift.enter.prevent="$emit('add_gap')"
    ></div>
    <div class="placeholder">Type here your text with gaps</div>
  </div>
</template>

<script>
/*eslint-disable*/
const gap = (id, color) => {
  let node = document.createElement("SPAN");
  node.id = `gap_${id}`;
  node.className = 'gap';
  node.contentEditable='false';
  node.textContent = `GAP ${id}`;
  node.style.backgroundColor  = color;
  return node;
};

const fix_space_around_gap = (parent) => {
  let index_append = 0;
  Array.from(parent.childNodes).forEach((node, index) => {
    index += index_append;
    if (node.nodeName === 'DIV') {
      fix_space_around_gap(node);
    } else if (node.nodeName === 'SPAN' && node.className === 'gap') {
      if (index === 0) {
        parent.insertBefore(document.createTextNode('_'), node);
        index += 1;
        index_append += 1;
      }
      let node_after_gap = parent.childNodes[index+1];
      if (!node_after_gap || node_after_gap.nodeName === 'BR' || (node_after_gap.nodeName === 'SPAN' && node_after_gap.className === 'gap')) {
        parent.insertBefore(document.createTextNode('_'), node_after_gap);
        index_append += 1;
      }
    }
  });
};

export default {
  name: "TextEditor",
  props: ['gaps', 'cache_gaps'],
  data: function () {
    return {
      is_input_transparent: true
    }
  },
  methods: {
    get_text: function () {
      let merge_arrays = (arr1, arr2) => {
        Array.prototype.push.apply(arr1[arr1.length-1], arr2[0]);
        if (arr2.length > 1) {
          arr2.splice(0, 1);
          Array.prototype.push.apply(arr1, arr2);
        }
      };

      let recursive_get_text = (node, is_root = false) => {
        let result = [[]];
        Array.from(node.childNodes).forEach((child_node) => {
          if (child_node.nodeName === '#text')
            result[result.length-1].push(child_node.textContent);
          else if (child_node.nodeName === 'DIV' && is_root) {
            result[result.length-1].push("\n");
            merge_arrays(result, recursive_get_text(child_node));
          } else if (child_node.nodeName === "BR") {
            result[result.length-1].push("\n");
          } else if (child_node.nodeName === 'SPAN' && child_node.className === 'gap') {
            let id = Number.parseInt(child_node.id.slice(4));
            let gap = this.gaps.find(g => g.id === id);
            if (!gap) {
              gap = this.cache_gaps.find(g => g.id === id);
              this.gaps.push(gap);
            }
            result.push(gap);
            result.push([]);
          } else {
            merge_arrays(result, recursive_get_text(child_node));
          }
        });
        return result;
      }

      return recursive_get_text(this.$refs.input, true).map(t => Array.isArray(t) ? t.join('') : t);
    },
    undo: function () {
      this.$nextTick(() => {
        setTimeout(() => {
          this.$nextTick(() => {
            this.get_text();
          });
        }, 300);
      });
    },
    paste: function (event) {
      let text = event.clipboardData.getData("text/plain").replace(/\n/g, '<br>');
      document.execCommand("insertHTML", false, text);
    },
    add_gap: function (new_gap) {
      let sel = window.getSelection();
      let node = sel.focusNode;
      let temp_node = node;
      while (temp_node.id !== 'text_editor') {
        if (!temp_node || temp_node.nodeName === 'BODY' || (temp_node.nodeName === 'SPAN' && temp_node.className === 'gap'))
          break;
        temp_node = temp_node.parentElement;
      }
      if (!temp_node || temp_node.nodeName === 'BODY' || (temp_node.nodeName === 'SPAN' && temp_node.className === 'gap'))
        node = this.$refs.input;
      let select_start_offset = sel.anchorOffset;
      let select_end_offset = sel.focusOffset;
      let gap_node = gap(new_gap.id, new_gap.color);
      if (node.nodeName === 'DIV') {
        Array.from(node.childNodes).forEach(n => {
          if (n.nodeName === 'BR')
            n.remove();
        });
        node.appendChild(document.createTextNode('_'));
        let text_node = document.createTextNode('');
        node.appendChild(text_node);
        node = text_node;
      }
      if (node.nodeName === '#text') {
        let parent = node.parentElement;

        // Add space middle GAPs, when paste GAP after GAP.
        let index_child = Array.prototype.indexOf.call(parent.childNodes, node);
        let is_set_space = false;
        if (index_child) {
          let node_before_current = parent.childNodes.item(index_child-1);
          if (node_before_current.nodeName === 'SPAN' && node_before_current.className === 'gap')
            is_set_space = true;
          if (node_before_current.nodeName === 'BR')
            node_before_current.remove();
        }

        parent.insertBefore(gap_node, node);
        let text_before_gap = node.textContent.slice(0, select_start_offset);
        parent.insertBefore(document.createTextNode(text_before_gap), gap_node);
        if (is_set_space && text_before_gap === '')
          parent.insertBefore(document.createTextNode(' '), gap_node);
        node.textContent = node.textContent.slice(select_end_offset);
        if (node.textContent === "") {
          node.textContent = '_';
          let rng = document.createRange();
          rng.setStart(node, 1);
          rng.collapse(true);
          sel.removeAllRanges();
          sel.addRange(rng);
        }
      } else if (node.id === 'text_editor') {

        // let n1 = document.createElement("SPAN");
        // n1.textContent = "_";
        // let n2 = document.createElement("SPAN");
        // n2.textContent = "_";
        // node.appendChild(n1);
        // node.appendChild(gap_node);
        // node.appendChild(n2);

        Array.from(node.childNodes).forEach(n => {
          if (n.nodeName === 'BR')
            n.remove();
        });

        node.appendChild(document.createTextNode('_'));
        node.appendChild(gap_node);
        let dot = document.createTextNode('_');
        node.appendChild(dot);
        let rng = document.createRange();
        rng.setStart(dot, 1);
        rng.collapse(true);
        sel.removeAllRanges();
        sel.addRange(rng);
      } else {
        node.appendChild(gap_node);
      }
      this.$nextTick(() => {
        this.$refs.input.focus();
        new_gap.set_text = (text) => {
          gap_node.textContent = text;
        };
        new_gap.node = gap_node;
      });
      this.$emit('clear_result');
      this.is_input_transparent = false;
    }
  },
  mounted() {
    let remove_recursive = (n, parent_node) => {
      if (n.nodeName === '#text')
        return true;
      if (n.nodeName !== 'SPAN' || n.className !== 'gap')
        return Array.from(n.childNodes).reduce((temp, child_node) => remove_recursive(child_node, parent_node) || temp, false);
      else {
        if (!parent_node.parentElement || Array.prototype.indexOf.call(parent_node.parentElement.childNodes, parent_node) === -1) {
          let id = Number.parseInt(n.id.slice(4));
          let index = this.gaps.findIndex(g => g.id === id);
          if (index !== -1)
            this.gaps[index].remove();
        }
      }
      return false;
    };
    let observer = new MutationObserver((mutations) => {
      this.$nextTick(() => {
        let is_remove_text = false;
        mutations.forEach(mutation => {
          if (mutation.type !== 'childList' || !mutation.removedNodes)
            return;
          Array.from(mutation.removedNodes).forEach(n => {
            if (remove_recursive(n, n))
              is_remove_text = true;
          });
        });
        if (is_remove_text)
          fix_space_around_gap(this.$refs.input);
      });
    });
    observer.observe(this.$refs.input, { attributes: true, childList: true, characterData: false, subtree: true });
  }
}
</script>

<style scoped lang="scss">
.text-editor-container {
  position: relative;
}

.input {
  display: block;
  width: 100%;
  height: auto;
  min-height: 50vh;
  padding: 0.375rem 0.75rem;
  font-size: 1.2em;
  font-weight: 400;
  line-height: 1.5;
  color: #495057;
  background-color: #fff;
  background-clip: padding-box;
  border: 1px solid #ced4da;
  border-radius: 0.25rem;
  transition: border-color 0.15s ease-in-out, box-shadow 0.15s ease-in-out;
  outline: none;
  max-height: calc(100vh - 110px);
  overflow-y: auto;
  background-color: rgba(255, 255, 255, 1);
  z-index: 10;
  position: relative;

  &.transparent {
    background-color: rgba(255, 255, 255, 0.5);
  }
}

.placeholder {
  padding: 0.375rem 0.75rem;
  z-index: 1;
  position: absolute;
  top: 0;
  left: 0;
  font-size: 1.2em;
}

</style>

<style lang="scss">

//span {
//  min-width: 10px;
//  display: inline-block;
//  &:before {
//    content: ":";
//  }
//  &:after {
//    content: ":";
//  }
//}

.gap {
  /*user-select: none;*/
  font-weight: bold;
  border: 1px solid #dee2e6;
  padding: 0 4px;
  //margin: 0 4px;
}

.input > * {
  //margin: 0 10px;
}

.input > div {
  display: inline-block;
  width: 100%;
}
</style>