<template>
  <footer class="footer">
    <!-- Financial Ticker Tape Banner - Moved to footer for less visual clutter -->
    <FinancialTicker />
  </footer>
</template>

<script lang="ts">
// Import financial ticker component for footer display
import FinancialTicker from '@/components/FinancialTicker.vue'

export default {
  // Register FinancialTicker component
  components: {
    FinancialTicker
  },
  data() {
    return {
      year: new Date().getFullYear()
    }
  }
}
</script>
