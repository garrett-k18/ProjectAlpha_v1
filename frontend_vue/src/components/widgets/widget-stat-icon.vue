<template>
  <div class="card widget-flat">
    <div :class="['card-body', dense ? 'py-2 px-3' : '']">
      <div class="float-end">
        <i
          :class="`mdi ${icon} widget-icon `"
          :style="{
            fontSize: iconSizePx + 'px',
            height: iconBoxPx + 'px',
            width: iconBoxPx + 'px',
            lineHeight: iconBoxPx + 'px'
          }"
        ></i>
      </div>
      <h5 :class="['text-muted fw-normal mt-0', titleClass]" :title="`${title}`">{{ title }}</h5>
      <h3 :class="['mt-3', dense ? 'mb-1' : 'mb-3', numberClass]">{{ number }}</h3>
      <p v-if="showFooter" class="mb-0 text-muted">
        <span class="me-2" :class="`text-${color}`">
          <i
              :class=" { 'mdi mdi-arrow-down-bold': `${color}` === 'danger' ,
          'mdi mdi-arrow-up-bold': `${color}` === 'success' }"
          ></i>
          {{ subtext }}
        </span>
        <span class="text-nowrap">Since last month</span>
      </p>
    </div>
  </div>
</template>

<script lang="ts">
/**
 * A simple widget with icon
 * 1. Widget icon name specify using the 'icon' input property
 * 2. Widget title specify the widget data are belongs to title.
 * 3. widget 'number' property specify the value of title such as progress or sales etc., that depends on title.
 * 4. widget trend color specify using the 'color' input property.
 * 5. widget trend specify using the 'subtext' input property. Trend value consider on title.
 */
export default {
  props: {
    icon: {
      type: String,
      default: '',
    },
    iconColor: {
      type: String,
      default: 'primary'
    },
    title: {
      type: String,
      default: '',
    },
    number: {
      type: String,
      default: '',
    },
    color: {
      type: String,
      default: 'success',
    },
    bgColor: {
      type: String,
      default: 'primary'
    },
    subtext: {
      type: String,
      default: '',
    },
    showFooter: {
      type: Boolean,
      default: true,
    },
    dense: {
      type: Boolean,
      default: false,
    },
    // Optional extra classes to tweak typography sizes
    titleClass: {
      type: String,
      default: '',
    },
    numberClass: {
      type: String,
      default: '',
    },
    // Control icon size (text) and its container box (background square)
    iconSizePx: {
      type: Number,
      default: 16,
    },
    iconBoxPx: {
      type: Number,
      default: 28,
    },
  },
}
</script>