<template>
  <div class="topnav">
    <div class="container-fluid">
      <nav class="navbar navbar-expand-lg">
        <div class="collapse navbar-collapse" id="topnav-menu-content">
          <ul class="navbar-nav">

            <b-dropdown as="li" class="nav-item" toggle-class="nav-link dropdown-toggle arrow-none"
                        menu-class="dropdown-menu" variant="light">
              <template #button-content>
                <i class="uil-dashboard"></i>Dashboards
                <div class="arrow-down"></div>
              </template>
              <template #default>
                <router-link to="/acquisitions" class="dropdown-item side-nav-link-ref">Acquisitions</router-link>
                <router-link to="/asset-mgmt" class="dropdown-item side-nav-link-ref">Asset Mgmt</router-link>
                <router-link to="/projects" class="dropdown-item side-nav-link-ref">Tasking</router-link>
              </template>

            </b-dropdown>

            
          </ul>
        </div>
      </nav>
    </div>
  </div>
</template>

<script lang="ts">
export default {
  mounted() {
    this.activateMenuItems()
  },
  methods: {
    /**
     * Activates the appropriate menu items based on the current URL path
     * Applies CSS classes to highlight the current page in the navigation menu
     */
    activateMenuItems() {
      // Get all navigation links with class 'side-nav-link-ref'
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
            // Debug logging
            console.log(links[i]);
            break; // Exit loop once match is found
          }
        }
      }

      if (menuItemEl) {
        // Add active class to the menu item
        menuItemEl.classList.add('active')
        
        // Get parent element with null check
        const parentEl = menuItemEl.parentElement
        if (parentEl) {
          // level 1 - add active class to direct parent
          parentEl.classList.add('active')
          
          // Check for parent's parent
          const parentParentEl = parentEl.parentElement
          if (parentParentEl) {
            // Add active to parent's parent
            parentParentEl.classList.add('active')
            
            // Check for deeper nesting - level 2
            const level2El = parentParentEl.parentElement
            if (level2El) {
              // level 2 nested - add active class
              level2El.classList.add('active')
            }
          }
        }
      }
    },
  }
}
</script>
