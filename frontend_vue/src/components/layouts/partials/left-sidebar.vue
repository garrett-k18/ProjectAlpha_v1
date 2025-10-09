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

        <li class="side-nav-title">Navigation</li>

        <li class="side-nav-item menuitem-active">
          <router-link to="/home" class="side-nav-link side-nav-link-ref">
            <i class="uil-home-alt"></i>
            <b-badge class="float-end" variant="success">5</b-badge>
            <span> Home </span>
          </router-link>
          <!-- Indent the dashboard sub-links under Home - always visible -->
          <ul class="side-nav-second-level" style="display: block; padding-left: 3.5rem;">
            <li>
              <router-link to="/acquisitions" class="side-nav-link-ref">Acquisitions</router-link>
            </li>
            <li>
              <router-link to="/asset-mgmt" class="side-nav-link-ref">Asset Management</router-link>
            </li>
            <li>
              <router-link to="/projects" class="side-nav-link-ref">Projects</router-link>
            </li>
            <li>
              <router-link to="/crm" class="side-nav-link-ref">CRM</router-link>
            </li>
            <li>
              <router-link to="/e-wallet" class="side-nav-link-ref">E-Wallet</router-link>
            </li>
          </ul>
        </li>

        <li class="side-nav-item">
          <router-link to="/assumptions" class="side-nav-link side-nav-link-ref">
            <i class="uil-cog"></i>
            <span> Assumptions </span>
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
          <router-link to="/apps/chat" class="side-nav-link side-nav-link-ref">
            <i class="uil-comments-alt"></i>
            <span> Chat </span>
          </router-link>
        </li>

        <li class="side-nav-item">
          <router-link to="/apps/file-manager" class="side-nav-link side-nav-link-ref">
            <i class="uil-folder-plus"></i>
            <span> Documents </span>
          </router-link>
        </li>

        <li class="side-nav-item" role="button">
          <a v-b-toggle.sidebarCrm class="side-nav-link">
            <i class="uil uil-tachometer-fast"></i>
            <b-badge class="text-white float-end" variant="danger">New</b-badge>
            <span> CRM </span>
          </a>
          <b-collapse id="sidebarCrm">
            <ul class="side-nav-second-level">
              <li>
                <router-link to="/apps/crm/brokers" class="side-nav-link-ref">Brokers</router-link>
              </li>
              <li>
                <router-link to="/apps/crm/tradingpartners" class="side-nav-link-ref">Trading Partners</router-link>
              </li>
              <li>
                <router-link to="/apps/crm/investors" class="side-nav-link-ref">Investors</router-link>
              </li>
              <li>
                <router-link to="/apps/crm/management" class="side-nav-link-ref">Management</router-link>
              </li>
            </ul>
          </b-collapse>
        </li>

        <li class="side-nav-item" role="button">
          <a v-b-toggle.sidebarEcommerce class="side-nav-link">
            <i class="uil-store"></i>
            <span> Ecommerce </span>
            <span class="menu-arrow"></span>
          </a>
          <b-collapse id="sidebarEcommerce">
            <ul class="side-nav-second-level">
              <li>
                <router-link to="/apps/ecommerce/products" class="side-nav-link-ref">Products</router-link>
              </li>
              <li>
                <router-link to="/apps/ecommerce/products-details" class="side-nav-link-ref">Products Details
                </router-link>
              </li>
              <li>
                <router-link to="/apps/ecommerce/orders" class="side-nav-link-ref">Orders</router-link>
              </li>
              <li>
                <router-link to="/apps/ecommerce/order-detail" class="side-nav-link-ref">Order Details</router-link>
              </li>
              <li>
                <router-link to="/apps/ecommerce/customers" class="side-nav-link-ref">Customers</router-link>
              </li>
              <li>
                <router-link to="/apps/ecommerce/shopping-cart" class="side-nav-link-ref">Shopping Cart</router-link>
              </li>
              <li>
                <router-link to="/apps/ecommerce/checkout" class="side-nav-link-ref">Checkout</router-link>
              </li>
              <li>
                <router-link to="/apps/ecommerce/sellers" class="side-nav-link-ref">Sellers</router-link>
              </li>
            </ul>
          </b-collapse>
        </li>

        <li class="side-nav-item" role="button">
          <a v-b-toggle.sidebarEmail class="side-nav-link">
            <i class="uil-envelope"></i>
            <span> Email </span>
            <span class="menu-arrow"></span>
          </a>
          <b-collapse id="sidebarEmail">
            <ul class="side-nav-second-level">
              <li>
                <router-link to="/apps/email/inbox" class="side-nav-link-ref">Inbox</router-link>
              </li>
              <li>
                <router-link to="/apps/email/read" class="side-nav-link-ref">Read Email</router-link>
              </li>
            </ul>
          </b-collapse>
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

        <li class="side-nav-item">
          <router-link to="/apps/social-feed" class="side-nav-link side-nav-link-ref">
            <i class="uil-rss"></i>
            <span> Social Feed </span>
          </router-link>
        </li>

        <li class="side-nav-item">
          <a v-b-toggle.sidebarTasks href="#" class="side-nav-link">
            <i class="uil-clipboard-alt"></i>
            <span> Tasks </span>
            <span class="menu-arrow"></span>
          </a>
          <b-collapse id="sidebarTasks">
            <ul class="side-nav-second-level">
              <li>
                <router-link to="/apps/tasks/list" class="side-nav-link-ref">List</router-link>
              </li>
              <li>
                <router-link to="/apps/tasks/details" class="side-nav-link-ref">Details</router-link>
              </li>
              <li>
                <router-link to="/apps/tasks/kanban" class="side-nav-link-ref">Kanban Board</router-link>
              </li>
            </ul>
          </b-collapse>
        </li>

        <li class="side-nav-title">Custom</li>

        <li class="side-nav-item" role="button">
          <a v-b-toggle.sidebarPages class="side-nav-link">
            <i class="uil-copy-alt"></i>
            <span> Pages </span>
            <span class="menu-arrow"></span>
          </a>
          <b-collapse id="sidebarPages">
            <ul class="side-nav-second-level">
              <li>
                <router-link to="/pages/profile" class="side-nav-link-ref">Profile</router-link>
              </li>
              <li>
                <router-link to="/pages/profile-2" class="side-nav-link-ref">Profile 2</router-link>
              </li>
              <li>
                <router-link to="/pages/invoice" class="side-nav-link-ref">Invoice</router-link>
              </li>
              <li>
                <router-link to="/pages/faq" class="side-nav-link-ref">FAQ</router-link>
              </li>
              <li>
                <router-link to="/pages/pricing" class="side-nav-link-ref">Pricing</router-link>
              </li>
              <li>
                <router-link to="/pages/maintenance" class="side-nav-link-ref">Maintenance</router-link>
              </li>
              <li class="side-nav-item" role="button">
                <a v-b-toggle.sidebarPagesAuth>
                  <span> Authentication </span>
                  <span class="menu-arrow"></span>
                </a>
                <b-collapse id="sidebarPagesAuth">
                  <ul class="side-nav-third-level">
                    <li>
                      <router-link to="/login" class="side-nav-link-ref">Login</router-link>
                    </li>
                    <li>
                      <router-link to="/login-2" class="side-nav-link-ref">Login 2</router-link>
                    </li>
                    <li>
                      <router-link to="/register" class="side-nav-link-ref">Register</router-link>
                    </li>
                    <li>
                      <router-link to="/register-2" class="side-nav-link-ref">Register 2</router-link>
                    </li>
                    <li>
                      <router-link to="/logout" class="side-nav-link-ref">Logout</router-link>
                    </li>
                    <li>
                      <router-link to="/logout-2" class="side-nav-link-ref">Logout 2</router-link>
                    </li>
                    <li>
                      <router-link to="/recoverpw" class="side-nav-link-ref">Recover Password</router-link>
                    </li>
                    <li>
                      <router-link to="/recoverpw-2" class="side-nav-link-ref">Recover Password 2</router-link>
                    </li>
                    <li>
                      <router-link to="/lock-screen" class="side-nav-link-ref">Lock Screen</router-link>
                    </li>
                    <li>
                      <router-link to="/lock-screen-2" class="side-nav-link-ref">Lock Screen 2</router-link>
                    </li>
                    <li>
                      <router-link to="/confirm-mail" class="side-nav-link-ref">Confirm Mail</router-link>
                    </li>
                    <li>
                      <router-link to="/confirm-mail-2" class="side-nav-link-ref">Confirm Mail 2</router-link>
                    </li>
                  </ul>
                </b-collapse>
              </li>
              <li class="side-nav-item" role="button">
                <a v-b-toggle.sidebarPagesError aria-expanded="false" aria-controls="sidebarPagesError">
                  <span> Error </span>
                  <span class="menu-arrow"></span>
                </a>
                <b-collapse id="sidebarPagesError">
                  <ul class="side-nav-third-level">
                    <li>
                      <router-link to="/error-404" class="side-nav-link-ref">Error 404</router-link>
                    </li>
                    <li>
                      <router-link to="/error-404-alt" class="side-nav-link-ref">Error 404-alt</router-link>
                    </li>
                    <li>
                      <router-link to="/error-500" class="side-nav-link-ref">Error 500</router-link>
                    </li>
                  </ul>
                </b-collapse>
              </li>
              <li>
                <router-link to="/pages/starter" class="side-nav-link-ref">Starter Page</router-link>
              </li>
              <li>
                <router-link to="/pages/preloader" class="side-nav-link-ref">With Preloader</router-link>
              </li>
              <li>
                <router-link to="/pages/timeline" class="side-nav-link-ref">Timeline</router-link>
              </li>
            </ul>
          </b-collapse>
        </li>

        <li class="side-nav-item">
          <router-link to="/landing" target="_blank" class="side-nav-link side-nav-link-ref">
            <i class="uil-globe"></i>
            <b-badge class="text-white float-end" variant="secondary">New</b-badge>
            <span> Landing </span>
          </router-link>
        </li>

        <li class="side-nav-item" role="button">
          <a v-b-toggle.sidebarLayouts href="#" class="side-nav-link">
            <i class="uil-window"></i>
            <span> Layouts </span>
            <span class="menu-arrow"></span>
          </a>
          <b-collapse id="sidebarLayouts">
            <ul class="side-nav-second-level">
              <li>
                <router-link to="/layout/horizontal" target="_blank" class="side-nav-link-ref">Horizontal</router-link>
              </li>
              <li>
                <router-link to="/layout/detached" target="_blank" class="side-nav-link-ref">Detached</router-link>
              </li>
              <li>
                <router-link to="/layout/full" target="_blank" class="side-nav-link-ref">Full View</router-link>
              </li>
              <li>
                <router-link to="/layout/fullscreen" target="_blank" class="side-nav-link-ref">Fullscreen View
                </router-link>
              </li>
              <li>
                <router-link to="/layout/hover" target="_blank" class="side-nav-link-ref">Hover Menu</router-link>
              </li>
              <li>
                <router-link to="/layout/compact" target="_blank" class="side-nav-link-ref">Compact</router-link>
              </li>
              <li>
                <router-link to="/layout/icon-view" target="_blank" class="side-nav-link-ref">Icon View</router-link>
              </li>
            </ul>
          </b-collapse>
        </li>

        <li class="side-nav-title">Components</li>

        <li class="side-nav-item" role="button">
          <a v-b-toggle.sidebarBaseUI class="side-nav-link">
            <i class="uil-box"></i>
            <span> Base UI </span>
            <span class="menu-arrow"></span>
          </a>
          <b-collapse id="sidebarBaseUI">
            <ul class="side-nav-second-level">
              <li>
                <router-link to="/ui/accordions" class="side-nav-link-ref">Accordions & Collapse</router-link>
              </li>
              <li>
                <router-link to="/ui/alerts" class="side-nav-link-ref">Alerts</router-link>
              </li>
              <li>
                <router-link to="/ui/avatars" class="side-nav-link-ref">Avatars</router-link>
              </li>
              <li>
                <router-link to="/ui/badges" class="side-nav-link-ref">Badges</router-link>
              </li>
              <li>
                <router-link to="/ui/breadcrumb" class="side-nav-link-ref">Breadcrumb</router-link>
              </li>
              <li>
                <router-link to="/ui/buttons" class="side-nav-link-ref">Buttons</router-link>
              </li>
              <li>
                <router-link to="/ui/cards" class="side-nav-link-ref">Cards</router-link>
              </li>
              <li>
                <router-link to="/ui/carousel" class="side-nav-link-ref">Carousel</router-link>
              </li>
              <li>
                <router-link to="/ui/dropdowns" class="side-nav-link-ref">Dropdowns</router-link>
              </li>
              <li>
                <router-link to="/ui/embed-video" class="side-nav-link-ref">Embed Video</router-link>
              </li>
              <li>
                <router-link to="/ui/grid" class="side-nav-link-ref">Grid</router-link>
              </li>
              <li>
                <router-link to="/ui/list-group" class="side-nav-link-ref">List Group</router-link>
              </li>
              <li>
                <router-link to="/ui/modals" class="side-nav-link-ref">Modals</router-link>
              </li>
              <li>
                <router-link to="/ui/notifications" class="side-nav-link-ref">Notifications</router-link>
              </li>
              <li>
                <router-link to="/ui/offcanvas" class="side-nav-link-ref">Offcanvas</router-link>
              </li>
              <li>
                <router-link to="/ui/placeholders" class="side-nav-link-ref">Placeholders</router-link>
              </li>
              <li>
                <router-link to="/ui/pagination" class="side-nav-link-ref">Pagination</router-link>
              </li>
              <li>
                <router-link to="/ui/popovers" class="side-nav-link-ref">Popovers</router-link>
              </li>
              <li>
                <router-link to="/ui/progress" class="side-nav-link-ref">Progress</router-link>
              </li>
              <li>
                <router-link to="/ui/ribbons" class="side-nav-link-ref">Ribbons</router-link>
              </li>
              <li>
                <router-link to="/ui/spinners" class="side-nav-link-ref">Spinners</router-link>
              </li>
              <li>
                <router-link to="/ui/tabs" class="side-nav-link-ref">Tabs</router-link>
              </li>
              <li>
                <router-link to="/ui/tooltips" class="side-nav-link-ref">Tooltips</router-link>
              </li>
              <li>
                <router-link to="/ui/links" class="side-nav-link-ref">Links</router-link>
              </li>
              <li>
                <router-link to="/ui/typography" class="side-nav-link-ref">Typography</router-link>
              </li>
              <li>
                <router-link to="/ui/utilities" class="side-nav-link-ref">Utilities</router-link>
              </li>
            </ul>
          </b-collapse>
        </li>

        <li class="side-nav-item" role="button">
          <a v-b-toggle.sidebarExtendedUI class="side-nav-link">
            <i class="uil-package"></i>
            <span> Extended UI </span>
            <span class="menu-arrow"></span>
          </a>
          <b-collapse id="sidebarExtendedUI">
            <ul class="side-nav-second-level">
              <li>
                <router-link to="/extended/dragula" class="side-nav-link-ref">Dragula</router-link>
              </li>
              <li>
                <router-link to="/extended/range-slider" class="side-nav-link-ref">Range Slider</router-link>
              </li>
              <li>
                <router-link to="/extended/ratings" class="side-nav-link-ref">Ratings</router-link>
              </li>
              <li>
                <router-link to="/extended/scrollbar" class="side-nav-link-ref">Scrollbar</router-link>
              </li>
              <li>
                <router-link to="/extended/scrollspy" class="side-nav-link-ref">Scrollspy</router-link>
              </li>
              <li>
                <router-link to="/extended/treeview" class="side-nav-link-ref">Treeview</router-link>
              </li>
            </ul>
          </b-collapse>
        </li>

        <li class="side-nav-item">
          <router-link to="/widgets" class="side-nav-link side-nav-link-ref">
            <i class="uil-layer-group"></i>
            <span> Widgets </span>
          </router-link>
        </li>

        <li class="side-nav-item" role="button">
          <a v-b-toggle.sidebarIcons class="side-nav-link">
            <i class="uil-streering"></i>
            <span> Icons </span>
            <span class="menu-arrow"></span>
          </a>
          <b-collapse id="sidebarIcons">
            <ul class="side-nav-second-level">
              <li>
                <router-link to="/icons/remix-icons" class="side-nav-link-ref">Remix Icons</router-link>
              </li>
              <li>
                <router-link to="/icons/mdi" class="side-nav-link-ref">Material Design</router-link>
              </li>
              <li>
                <router-link to="/icons/unicons" class="side-nav-link-ref">Unicons</router-link>
              </li>
            </ul>
          </b-collapse>
        </li>

        <li class="side-nav-item" role="button">
          <a v-b-toggle.sidebarCharts class="side-nav-link">
            <i class="uil-chart"></i>
            <span> Charts </span>
            <span class="menu-arrow"></span>
          </a>
          <b-collapse id="sidebarCharts">
            <ul class="side-nav-second-level">
              <li class="side-nav-item" role="button">
                <a v-b-toggle.sidebarApexCharts aria-expanded="false" aria-controls="sidebarApexCharts">
                  <span> Apex Charts </span>
                  <span class="menu-arrow"></span>
                </a>
                <b-collapse id="sidebarApexCharts">
                  <ul class="side-nav-third-level">
                    <li>
                      <router-link to="/charts/apex/area" class="side-nav-link-ref">Area</router-link>
                    </li>
                    <li>
                      <router-link to="/charts/apex/bar" class="side-nav-link-ref">Bar</router-link>
                    </li>
                    <li>
                      <router-link to="/charts/apex/bubble" class="side-nav-link-ref">Bubble</router-link>
                    </li>
                    <li>
                      <router-link to="/charts/apex/candlestick" class="side-nav-link-ref">Candlestick</router-link>
                    </li>
                    <li>
                      <router-link to="/charts/apex/column" class="side-nav-link-ref">Column</router-link>
                    </li>
                    <li>
                      <router-link to="/charts/apex/heatmap" class="side-nav-link-ref">Heatmap</router-link>
                    </li>
                    <li>
                      <router-link to="/charts/apex/line" class="side-nav-link-ref">Line</router-link>
                    </li>
                    <li>
                      <router-link to="/charts/apex/mixed" class="side-nav-link-ref">Mixed</router-link>
                    </li>
                    <li>
                      <router-link to="/charts/apex/timeline" class="side-nav-link-ref">Timeline</router-link>
                    </li>
<!--                    <li>-->
<!--                      <router-link to="/charts/apex/boxplot" class="side-nav-link-ref">Boxplot</router-link>-->
<!--                    </li>-->
                    <li>
                      <router-link to="/charts/apex/treemap" class="side-nav-link-ref">Treemap</router-link>
                    </li>
                    <li>
                      <router-link to="/charts/apex/pie" class="side-nav-link-ref">Pie</router-link>
                    </li>
                    <li>
                      <router-link to="/charts/apex/radar" class="side-nav-link-ref">Radar</router-link>
                    </li>
                    <li>
                      <router-link to="/charts/apex/radialbar" class="side-nav-link-ref">RadialBar</router-link>
                    </li>
                    <li>
                      <router-link to="/charts/apex/scatter" class="side-nav-link-ref">Scatter</router-link>
                    </li>
                    <li>
                      <router-link to="/charts/apex/polar-area" class="side-nav-link-ref">Polar Area</router-link>
                    </li>
                  </ul>
                </b-collapse>
              </li>
              <li class="side-nav-item" role="button">
                <a v-b-toggle.sidebarChartJSCharts>
                  <span> ChartJS </span>
                  <span class="menu-arrow"></span>
                </a>
                <b-collapse id="sidebarChartJSCharts">
                  <ul class="side-nav-third-level">
                    <li>
                      <router-link to="/charts/chartjs/area" class="side-nav-link-ref">Area</router-link>
                    </li>
                    <li>
                      <router-link to="/charts/chartjs/bar" class="side-nav-link-ref">Bar</router-link>
                    </li>
                    <li>
                      <router-link to="/charts/chartjs/line" class="side-nav-link-ref">Line</router-link>
                    </li>
                    <li>
                      <router-link to="/charts/chartjs/other" class="side-nav-link-ref">Other</router-link>
                    </li>

                  </ul>
                </b-collapse>
              </li>

              <li>
                <router-link to="/charts/sparkline" class="side-nav-link-ref">Sparklines</router-link>
              </li>
            </ul>
          </b-collapse>
        </li>

        <li class="side-nav-item" role="button">
          <a v-b-toggle.sidebarForms class="side-nav-link">
            <i class="uil-document-layout-center"></i>
            <span> Forms </span>
            <span class="menu-arrow"></span>
          </a>
          <b-collapse id="sidebarForms">
            <ul class="side-nav-second-level">
              <li>
                <router-link to="/forms/elements" class="side-nav-link-ref">Basic Elements</router-link>
              </li>
              <li>
                <router-link to="/forms/advanced" class="side-nav-link-ref">Form Advanced</router-link>
              </li>
              <li>
                <router-link to="/forms/validation" class="side-nav-link-ref">Validation</router-link>
              </li>
              <li>
                <router-link to="/forms/wizard" class="side-nav-link-ref">Wizard</router-link>
              </li>
              <li>
                <router-link to="/forms/fileuploads" class="side-nav-link-ref">File Uploads</router-link>
              </li>
              <li>
                <router-link to="/forms/editor" class="side-nav-link-ref">Editors</router-link>
              </li>
            </ul>
          </b-collapse>
        </li>

        <li class="side-nav-item" role="button">
          <a v-b-toggle.sidebarTables class="side-nav-link">
            <i class="uil-table"></i>
            <span> Tables </span>
            <span class="menu-arrow"></span>
          </a>
          <b-collapse id="sidebarTables">
            <ul class="side-nav-second-level">
              <li>
                <router-link to="/tables/basic" class="side-nav-link-ref">Basic Tables</router-link>
              </li>
              <li>
                <router-link to="/tables/datatable" class="side-nav-link-ref">Data Tables</router-link>
              </li>
              <li>
                <router-link to="/tables/advanced" class="side-nav-link-ref">Advanced</router-link>
              </li>
            </ul>
          </b-collapse>
        </li>

        <li class="side-nav-item" role="button">
          <a v-b-toggle.sidebarMaps class="side-nav-link">
            <i class="uil-location-point"></i>
            <span> Maps </span>
            <span class="menu-arrow"></span>
          </a>
          <b-collapse id="sidebarMaps">
            <ul class="side-nav-second-level">
              <li>
                <router-link to="/maps/google-map" class="side-nav-link-ref">Google Maps</router-link>
              </li>
              <li>
                <router-link to="/maps/vector-map" class="side-nav-link-ref">Vector Maps</router-link>
              </li>
            </ul>
          </b-collapse>
        </li>

        <li class="side-nav-item" role="button">
          <a v-b-toggle.sidebarMultiLevel class="side-nav-link">
            <i class="uil-folder-plus"></i>
            <span> Multi Level </span>
            <span class="menu-arrow"></span>
          </a>
          <b-collapse id="sidebarMultiLevel">
            <ul class="side-nav-second-level">
              <li class="side-nav-item">
                <a v-b-toggle.sidebarSecondLevel>
                  <span> Second Level </span>
                  <span class="menu-arrow"></span>
                </a>
                <b-collapse id="sidebarSecondLevel">
                  <ul class="side-nav-third-level">
                    <li>
                      <a href="javascript: void(0);">Item 1</a>
                    </li>
                    <li>
                      <a href="javascript: void(0);">Item 2</a>
                    </li>
                  </ul>
                </b-collapse>
              </li>
              <li class="side-nav-item">
                <a v-b-toggle.sidebarThirdLevel>
                  <span> Third Level </span>
                  <span class="menu-arrow"></span>
                </a>
                <b-collapse id="sidebarThirdLevel">
                  <ul class="side-nav-third-level">
                    <li>
                      <a href="javascript: void(0);">Item 1</a>
                    </li>
                    <li class="side-nav-item">
                      <a data-bs-toggle="collapse" href="#sidebarFourthLevel" aria-expanded="false"
                         aria-controls="sidebarFourthLevel">
                        <span> Item 2 </span>
                        <span class="menu-arrow"></span>
                      </a>
                      <div class="collapse" id="sidebarFourthLevel">
                        <ul class="side-nav-forth-level">
                          <li>
                            <a href="javascript: void(0);">Item 2.1</a>
                          </li>
                          <li>
                            <a href="javascript: void(0);">Item 2.2</a>
                          </li>
                        </ul>
                      </div>
                    </li>
                  </ul>
                </b-collapse>
              </li>
            </ul>
          </b-collapse>
        </li>

        <div class="help-box text-white text-center">
          <a href="javascript: void(0);" class="float-end close-btn text-white">
            <i class="mdi mdi-close"></i>
          </a>
          <img src="@/assets/images/svg/help-icon.svg" height="90" alt="Helper Icon Image"/>
          <h5 class="mt-3">Unlimited Access</h5>
          <p class="mb-3">Upgrade to plan to get access to unlimited reports</p>
          <a href="javascript: void(0);" class="btn btn-secondary btn-sm">Upgrade</a>
        </div>

      </ul>
      <!--      <AppMenu/>-->
      <div class="clearfix"></div>
    </simplebar>
  </div>
</template>

<script lang="ts">
import simplebar from "simplebar-vue"

export default {
  components: {simplebar},
  mounted() {
    this.activateMenuItems()
    this.initSidenav()
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
