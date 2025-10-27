<template>
  <div class="leftside-menu">

    <!-- Brand Logo Light -->
    <router-link to="/home" class="logo logo-light">
        <span class="logo-lg">
            <img src="@/assets/images/logo.svg" alt="projectalpha" height="93">
        </span>
      <span class="logo-sm">
            <img src="@/assets/images/logo-sm.png" alt="small logo">
        </span>
    </router-link>

    <!-- Brand Logo Dark -->
    <router-link to="/home" class="logo logo-dark">
        <span class="logo-lg">
            <img src="@/assets/images/logo.svg" alt="projectalpha" height="93">
        </span>
      <span class="logo-sm">
            <img src="@/assets/images/logo-dark-sm.png" alt="small logo">
        </span>
    </router-link>

    <!-- Sidebar Hover Menu Toggle Button -->
    <div class="button-sm-hover" data-bs-toggle="tooltip" data-bs-placement="right" title="Show Full Sidebar">
      <i class="ri-checkbox-blank-circle-line align-middle"></i>
    </div>

    <!-- Full Sidebar Menu Close Button -->
    <div class="button-close-fullsidebar">
      <i class="ri-close-fill align-middle"></i>
    </div>

    <!-- Sidebar -left -->
    <simplebar class="h-100" id="leftside-menu-container">
      <!-- Leftbar User -->
      <div class="leftbar-user">
        <router-link to="/pages/profile">
          <img src="@/assets/images/users/avatar-1.jpg" alt="user-image" height="42" class="rounded-circle shadow-sm">
          <span class="leftbar-user-name">Garrett</span>
        </router-link>
      </div>

      <!--- Sidemenu -->
      <ul class="side-nav">

        <li class="side-nav-item menuitem-active">
          <router-link to="/home" class="side-nav-link side-nav-link-ref">
            <i class="uil-home-alt"></i>
            <span>{{ dashboardLabel }}</span>
          </router-link>
        </li>

        <li class="side-nav-title">Dashboards</li>

        <li class="side-nav-item">
          <router-link to="/acquisitions" class="side-nav-link side-nav-link-ref">
            <i class="uil-analysis"></i>
            <span> Acquisitions </span>
          </router-link>
        </li>

        <li class="side-nav-item">
          <router-link to="/asset-mgmt" class="side-nav-link side-nav-link-ref">
            <i class="uil-analytics"></i>
            <span> Asset Management </span>
          </router-link>
        </li>

        <li class="side-nav-item">
          <router-link to="/portfolio-mgmt" class="side-nav-link side-nav-link-ref">
            <i class="uil-briefcase-alt"></i>
            <span> Portfolio Management </span>
          </router-link>
        </li>

        <li class="side-nav-item">
          <router-link to="javascript:void(0)" class="side-nav-link side-nav-link-ref">
            <i class="uil-chart-line"></i>
            <span> Reporting </span>
          </router-link>
        </li>

        <li class="side-nav-title">Apps</li>

        <li class="side-nav-item">
          <router-link to="/apps/calendar" class="side-nav-link side-nav-link-ref">
            <i class="uil-calender"></i>
            <span> Calendar </span>
          </router-link>
        </li>

        <li class="side-nav-item">
          <router-link to="/apps/file-manager" class="side-nav-link side-nav-link-ref">
            <i class="uil-folder-plus"></i>
            <span> Documents </span>
          </router-link>
        </li>

        <li class="side-nav-item">
          <router-link to="/apps/crm" class="side-nav-link side-nav-link-ref">
            <i class="uil-tachometer-fast"></i>
            <span> CRMs </span>
          </router-link>
        </li>

        <li class="side-nav-item" role="button">
          <a v-b-toggle.sidebarProjects class="side-nav-link">
            <i class="uil-briefcase"></i>
            <span> Projects </span>
            <span class="menu-arrow"></span>
          </a>
          <b-collapse id="sidebarProjects">
            <ul class="side-nav-second-level">
              <li>
                <router-link to="/apps/projects/list" class="side-nav-link-ref">List</router-link>
              </li>
              <li>
                <router-link to="/apps/projects/details" class="side-nav-link-ref">Details</router-link>
              </li>
              <li>
                <router-link to="/apps/projects/gantt" class="side-nav-link-ref">Gantt
                  <b-badge pill class="text-dark font-10 float-end" variant="light">New</b-badge>
                </router-link>
              </li>
              <li>
                <router-link to="/apps/projects/create" class="side-nav-link-ref">Create Project</router-link>
              </li>
            </ul>
          </b-collapse>
        </li>

        <li class="side-nav-title">Admin</li>

        <li class="side-nav-item">
          <router-link to="/assumptions" class="side-nav-link side-nav-link-ref">
            <i class="uil-cog"></i>
            <span> Assumptions </span>
          </router-link>
        </li>

      </ul>
      <!--      <AppMenu/>-->
      <div class="clearfix"></div>
    </simplebar>
  </div>
</template>

<script lang="ts">
import simplebar from "simplebar-vue"
import {useAuthStore} from "@/stores/auth"

export default {
  components: {simplebar},
  computed: {
    /**
     * Returns the personalized dashboard label by combining the current
     * authenticated user's first name (when available) with the Dashboard
     * suffix. Falls back to a generic "Dashboard" label when no user data is
     * present, ensuring the sidebar title always renders meaningful text.
     */
    dashboardLabel(): string {
      const authStore = useAuthStore()
      const user = authStore.user as {first_name?: string; name?: string} | null

      if (!user) {
        return "Dashboard"
      }

      const firstNameFromField = user.first_name?.trim()
      if (firstNameFromField) {
        return `${firstNameFromField} Dashboard`
      }

      const derivedFirstName = user.name?.split(" ")[0]?.trim()
      if (derivedFirstName) {
        return `${derivedFirstName} Dashboard`
      }

      return "Dashboard"
    },
  },
  
  /**
   * PROBLEM: CRM pages (and all app pages) wrap their content in <Layout>, which includes
   * this sidebar component. When navigating between CRM pages (e.g., Brokers → Trading Partners),
   * Vue destroys the old page's Layout and creates a new one, causing the sidebar to:
   * 1. Unmount (destroy) completely
   * 2. Remount (recreate) from scratch
   * 3. Reset scroll position to top (default behavior)
   * 
   * WHY THIS HAPPENS:
   * - Each route component (Brokers, Trading Partners, etc.) imports and renders <Layout>
   * - Vue treats each navigation as a new component instance
   * - Component data() resets on every mount, so we can't store scroll position there
   * 
   * SOLUTION: sessionStorage
   * - sessionStorage is browser storage that persists across component remounts
   * - It survives component destruction but clears when the browser tab closes
   * - We save scroll position before unmount and restore it after mount
   * 
   * HOW IT WORKS:
   * 1. beforeUnmount(): Captures current scroll position and saves to sessionStorage
   * 2. mounted(): Reads saved position from sessionStorage and restores it
   * 3. $nextTick(): Ensures DOM is fully rendered before setting scroll position
   */
  
  beforeUnmount() {
    // Save scroll position to sessionStorage before sidebar unmounts
    // This runs when navigating away from current page
    const scrollContainer = document.querySelector('#leftside-menu-container .simplebar-content-wrapper')
    if (scrollContainer) {
      // Always save position - we'll check on mount whether to restore it
      sessionStorage.setItem('sidebar-scroll-position', scrollContainer.scrollTop.toString())
    }
  },
  
  mounted() {
    this.activateMenuItems()
    this.initSidenav()
    
    // Restore scroll position after sidebar remounts
    // Only restore if we're on a CRM page, otherwise clear it to free memory
    this.$nextTick(() => {
      const currentPath = window.location.pathname
      const scrollContainer = document.querySelector('#leftside-menu-container .simplebar-content-wrapper')
      const savedPosition = sessionStorage.getItem('sidebar-scroll-position')
      
      if (currentPath.startsWith('/apps/crm/')) {
        // We're on a CRM page - restore scroll position
        if (scrollContainer && savedPosition) {
          scrollContainer.scrollTop = parseInt(savedPosition, 10)
        }
      } else {
        // We're NOT on a CRM page - clear the saved position to free memory
        sessionStorage.removeItem('sidebar-scroll-position')
      }
    })
  },
  methods: {
    /**
     * Activates the appropriate menu items based on the current URL path.
     * This function applies 'active' and related classes to menu items and their parent
     * elements to visually indicate the current page in the navigation.
     * 
     * The function performs the following steps:
     * 1. Gets all navigation links with class 'side-nav-link-ref'
     * 2. Finds the link matching the current URL pathname
     * 3. Applies appropriate classes to the matched link and its parent elements
     */
    activateMenuItems() {
      // Get all side navigation links
      const links = document.getElementsByClassName('side-nav-link-ref')

      // Variable to store the matched menu item element
      let menuItemEl = null
      
      // Iterate through all links to find the one matching current URL path
      for (let i = 0; i < links.length; i++) {
        // Type-safe check for the pathname property using explicit type guard
        if (links[i] instanceof HTMLAnchorElement) {
          // Now TypeScript recognizes this is an HTMLAnchorElement with pathname property
          const anchorElement = links[i] as HTMLAnchorElement;
          const linkPath = anchorElement.pathname;
          
          // If this link's path matches the current window location
          if (window.location.pathname === linkPath) {
            menuItemEl = links[i];
            break; // Exit loop once match is found
          }
        }
      }


      if (menuItemEl) {
        // Always add active class to the selected menu item
        menuItemEl.classList.add('active')
        
        // Get parent element with null check
        const parentEl = menuItemEl.parentElement
        if (!parentEl) return // Exit if no parent element
        
        // Level 0 - Add active class to direct parent
        parentEl.classList.add('menuitem-active')
        
        // Get parent's parent element
        const p1 = parentEl.parentElement
        if (!p1) return // Exit if no parent's parent
        
        // Get next level parent
        const p2 = p1.parentElement
        if (!p2) return // Exit if no further parent
        
        // Get next level parent
        const p3 = p2.parentElement
        if (!p3) return // Exit if no further parent
        
        // Check for deep nesting (level 2)
        const p4 = p3.parentElement
        if (p4) {
          const p5 = p4.parentElement
          if (p5) {
            const p6 = p5.parentElement
            if (p6) {
              // Level 2 nested - handle deep nesting
              p6.classList.add('menuitem-active') // Level 6
              p3.classList.add('menuitem-active') // Level 3
              
              // Only access children if they exist
              if (p3.children && p3.children.length > 0) {
                p3.children[0].classList.add('active')
              }
              
              // Add show class to relevant parents
              p5.classList.add('show') // Level 5
              p2.classList.add('show') // Level 2
            } else {
              // Level 1 nested - simpler nesting
              p3.classList.add('menuitem-active') // Level 3
              p2.classList.add('show') // Level 2
            }
          } else {
            // Fallback for level 1 nested
            p3.classList.add('menuitem-active') // Level 3
            p2.classList.add('show') // Level 2
          }
        } else {
          // Minimal nesting - handle as level 1
          if (p2 && p3) {
            p3.classList.add('menuitem-active') // Level 3
            p2.classList.add('show') // Level 2
          }
        }
      }
    },

    initSidenav() {

      setTimeout(function () {
        // Get the activated menu item with specific HTMLElement type
        let activatedItem = document.querySelector<HTMLElement>('.side-nav-link-ref.active');
        if (activatedItem != null) {
          // Get the scrollable container with specific HTMLElement type
          let simplebarContent = document.querySelector<HTMLElement>('.leftside-menu .simplebar-content-wrapper');
          let offset = activatedItem.offsetTop - 300;
          if (simplebarContent && offset > 100) {
            // Now simplebarContent is properly typed as HTMLElement
            scrollTo(simplebarContent, offset, 600);
          }
        }
      }, 200);

      // scrollTo (Sidenav Active Menu)
      /**
       * Easing function for smooth scrolling animation using quadratic easing in/out
       * @param t - Current time
       * @param b - Start value
       * @param c - Change in value
       * @param d - Duration
       * @returns Calculated easing value
       */
      function easeInOutQuad(t: number, b: number, c: number, d: number): number {
        t /= d / 2;
        if (t < 1) return c / 2 * t * t + b;
        t--;
        return -c / 2 * (t * (t - 2) - 1) + b;
      }

      /**
       * Smoothly scrolls an element to a specified position
       * @param element - The DOM element to scroll
       * @param to - Target scroll position
       * @param duration - Animation duration in milliseconds
       */
      function scrollTo(element: HTMLElement, to: number, duration: number): void {
        let start = element.scrollTop, 
            change = to - start, 
            currentTime = 0, 
            increment = 20;
            
        /**
         * Animation step function
         * Recursively calls itself until animation duration is complete
         */
        const animateScroll = function(): void {
          currentTime += increment;
          let val = easeInOutQuad(currentTime, start, change, duration);
          element.scrollTop = val;
          if (currentTime < duration) {
            setTimeout(animateScroll, increment);
          }
        };
        
        // Start the animation
        animateScroll();
      }
    },
  }
}
</script>
