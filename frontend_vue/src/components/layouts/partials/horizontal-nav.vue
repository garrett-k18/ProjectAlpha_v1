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
                <router-link to="/" class="dropdown-item side-nav-link-ref">Ecommerce</router-link>
                <router-link to="/projects" class="dropdown-item side-nav-link-ref">Projects</router-link>
                <router-link to="/crm" class="dropdown-item side-nav-link-ref">CRM</router-link>
                <router-link to="/e-wallet" class="dropdown-item side-nav-link-ref">E-Wallet</router-link>
              </template>

            </b-dropdown>

            <li class="nav-item dropdown">
              <a class="nav-link dropdown-toggle arrow-none" href="#" id="topnav-apps" role="button"
                 data-bs-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
                <i class="uil-apps"></i>Apps
                <div class="arrow-down"></div>
              </a>
              <div class="dropdown-menu" aria-labelledby="topnav-apps">
                <router-link to="/apps/calendar" class="dropdown-item side-nav-link-ref">Calendar</router-link>
                <router-link to="/apps/chat" class="dropdown-item side-nav-link-ref">Chat</router-link>
                <div class="dropdown">
                  <a class="dropdown-item dropdown-toggle arrow-none" href="#" id="topnav-crm" role="button"
                     data-bs-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
                    CRM
                    <div class="arrow-down"></div>
                  </a>
                  <div class="dropdown-menu" aria-labelledby="topnav-crm">
                    <router-link to="/apps/crm/projects" class="dropdown-item side-nav-link-ref">Project</router-link>
                    <router-link to="/apps/crm/brokers" class="dropdown-item side-nav-link-ref">Brokers
                    </router-link>
                    <router-link to="/apps/crm/clients" class="dropdown-item side-nav-link-ref">Clients</router-link>
                    <router-link to="/apps/crm/management" class="dropdown-item side-nav-link-ref">Management
                    </router-link>
                  </div>
                </div>
                <div class="dropdown">
                  <a class="dropdown-item dropdown-toggle arrow-none" href="#" id="topnav-ecommerce" role="button"
                     data-bs-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
                    Ecommerce
                    <div class="arrow-down"></div>
                  </a>
                  <div class="dropdown-menu" aria-labelledby="topnav-ecommerce">
                    <router-link to="/apps/ecommerce/products" class="dropdown-item side-nav-link-ref">Products
                    </router-link>
                    <router-link to="/apps/ecommerce/products-details" class="dropdown-item side-nav-link-ref">Products
                      Details
                    </router-link>
                    <router-link to="/apps/ecommerce/orders" class="dropdown-item side-nav-link-ref">Orders
                    </router-link>
                    <router-link to="/apps/ecommerce/order-details" class="dropdown-item side-nav-link-ref">Order
                      Details
                    </router-link>
                    <router-link to="/apps/ecommerce/customers" class="dropdown-item side-nav-link-ref">Customers
                    </router-link>
                    <router-link to="/apps/ecommerce/shopping-cart" class="dropdown-item side-nav-link-ref">Shopping
                      Cart
                    </router-link>
                    <router-link to="/apps/ecommerce/checkout" class="dropdown-item side-nav-link-ref">Checkout
                    </router-link>
                    <router-link to="/apps/ecommerce/sellers" class="dropdown-item side-nav-link-ref">Sellers
                    </router-link>
                  </div>
                </div>
                <div class="dropdown">
                  <a class="dropdown-item dropdown-toggle arrow-none" href="#" id="topnav-email" role="button"
                     data-bs-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
                    Email
                    <div class="arrow-down"></div>
                  </a>
                  <div class="dropdown-menu" aria-labelledby="topnav-email">
                    <router-link to="/apps/email/inbox" class="dropdown-item side-nav-link-ref">Inbox</router-link>
                    <router-link to="/apps/email/read" class="dropdown-item side-nav-link-ref">Read Email</router-link>
                  </div>
                </div>
                <div class="dropdown">
                  <a class="dropdown-item dropdown-toggle arrow-none" href="#" id="topnav-project" role="button"
                     data-bs-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
                    Projects
                    <div class="arrow-down"></div>
                  </a>
                  <div class="dropdown-menu" aria-labelledby="topnav-project">
                    <router-link to="/apps/projects/list" class="dropdown-item side-nav-link-ref">List</router-link>
                    <router-link to="/apps/projects/details" class="dropdown-item side-nav-link-ref">Details
                    </router-link>
                    <router-link to="/apps/projects/gantt" class="dropdown-item side-nav-link-ref">Gantt</router-link>
                    <router-link to="/apps/projects/create" class="dropdown-item side-nav-link-ref">Create Project
                    </router-link>
                  </div>
                </div>
                <router-link to="/apps/social-feed" class="dropdown-item side-nav-link-ref">Social Feed</router-link>
                <div class="dropdown">
                  <a class="dropdown-item dropdown-toggle arrow-none" href="#" id="topnav-tasks" role="button"
                     data-bs-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
                    Tasks
                    <div class="arrow-down"></div>
                  </a>
                  <div class="dropdown-menu" aria-labelledby="topnav-tasks">
                    <router-link to="/apps/tasks/list" class="dropdown-item side-nav-link-ref">List</router-link>
                    <router-link to="/apps/tasks/details" class="dropdown-item side-nav-link-ref">Details</router-link>
                    <router-link to="/apps/tasks/kanban" class="dropdown-item side-nav-link-ref">Kanban Board
                    </router-link>
                  </div>
                </div>
                <router-link to="/apps/file-manager" class="dropdown-item side-nav-link-ref">File Manager</router-link>
              </div>
            </li>
            <li class="nav-item dropdown">
              <a class="nav-link dropdown-toggle arrow-none" href="#" id="topnav-pages" role="button"
                 data-bs-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
                <i class="uil-copy-alt"></i>Pages
                <div class="arrow-down"></div>
              </a>
              <div class="dropdown-menu" aria-labelledby="topnav-pages">
                <div class="dropdown">
                  <a class="dropdown-item dropdown-toggle arrow-none" href="#" id="topnav-auth" role="button"
                     data-bs-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
                    Authenitication
                    <div class="arrow-down"></div>
                  </a>
                  <div class="dropdown-menu" aria-labelledby="topnav-auth">
                    <router-link to="/login" class="dropdown-item side-nav-link-ref">Login</router-link>
                    <router-link to="/login-2" class="dropdown-item side-nav-link-ref">Login 2</router-link>
                    <router-link to="/register" class="dropdown-item side-nav-link-ref">Register</router-link>
                    <router-link to="/register-2" class="dropdown-item side-nav-link-ref">Register 2</router-link>
                    <router-link to="/logout" class="dropdown-item side-nav-link-ref">Logout</router-link>
                    <router-link to="/logout-2" class="dropdown-item side-nav-link-ref">Logout 2</router-link>
                    <router-link to="/recoverpw" class="dropdown-item side-nav-link-ref">Recover Password</router-link>
                    <router-link to="/recoverpw-2" class="dropdown-item side-nav-link-ref">Recover Password 2
                    </router-link>
                    <router-link to="/lock-screen" class="dropdown-item side-nav-link-ref">Lock Screen</router-link>
                    <router-link to="/lock-screen-2" class="dropdown-item side-nav-link-ref">Lock Screen 2</router-link>
                    <router-link to="/confirm-mail" class="dropdown-item side-nav-link-ref">Confirm Mail</router-link>
                    <router-link to="/confirm-mail-2" class="dropdown-item side-nav-link-ref">Confirm Mail 2
                    </router-link>
                  </div>
                </div>
                <div class="dropdown">
                  <a class="dropdown-item dropdown-toggle arrow-none" href="#" id="topnav-error" role="button"
                     data-bs-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
                    Error
                    <div class="arrow-down"></div>
                  </a>
                  <div class="dropdown-menu" aria-labelledby="topnav-error">
                    <router-link to="/error-404" class="dropdown-item side-nav-link-ref">Error 404</router-link>
                    <router-link to="/error-404-alt" class="dropdown-item side-nav-link-ref">Error 404-alt</router-link>
                    <router-link to="/error-500" class="dropdown-item side-nav-link-ref">Error 500</router-link>
                  </div>
                </div>
                <router-link to="/pages/starter" class="dropdown-item side-nav-link-ref">Starter Page</router-link>
                <router-link to="/pages/preloader" class="dropdown-item side-nav-link-ref">With Preloader</router-link>
                <router-link to="/pages/profile" class="dropdown-item side-nav-link-ref">Profile</router-link>
                <router-link to="/pages/profile-2" class="dropdown-item side-nav-link-ref">Profile 2</router-link>
                <router-link to="/pages/invoice" class="dropdown-item side-nav-link-ref">Invoice</router-link>
                <router-link to="/pages/faq" class="dropdown-item side-nav-link-ref">FAQ</router-link>
                <router-link to="/pages/pricing" class="dropdown-item side-nav-link-ref">Pricing</router-link>
                <router-link to="/pages/maintenance" class="dropdown-item side-nav-link-ref">Maintenance</router-link>
                <router-link to="/pages/timeline" class="dropdown-item side-nav-link-ref">Timeline</router-link>
                <router-link to="/landing" class="dropdown-item side-nav-link-ref">Landing</router-link>
              </div>
            </li>
            <li class="nav-item dropdown">
              <a class="nav-link dropdown-toggle arrow-none" href="#" id="topnav-components" role="button"
                 data-bs-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
                <i class="uil-package"></i>Components
                <div class="arrow-down"></div>
              </a>
              <div class="dropdown-menu" aria-labelledby="topnav-components">
                <router-link to="/widgets" class="dropdown-item side-nav-link-ref">Widgets</router-link>
                <div class="dropdown">
                  <a class="dropdown-item dropdown-toggle arrow-none" href="#" id="topnav-ui-kit" role="button"
                     data-bs-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
                    Base UI 1
                    <div class="arrow-down"></div>
                  </a>
                  <div class="dropdown-menu" aria-labelledby="topnav-ui-kit">
                    <router-link to="/ui/accordions" class="dropdown-item side-nav-link-ref">Accordions</router-link>
                    <router-link to="/ui/alerts" class="dropdown-item side-nav-link-ref">Alerts</router-link>
                    <router-link to="/ui/avatars" class="dropdown-item side-nav-link-ref">Avatars</router-link>
                    <router-link to="/ui/badges" class="dropdown-item side-nav-link-ref">Badges</router-link>
                    <router-link to="/ui/breadcrumb" class="dropdown-item side-nav-link-ref">Breadcrumb</router-link>
                    <router-link to="/ui/buttons" class="dropdown-item side-nav-link-ref">Buttons</router-link>
                    <router-link to="/ui/cards" class="dropdown-item side-nav-link-ref">Cards</router-link>
                    <router-link to="/ui/carousel" class="dropdown-item side-nav-link-ref">Carousel</router-link>
                    <router-link to="/ui/dropdowns" class="dropdown-item side-nav-link-ref">Dropdowns</router-link>
                    <router-link to="/ui/embed-video" class="dropdown-item side-nav-link-ref">Embed Video</router-link>
                    <router-link to="/ui/grid" class="dropdown-item side-nav-link-ref">Grid</router-link>
                    <router-link to="/ui/list-group" class="dropdown-item side-nav-link-ref">List Group</router-link>
                  </div>
                </div>
                <div class="dropdown">
                  <a class="dropdown-item dropdown-toggle arrow-none" href="#" id="topnav-ui-kit2" role="button"
                     data-bs-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
                    Base UI 2
                    <div class="arrow-down"></div>
                  </a>
                  <div class="dropdown-menu" aria-labelledby="topnav-ui-kit2">
                    <router-link to="/ui/modals" class="dropdown-item side-nav-link-ref">Modals</router-link>
                    <router-link to="/ui/notifications" class="dropdown-item side-nav-link-ref">Notifications
                    </router-link>
                    <router-link to="/ui/offcanvas" class="dropdown-item side-nav-link-ref">Offcanvas</router-link>
                    <router-link to="/ui/placeholders" class="dropdown-item side-nav-link-ref">Placeholders
                    </router-link>
                    <router-link to="/ui/pagination" class="dropdown-item side-nav-link-ref">Pagination</router-link>
                    <router-link to="/ui/popovers" class="dropdown-item side-nav-link-ref">Popovers</router-link>
                    <router-link to="/ui/progress" class="dropdown-item side-nav-link-ref">Progress</router-link>
                    <router-link to="/ui/ribbons" class="dropdown-item side-nav-link-ref">Ribbons</router-link>
                    <router-link to="/ui/spinners" class="dropdown-item side-nav-link-ref">Spinners</router-link>
                    <router-link to="/ui/tabs" class="dropdown-item side-nav-link-ref">Tabs</router-link>
                    <router-link to="/ui/tooltips" class="dropdown-item side-nav-link-ref">Tooltips</router-link>
                    <router-link to="/ui/links" class="dropdown-item side-nav-link-ref">Links</router-link>
                    <router-link to="/ui/typography" class="dropdown-item side-nav-link-ref">Typography</router-link>
                    <router-link to="/ui/utilities" class="dropdown-item side-nav-link-ref">Utilities</router-link>
                  </div>
                </div>
                <div class="dropdown">
                  <a class="dropdown-item dropdown-toggle arrow-none" href="#" id="topnav-extended-ui" role="button"
                     data-bs-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
                    Extended UI
                    <div class="arrow-down"></div>
                  </a>
                  <div class="dropdown-menu" aria-labelledby="topnav-extended-ui">
                    <router-link to="/extended/dragula" class="dropdown-item side-nav-link-ref">Dragula</router-link>
                    <router-link to="/extended/range-slider" class="dropdown-item side-nav-link-ref">Range Slider
                    </router-link>
                    <router-link to="/extended/ratings" class="dropdown-item side-nav-link-ref">Ratings</router-link>
                    <router-link to="/extended/scrollbar" class="dropdown-item side-nav-link-ref">Scrollbar
                    </router-link>
                    <router-link to="/extended/scrollspy" class="dropdown-item side-nav-link-ref">Scrollspy
                    </router-link>
                    <router-link to="/extended/treeview" class="dropdown-item side-nav-link-ref">Treeview</router-link>
                  </div>
                </div>
                <div class="dropdown">
                  <a class="dropdown-item dropdown-toggle arrow-none" href="#" id="topnav-forms" role="button"
                     data-bs-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
                    Forms
                    <div class="arrow-down"></div>
                  </a>
                  <div class="dropdown-menu" aria-labelledby="topnav-forms">
                    <router-link to="/forms/elements" class="dropdown-item side-nav-link-ref">Basic Elements
                    </router-link>
                    <router-link to="/forms/advanced" class="dropdown-item side-nav-link-ref">Form Advanced
                    </router-link>
                    <router-link to="/forms/validation" class="dropdown-item side-nav-link-ref">Validation</router-link>
                    <router-link to="/forms/wizard" class="dropdown-item side-nav-link-ref">Wizard</router-link>
                    <router-link to="/forms/fileuploads" class="dropdown-item side-nav-link-ref">File Uploads
                    </router-link>
                    <router-link to="/forms/editor" class="dropdown-item side-nav-link-ref">Editors</router-link>
                  </div>
                </div>
                <div class="dropdown">
                  <a class="dropdown-item dropdown-toggle arrow-none" href="#" id="topnav-charts" role="button"
                     data-bs-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
                    Charts
                    <div class="arrow-down"></div>
                  </a>
                  <div class="dropdown-menu" aria-labelledby="topnav-charts">
                    <router-link to="/charts/chartjs/area" class="dropdown-item side-nav-link-ref">Chartjs</router-link>
                    <router-link to="/charts/apex/line" class="dropdown-item side-nav-link-ref">Apex Charts
                    </router-link>
                    <router-link to="/charts/sparkline" class="dropdown-item side-nav-link-ref">Sparklines</router-link>
                  </div>
                </div>
                <div class="dropdown">
                  <a class="dropdown-item dropdown-toggle arrow-none" href="#" id="topnav-tables" role="button"
                     data-bs-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
                    Tables
                    <div class="arrow-down"></div>
                  </a>
                  <div class="dropdown-menu" aria-labelledby="topnav-tables">
                    <router-link to="/tables/basic" class="dropdown-item side-nav-link-ref">Basic Tables</router-link>
                    <router-link to="/tables/datatable" class="dropdown-item side-nav-link-ref">Data Tables
                    </router-link>
                    <router-link to="/tables/advanced" class="dropdown-item side-nav-link-ref">Advanced</router-link>
                  </div>
                </div>
                <div class="dropdown">
                  <a class="dropdown-item dropdown-toggle arrow-none" href="#" id="topnav-icons" role="button"
                     data-bs-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
                    Icons
                    <div class="arrow-down"></div>
                  </a>
                  <div class="dropdown-menu" aria-labelledby="topnav-icons">
                    <router-link to="/icons/remix-icons" class="dropdown-item side-nav-link-ref">Remix Icons
                    </router-link>
                    <router-link to="/icons/mdi" class="dropdown-item side-nav-link-ref">Material Design</router-link>
                    <router-link to="/icons/unicons" class="dropdown-item side-nav-link-ref">Unicons</router-link>
                  </div>
                </div>
                <div class="dropdown">
                  <a class="dropdown-item dropdown-toggle arrow-none" href="#" id="topnav-maps" role="button"
                     data-bs-toggle="dropdown" aria-expanded="false">
                    Maps
                    <div class="arrow-down"></div>
                  </a>
                  <div class="dropdown-menu" aria-labelledby="topnav-maps">
                    <router-link to="/maps/google-map" class="dropdown-item side-nav-link-ref">Google Maps</router-link>
                    <router-link to="/maps/vector-map" class="dropdown-item side-nav-link-ref">Vector Maps</router-link>
                  </div>
                </div>
              </div>
            </li>
            <li class="nav-item dropdown">
              <a class="nav-link dropdown-toggle arrow-none" href="#" id="topnav-layouts" role="button"
                 data-bs-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
                <i class="uil-window"></i>Layouts
                <div class="arrow-down"></div>
              </a>
              <div class="dropdown-menu" aria-labelledby="topnav-layouts">
                <router-link to="/layout/vertical" class="dropdown-item side-nav-link-ref" target="_blank">Vertical
                </router-link>
                <router-link to="/layout/horizontal" class="dropdown-item side-nav-link-ref" target="_blank">
                  Horizontal
                </router-link>
                <router-link to="/layout/detached" class="dropdown-item side-nav-link-ref" target="_blank">Detached
                </router-link>
                <router-link to="/layout/full" class="dropdown-item side-nav-link-ref" target="_blank">Full
                </router-link>
                <router-link to="/layout/fullscreen" class="dropdown-item side-nav-link-ref" target="_blank">
                  Fullscreen
                </router-link>
                <router-link to="/layout/hover" class="dropdown-item side-nav-link-ref" target="_blank">Hover Menu
                </router-link>
                <router-link to="/layout/compact" class="dropdown-item side-nav-link-ref" target="_blank">Compact Menu
                </router-link>
                <router-link to="/layout/icon-view" class="dropdown-item side-nav-link-ref" target="_blank">Icon View
                </router-link>
              </div>
            </li>
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
