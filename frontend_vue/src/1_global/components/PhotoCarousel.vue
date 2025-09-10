<template>
  <!--
    PhotoCarousel: A reusable image carousel with optional thumbnail strip.
    - Uses BootstrapVue 3's <b-carousel> (already used elsewhere in this project).
    - Accepts an array of image objects via the "images" prop.
    - Exposes v-model (modelValue) to control the active slide from parent components.
    - Avoids custom JS/CSS and relies on framework utilities, per project guidelines.
  -->
  <div class="d-flex flex-column justify-content-between h-100">
    <!-- Main carousel region -->
    <div class="text-center d-block flex-fill mx-auto" :style="containerStyleObject">
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
        :controls="controlsComputed"
        :indicators="indicatorsComputed"
        :wrap="loop"
        :class="['h-100', bgTransparent ? 'bg-transparent' : '']"
        @sliding-start="$emit('slide', current)"
        @sliding-end="$emit('slid', current)"
      >
        <!-- Render a slide for each image; make slide fill height for stable layout -->
        <b-carousel-slide v-for="(img, idx) in images" :key="idx" :background="slideBackground" class="h-100">
          <template #img>
            <!-- The displayed image for the slide -->
            <img
              :src="img.src"
              :alt="img.alt || `Slide ${idx + 1}`"
              :class="imgClass"
              :style="imgStyleObject"
            />
          </template>
        </b-carousel-slide>
      </b-carousel>
    </div>

    <!-- Optional thumbnail strip below the main carousel (tight spacing) -->
    <div v-if="thumbsVisibleComputed" class="d-flex justify-content-center flex-nowrap overflow-auto mt-auto w-100 pb-0">
      <a
        v-for="(img, idx) in images"
        :key="`thumb-${idx}`"
        href="javascript:void(0);"
        :class="idx > 0 ? 'ms-1' : ''"
        @click.prevent="setCurrent(idx)"
      >
        <img
          :src="img.thumb || img.src"
          class="img-fluid img-thumbnail p-1"
          :style="thumbStyleObject"
          :alt="img.alt || `Thumbnail ${idx + 1}`"
        />
      </a>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, watch, computed, toRefs } from 'vue'
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
      default: true, // show dots by default for easier navigation
    },
    // Show previous/next controls
    controls: {
      type: Boolean,
      default: true, // show prev/next by default
    },
    // Force show controls/indicators regardless of image count (debug/UX tuning)
    forceShowControls: {
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
      // Keep 'img-fluid' by default for typical usage, but allow callers to override
      // it (e.g., provide 'w-100 h-100' for fixed viewport fill without height:auto !important)
      default: 'img-fluid d-block mx-auto',
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
    // When true, render the main image as a centered square (width = height)
    square: {
      type: Boolean,
      default: false,
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
    // Force show thumbnails even when there is only one image (debug/UX tuning)
    forceShowThumbnails: {
      type: Boolean,
      default: false,
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
    // Optional explicit height for the outer carousel container. When set to '100%',
    // and the parent provides a height via flexbox, the main image will fill the
    // available vertical space above the thumbnails.
    containerHeight: {
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
      const style: Record<string, string> = {
        width: width,
      }
      if (height) style.height = height
      return style
    })

    // Compute inline style for main image based on props
    // Using fixed dimensions with object-fit: cover to ensure consistent sizing
    const imgStyleObject = computed(() => {
      const mw = typeof props.imgMaxWidth === 'number' ? `${props.imgMaxWidth}px` : props.imgMaxWidth
      const mh = props.imgMaxHeight
        ? typeof props.imgMaxHeight === 'number'
          ? `${props.imgMaxHeight}px`
          : props.imgMaxHeight
        : undefined
      
      // Use fixed width and height instead of max-width/max-height for consistent dimensions
      const style: Record<string, string> = {
        objectFit: 'cover',       // fill available area and crop as needed
        objectPosition: '50% 50%', // center the image crop
      }
      // If square mode is enabled, prefer a square frame that uses the full height
      // of the carousel viewport and lets width follow via the aspect ratio.
      if (props.square) {
        style.height = mh || '100%'
        style.width = 'auto'
        // aspect-ratio is well supported in modern browsers; keeps the image square
        // while object-fit: cover ensures good cropping.
        // @ts-ignore - TS typings for inline CSS may not include aspectRatio string
        ;(style as any).aspectRatio = '1 / 1'
        return style
      }
      
      // Set fixed dimensions if both width and height are provided
      if (mw && mh) {
        style.width = mw
        style.height = mh
      } else {
        // Fallback to max dimensions if only one is provided
        style.maxWidth = mw
        if (mh) style.maxHeight = mh
      }
      
      return style
    })

    // Compute inline style for the outer carousel container
    // Always fill available column width; optionally constrain via max-width/height if provided
    const containerStyleObject = computed(() => {
      const style: Record<string, string> = { width: '100%' }
      if (props.containerMaxWidth) {
        const mw =
          typeof props.containerMaxWidth === 'number'
            ? `${props.containerMaxWidth}px`
            : props.containerMaxWidth
        style.maxWidth = mw
      }
      if (props.containerHeight) {
        const ch =
          typeof props.containerHeight === 'number' ? `${props.containerHeight}px` : props.containerHeight
        style.height = ch
      }
      return style
    })

    // Method to set the current slide from thumbnail click
    const setCurrent = (idx: number) => {
      current.value = idx
    }

    // Controls/indicators/thumbs visibility (derived from props)
    const controlsComputed = computed(() => !!(props.forceShowControls || props.controls))
    const indicatorsComputed = computed(() => !!(props.forceShowControls || props.indicators))
    const thumbsVisibleComputed = computed(() => {
      const hasMultiple = (props.images?.length || 0) > 1
      return !!((props.showThumbnails && hasMultiple) || props.forceShowThumbnails)
    })

    return {
      current,
      thumbStyleObject,
      imgStyleObject,
      containerStyleObject,
      setCurrent,
      // Expose props explicitly for robust TypeScript template inference
      ...toRefs(props),
      controlsComputed,
      indicatorsComputed,
      thumbsVisibleComputed,
    }
  },
})
</script>

<style scoped>
/* Ensure the carousel's internal containers honor the fixed height */
:deep(.carousel-inner) {
  height: 100%;
}
:deep(.carousel-item) {
  height: 100%;
}
/* Ensure controls/indicators are not clipped and are visible above images */
:deep(.carousel) {
  overflow: visible;
}
:deep(.carousel-control-prev),
:deep(.carousel-control-next),
:deep(.carousel-indicators) {
  z-index: 3;
}
</style>
