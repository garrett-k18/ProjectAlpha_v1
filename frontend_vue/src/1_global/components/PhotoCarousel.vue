<template>
  <!--
    PhotoCarousel: A reusable image carousel with optional thumbnail strip.
    - Uses BootstrapVue 3's <b-carousel> (already used elsewhere in this project).
    - Accepts an array of image objects via the "images" prop.
    - Exposes v-model (modelValue) to control the active slide from parent components.
    - Avoids custom JS/CSS and relies on framework utilities, per project guidelines.
  -->
  <div>
    <!-- Main carousel region -->
    <div class="text-center d-block mb-3 mx-auto" :style="containerStyleObject">
      <!--
        b-carousel props:
        - v-model binds the active slide index (number)
        - interval=0 means manual; set >0 for auto-advance
        - controls/indicators show navigation UI
        - wrap enables looping
      -->
      <b-carousel
        v-model="current"
        :interval="interval"
        :controls="controls"
        :indicators="indicators"
        :wrap="loop"
        :class="bgTransparent ? 'bg-transparent' : ''"
        @sliding-start="$emit('slide', current)"
        @sliding-end="$emit('slid', current)"
      >
        <!-- Render a slide for each image; set background via built-in prop to override default gray -->
        <b-carousel-slide v-for="(img, idx) in images" :key="idx" :background="slideBackground">
          <template #img>
            <!-- The displayed image for the slide -->
            <img
              :src="img.src"
              :alt="img.alt || `Slide ${idx + 1}`"
              :class="`img-fluid ${imgClass}`"
              :style="imgStyleObject"
            />
          </template>
        </b-carousel-slide>
      </b-carousel>
    </div>

    <!-- Optional thumbnail strip below the main carousel (hidden on < lg by design) -->
    <div v-if="showThumbnails && images.length > 1" class="d-lg-flex d-none justify-content-center">
      <a
        v-for="(img, idx) in images"
        :key="`thumb-${idx}`"
        href="javascript:void(0);"
        :class="idx > 0 ? 'ms-2' : ''"
        @click.prevent="setCurrent(idx)"
      >
        <img
          :src="img.thumb || img.src"
          class="img-fluid img-thumbnail p-2"
          :style="thumbStyleObject"
          :alt="img.alt || `Thumbnail ${idx + 1}`"
        />
      </a>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, watch, computed } from 'vue'
import type { PropType } from 'vue'

// Type for a single image item accepted by this component
export type PhotoItem = {
  // Full-size image URL shown in the main carousel
  src: string
  // Optional alt text for accessibility
  alt?: string
  // Optional thumbnail URL; falls back to src if not provided
  thumb?: string
}

export default defineComponent({
  name: 'PhotoCarousel',
  props: {
    // List of images to display in the carousel
    images: {
      type: Array as PropType<PhotoItem[]>,
      default: () => [],
    },
    // Auto-slide interval in ms. Use 0 for manual.
    interval: {
      type: Number,
      default: 0,
    },
    // Show dot indicators below the carousel
    indicators: {
      type: Boolean,
      default: false,
    },
    // Show previous/next controls
    controls: {
      type: Boolean,
      default: false,
    },
    // Loop when reaching first/last slide
    loop: {
      type: Boolean,
      default: true,
    },
    // Extra classes for the main <img> element inside each slide
    imgClass: {
      type: String,
      default: 'd-block mx-auto',
    },
    // Constrain main image max width/height (numbers are treated as px)
    imgMaxWidth: {
      type: [String, Number] as PropType<string | number>,
      default: 280,
    },
    imgMaxHeight: {
      type: [String, Number] as PropType<string | number>,
      default: undefined,
    },
    // Thumbnail sizing (applied as max-width/height inline style)
    thumbWidth: {
      type: [String, Number] as PropType<string | number>,
      default: 75,
    },
    thumbHeight: {
      type: [String, Number] as PropType<string | number>,
      default: undefined,
    },
    // Whether to render the thumbnail strip
    showThumbnails: {
      type: Boolean,
      default: true,
    },
    // Make carousel container background transparent (helps with large images)
    bgTransparent: {
      type: Boolean,
      default: true,
    },
    // Optionally constrain the outer carousel container's max width
    containerMaxWidth: {
      type: [String, Number] as PropType<string | number>,
      default: undefined,
    },
    // Background color for each slide (applied via inline style on b-carousel-slide)
    // Defaults to white to replace the gray demo background
    slideBackground: {
      type: String,
      default: '#fff',
    },
    // v-model for external active slide control
    modelValue: {
      type: Number,
      default: 0,
    },
  },
  emits: ['update:modelValue', 'slide', 'slid'],
  setup(props, { emit }) {
    // Current active slide index for the carousel
    const current = ref<number>(props.modelValue)

    // Keep internal state in sync with external v-model
    watch(
      () => props.modelValue,
      (v) => {
        current.value = v
      }
    )

    // Emit updates when user changes the slide
    watch(current, (v) => emit('update:modelValue', v))

    // Compute inline style for thumbnails based on props
    const thumbStyleObject = computed(() => {
      const width = typeof props.thumbWidth === 'number' ? `${props.thumbWidth}px` : props.thumbWidth
      const height = props.thumbHeight
        ? typeof props.thumbHeight === 'number'
          ? `${props.thumbHeight}px`
          : props.thumbHeight
        : undefined
      return {
        maxWidth: width,
        ...(height ? { maxHeight: height } : {}),
      } as Record<string, string>
    })

    // Compute inline style for main image based on props
    const imgStyleObject = computed(() => {
      const mw = typeof props.imgMaxWidth === 'number' ? `${props.imgMaxWidth}px` : props.imgMaxWidth
      const mh = props.imgMaxHeight
        ? typeof props.imgMaxHeight === 'number'
          ? `${props.imgMaxHeight}px`
          : props.imgMaxHeight
        : undefined
      return {
        maxWidth: mw,
        ...(mh ? { maxHeight: mh } : {}),
        objectFit: 'contain',
      } as Record<string, string>
    })

    // Compute inline style for the outer carousel container
    // Always fill available column width; optionally constrain via max-width if provided
    const containerStyleObject = computed(() => {
      const style: Record<string, string> = { width: '100%' }
      if (props.containerMaxWidth) {
        const mw =
          typeof props.containerMaxWidth === 'number'
            ? `${props.containerMaxWidth}px`
            : props.containerMaxWidth
        style.maxWidth = mw
      }
      return style
    })

    // Method to set the current slide from thumbnail click
    const setCurrent = (idx: number) => {
      current.value = idx
    }

    return {
      current,
      thumbStyleObject,
      imgStyleObject,
      containerStyleObject,
      setCurrent,
    }
  },
})
</script>

<style scoped>
/* No custom CSS beyond utility classes; using Bootstrap/Hyper utilities. */
</style>
