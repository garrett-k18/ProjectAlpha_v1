<template>
  <slot/>
</template>

<script lang="ts">
export default {
  props: {bodyClass: String},
  mounted() {
    let classes = this.bodyClass?.split(" ")
    if (this.bodyClass) {
      for (let i in classes) {
        document.body.classList.add(classes[i])
      }
    }
  },
  unmounted() {
    let classes = this.bodyClass?.split(" ")
    if (this.bodyClass) {
      for (let i in classes) {
        document.body.classList.remove(classes[i])
      }
    }
  }
}
</script>


