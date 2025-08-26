<template>
  <!-- Broker profile card: renders the broker's public details when provided.
       This component is chrome-agnostic and fits inside the broker portal page. -->
  <b-card class="text-center">
    <!-- Avatar rendered as initials (no images). Uses broker name/email; falls back to 'BR'. -->
    <!-- Use built-in size prop to enlarge avatar and Bootstrap fs-2 to scale initials -->
    <b-avatar
      :text="initials"
      variant="primary"
      size="4rem"
      class="img-thumbnail text-white fs-2"
      rounded="circle"
      aria-label="broker-initials-avatar"
    />

    <!-- Name and firm come from the broker object when available. -->
    <h4 class="mb-0 mt-2">{{ broker?.broker_name || 'Broker' }}</h4>
    <p class="text-muted font-14 mb-1">{{ broker?.broker_firm || '—' }}</p>
    <p class="text-muted font-13" v-if="broker?.broker_email">
      <a :href="`mailto:${broker.broker_email}`" class="text-muted">{{ broker.broker_email }}</a>
    </p>

    <!-- Optional action buttons hidden for public portal; leave markup for consistent spacing/style. -->
    <div class="d-none">
      <b-button class="mb-2 me-1" size="sm" variant="success">Follow</b-button>
      <b-button class="mb-2" size="sm" variant="danger">Message</b-button>
    </div>

    <!-- Removed duplicate details section to keep the card compact. -->

    <!-- Social list removed for public portal (no external links needed). Keep structure hidden if desired. -->
    <ul class="social-list list-inline mt-3 mb-0 d-none"></ul>
  </b-card>
</template>

<script lang="ts">
export default {
  props: {
    // Broker object with fields: id, broker_name, broker_email, broker_firm
    // When null (e.g., single-invite tokens without broker context), the UI shows fallbacks.
    broker: { type: Object, default: null },
  },
  computed: {
    // Compute initials to display in the avatar.
    // Rules:
    // - Prefer broker_name (take first letters of first two words)
    // - Else derive from broker_email (first two letters before '@')
    // - Fallback to 'BR' (for Broker)
    initials(): string {
      // Extract from broker_name when available
      const name: string = (this as any).broker?.broker_name || ''
      if (name.trim().length > 0) {
        const parts = name.trim().split(/\s+/).filter(Boolean)
        const first = parts[0]?.charAt(0) || ''
        const second = parts[1]?.charAt(0) || ''
        return `${first}${second}`.toUpperCase() || (first || '').toUpperCase() || 'BR'
      }
      // Else, derive from email when available
      const email: string = (this as any).broker?.broker_email || ''
      if (email.includes('@')) {
        const local = email.split('@')[0]
        const a = local.charAt(0)
        const b = local.charAt(1)
        return `${a}${b}`.toUpperCase() || (a || '').toUpperCase() || 'BR'
      }
      // Final fallback
      return 'BR'
    }
  }
}
</script>
