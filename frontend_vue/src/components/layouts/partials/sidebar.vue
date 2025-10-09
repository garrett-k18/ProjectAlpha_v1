<template>
  <!-- ========== Left Sidebar Start ========== -->
  <div
      v-click-outside="clickOutSideConfig"
      class="leftside-menu"
      :data-sidebar-size="type"
      :data-leftbar-theme="theme"
      :class="classes"
  >
    <simplebar
        v-if="!isCondensed"
        :settings="settings"
        class="h-100"
    >
      <div
          v-if="includeUser"
          class="leftbar-user"
      >
        <a href="javascript: void(0);">
          <img
              src="@/assets/images/users/avatar-1.jpg"
              alt="user-image"
              height="42"
              class="rounded-circle shadow-sm"
          />
          <span class="leftbar-user-name">Garrett</span>
        </a>
      </div>
      <a
          v-else
          href="/home"
          class="logo text-center"
      >
        <span class="logo-lg">
          <img
              id="side-main-logo"
              src="@/assets/images/logo.svg"
              alt="projectalpha"
              height="62"
          />
        </span>
        <span class="logo-sm">
          <img
              id="side-sm-main-logo"
              src="@/assets/images/logo-sm.png"
              alt="Small logo"
              height="16"
          />
        </span>
      </a>

      <AppMenu mode="vertical"/>

      <div class="help-box text-white text-center">
        <a
            href="javascript: void(0);"
            class="float-right close-btn text-white"
        >
          <i class="mdi mdi-close"></i>
        </a>
        <img
            src="@/assets/images/svg/help-icon.svg"
            height="90"
            alt="Helper Icon Image"
        />
        <h5 class="mt-3">Unlimited Access</h5>
        <p class="mb-3">Upgrade to plan to get access to unlimited reports</p>
        <a
            href="javascript: void(0);"
            class="btn btn-outline-light btn-sm"
        >Upgrade</a>
      </div>
    </simplebar>

    <div v-else>
      <div
          v-if="includeUser"
          class="leftbar-user"
      >
        <a href="javascript: void(0);">
          <img
              src="@/assets/images/users/avatar-1.jpg"
              alt="user-image"
              height="42"
              class="rounded-circle shadow-sm"
          />
          <span class="leftbar-user-name">Garrett</span>
        </a>
      </div>

      <a
          v-else
          href="/home"
          class="logo text-center"
      >
        <span class="logo-lg">
          <img
              id="side-main-logo"
              src="@/assets/images/logo.svg"
              alt="projectalpha"
              height="42"
          />
        </span>
        <span class="logo-sm">
          <img
              id="side-sm-main-logo"
              src="@/assets/images/logo-sm.png"
              alt="Small logo"
              height="16"
          />
        </span>
      </a>

      <AppMenu/>

      <div class="help-box text-white text-center">
        <a
            href="javascript: void(0);"
            class="float-right close-btn text-white"
        >
          <i class="mdi mdi-close"></i>
        </a>
        <img
            src="@/assets/images/svg/help-icon.svg"
            height="90"
            alt="Helper Icon Image"
        />
        <h5 class="mt-3">Unlimited Access</h5>
        <p class="mb-3">Upgrade to plan to get access to unlimited reports</p>
        <a
            href="javascript: void(0);"
            class="btn btn-outline-light btn-sm"
        >Upgrade</a>
      </div>
    </div>
    <!-- Sidebar -left -->
  </div>
  <!-- Left Sidebar End -->
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import simplebar from 'simplebar-vue';
import AppMenu from "@/components/layouts/partials/app-menu.vue";

export default defineComponent({
  name: 'Sidebar',
  components: {
    AppMenu, 
    simplebar
  },
  props: {
    isCondensed: {
      type: Boolean,
      default: false,
    },
    theme: {
      type: String as () => 'default' | 'light' | 'dark',
      required: true,
    },
    type: {
      type: String as () => 'fixed' | 'condensed' | 'scrollable',
      required: true,
    },
    user: {
      type: Object as () => Record<string, any>,
      required: false,
      default: () => ({}),
    },
    includeUser: {
      type: Boolean,
      default: false,
    },
    classes: {
      type: String,
      default: '',
    },
  },
  data() {
    return {
      settings: {
        minScrollbarLength: 60,
      },
      clickOutSideConfig: {
        handler: this.handleMenuClick as (event: Event, el: HTMLElement) => void,
        middleware: this.middleware as (event: Event, el: HTMLElement) => boolean,
        events: ['click'] as string[],
      },
      // Explicitly typed data properties
      type: this.$props.type as 'fixed' | 'condensed' | 'scrollable',
      theme: this.$props.theme as 'default' | 'light' | 'dark',
    };
  },
  watch: {
    theme: function (newVal: string, oldVal: string) {
      if (newVal !== oldVal) {
        this.activateTheme(newVal as any);
      }
    },
    type: function (newVal: string, oldVal: string) {
      if (newVal !== oldVal) {
        this.activateType(newVal as any);
      }
    },
  },
  created: function () {
    this.activateTheme(this.theme);
    this.activateType(this.type);
  },
  methods: {
    handleMenuClick(event: Event, el: HTMLElement): void {
      const parent = this.$parent as any;
      if (parent && typeof parent.hideMenu === 'function') {
        parent.hideMenu();
      }
    },
    middleware(event: Event, el: HTMLElement): boolean {
      return !(event.target as HTMLElement).classList.contains('toggle-menu');
    },
    activateTheme(theme: 'default' | 'light' | 'dark'): void {
      switch (theme) {
        case 'default':
          document.body.removeAttribute('data-leftbar-theme');
          break;
        case 'light':
          document.body.setAttribute('data-leftbar-theme', 'light');
          break;
        case 'dark':
          document.body.setAttribute('data-leftbar-theme', 'dark');
          break;
        default:
          document.body.removeAttribute('data-leftbar-theme');
          break;
      }
    },
    activateType(type: 'fixed' | 'condensed' | 'scrollable'): void {
      switch (type) {
        case 'fixed':
          document.body.removeAttribute('data-leftbar-compact-mode');
          break;
        case 'condensed':
          document.body.setAttribute('data-leftbar-compact-mode', 'condensed');
          document.body.classList.remove('left-side-menu-dark');
          document.body.classList.remove('boxed-layout');
          break;
        case 'scrollable':
          document.body.setAttribute('data-leftbar-compact-mode', 'scrollable');
          break;
        default:
          document.body.removeAttribute('data-leftbar-compact-mode');
          break;
      }
    },
  },
});
</script>