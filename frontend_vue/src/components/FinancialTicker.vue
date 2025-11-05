<template>
  <!-- Financial Ticker Tape Banner - Auto-scrolling financial indicators -->
  <div class="ticker-wrapper">
    <div class="ticker-container">
      <!-- Duplicate content for seamless loop -->
      <div class="ticker-content" ref="tickerContent">
        <!-- First set of data -->
        <div class="ticker-item" v-for="(item, index) in tickerData" :key="`first-${index}`">
          <span class="ticker-label">{{ item.label }}</span>
          <span class="ticker-date">{{ item.date }}</span>
          <span class="ticker-value">{{ item.value }}</span>
          <span class="ticker-change" :class="getChangeClass(item.change)">
            {{ item.change }}
          </span>
        </div>
        
        <!-- Second set of data for seamless loop -->
        <div class="ticker-item" v-for="(item, index) in tickerData" :key="`second-${index}`">
          <span class="ticker-label">{{ item.label }}</span>
          <span class="ticker-date">{{ item.date }}</span>
          <span class="ticker-value">{{ item.value }}</span>
          <span class="ticker-change" :class="getChangeClass(item.change)">
            {{ item.change }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'FinancialTicker',
  
  data() {
    return {
      // Financial indicators data - can be updated via API or props
      tickerData: [
        {
          label: 'SOFR',
          date: 'Nov 3, 2025',
          value: '4.00%',
          change: '-3.15%'
        },
        {
          label: 'Fed Funds',
          date: 'Nov 3, 2025',
          value: '3.87%',
          change: '+0.00%'
        },
        {
          label: '30-Year Mortgage',
          date: 'Oct 29, 2025',
          value: '6.17%',
          change: '-0.32%'
        },
        {
          label: '10-Yr Treasury',
          date: 'Nov 3, 2025',
          value: '4.10%',
          change: '-0.73%'
        },
        {
          label: 'CPI',
          date: 'Aug 31, 2025',
          value: '3.0%',
          change: '+2.84%'
        }
      ]
    }
  },
  
  methods: {
    /**
     * Returns CSS class based on whether change is positive or negative
     * @param {string} change - The change value (e.g., '+2.84%' or '-3.15%')
     * @returns {string} - CSS class name
     */
    getChangeClass(change) {
      if (change.startsWith('+')) {
        return 'positive';
      } else if (change.startsWith('-')) {
        return 'negative';
      }
      return 'neutral';
    }
  }
}
</script>

<style scoped>
/* Ticker wrapper - fixed position banner */
.ticker-wrapper {
  width: 100%;
  background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
  border-bottom: 2px solid rgba(0, 0, 0, 0.1);
  overflow: hidden;
  padding: 0.5rem 0;
  position: relative;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

/* Container for the scrolling content */
.ticker-container {
  width: 100%;
  overflow: hidden;
  white-space: nowrap;
}

/* The actual scrolling content */
.ticker-content {
  display: inline-flex;
  animation: scroll 60s linear infinite;
  gap: 3rem;
}

/* Pause animation on hover */
.ticker-content:hover {
  animation-play-state: paused;
}

/* Individual ticker item */
.ticker-item {
  display: inline-flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.25rem 1rem;
  background: rgba(0, 0, 0, 0.03);
  border-radius: 0.25rem;
  border-left: 3px solid rgba(0, 0, 0, 0.2);
  transition: all 0.3s ease;
}

/* Hover effect on ticker items */
.ticker-item:hover {
  background: rgba(0, 0, 0, 0.06);
  transform: scale(1.05);
  border-left-color: var(--ct-primary);
}

/* Label styling (e.g., "SOFR", "Fed Funds") */
.ticker-label {
  font-weight: 600;
  font-size: 0.875rem;
  color: #1a1d29;
  letter-spacing: 0.5px;
  text-transform: uppercase;
}

/* Date styling */
.ticker-date {
  font-size: 0.75rem;
  color: rgba(0, 0, 0, 0.5);
  font-weight: 400;
}

/* Value styling (e.g., "4.00%") */
.ticker-value {
  font-size: 0.875rem;
  font-weight: 700;
  color: #1a1d29;
  background: rgba(0, 0, 0, 0.08);
  padding: 0.125rem 0.5rem;
  border-radius: 0.25rem;
}

/* Change indicator styling */
.ticker-change {
  font-size: 0.875rem;
  font-weight: 600;
  padding: 0.125rem 0.5rem;
  border-radius: 0.25rem;
}

/* Positive change (green) */
.ticker-change.positive {
  color: #10b981;
  background: rgba(16, 185, 129, 0.1);
}

/* Negative change (red) */
.ticker-change.negative {
  color: #ef4444;
  background: rgba(239, 68, 68, 0.1);
}

/* Neutral change (gray) */
.ticker-change.neutral {
  color: rgba(0, 0, 0, 0.6);
  background: rgba(0, 0, 0, 0.05);
}

/* Scrolling animation - seamless infinite loop */
@keyframes scroll {
  0% {
    transform: translateX(0);
  }
  100% {
    transform: translateX(-50%);
  }
}

/* Responsive adjustments for smaller screens */
@media (max-width: 768px) {
  .ticker-wrapper {
    padding: 0.375rem 0;
  }
  
  .ticker-item {
    gap: 0.5rem;
    padding: 0.25rem 0.75rem;
  }
  
  .ticker-label {
    font-size: 0.75rem;
  }
  
  .ticker-date {
    font-size: 0.625rem;
  }
  
  .ticker-value,
  .ticker-change {
    font-size: 0.75rem;
    padding: 0.125rem 0.375rem;
  }
  
  /* Faster scroll on mobile for better UX */
  .ticker-content {
    animation-duration: 40s;
  }
}

/* Optional: Add a subtle gradient fade at edges */
.ticker-wrapper::before,
.ticker-wrapper::after {
  content: '';
  position: absolute;
  top: 0;
  bottom: 0;
  width: 50px;
  pointer-events: none;
  z-index: 2;
}

.ticker-wrapper::before {
  left: 0;
  background: linear-gradient(to right, #f8f9fa, transparent);
}

.ticker-wrapper::after {
  right: 0;
  background: linear-gradient(to left, #f8f9fa, transparent);
}
</style>

