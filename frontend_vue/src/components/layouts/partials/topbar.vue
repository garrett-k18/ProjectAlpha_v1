<template>
  <div class="navbar-custom">
    <div class="topbar container-fluid">
      <div class="d-flex align-items-center gap-lg-2 gap-1">

        <!-- Topbar Brand Logo -->
        <div class="logo-topbar">
          <!-- Logo light -->
          <router-link to="/home" class="logo-light">
                    <span class="logo-lg">
                        <img src="@/assets/images/logo.svg" alt="projectalpha" height="62">
                    </span>
            <span class="logo-sm">
                        <img src="@/assets/images/logo-sm.png" alt="small logo">
                    </span>
          </router-link>

          <!-- Logo Dark -->
          <router-link to="/home" class="logo-dark">
                    <span class="logo-lg">
                        <img src="@/assets/images/logo.svg" alt="projectalpha" height="62">
                    </span>
            <span class="logo-sm">
                        <img src="@/assets/images/logo-dark-sm.png" alt="small logo">
                    </span>
          </router-link>
        </div>

        <!-- Sidebar Menu Toggle Button -->
        <button class="button-toggle-menu">
          <i class="mdi mdi-menu"></i>
        </button>

        <!-- Horizontal Menu Toggle Button -->
        <button class="navbar-toggle horizontal-button-toggle-menu" data-bs-toggle="collapse" data-bs-target="#topnav-menu-content">
          <div class="lines">
            <span></span>
            <span></span>
            <span></span>
          </div>
        </button>

        <!-- Topbar Search Form -->
        <b-nav-item-dropdown
            class="app-search d-none d-lg-block"
            menu-class="dropdown-menu dropdown-menu-animated dropdown-lg"
            toggle-class="arrow-none"
        >
          <template #button-content>
            <b-form>
              <b-form-group class="input-group">
                <b-form-input
                    type="search"
                    class="form-control dropdown-toggle"
                    placeholder="Search..."
                    id="top-search"
                />
                <span class="ri-search-line search-icon"></span>
              </b-form-group>
              <b-button variant="primary" class="input-group-text" type="submit">Search</b-button>
            </b-form>
          </template>

          <div style="width: 320px">
            <b-dropdown-header class="noti-title">
              <h5 class="text-overflow mb-2">Found <span class="text-danger">17</span> results</h5>
            </b-dropdown-header>

            <b-dropdown-item class="notify-item">
              <i class="uil-notes font-16 me-1"></i>
              <span>Analytics Report</span>
            </b-dropdown-item>

            <b-dropdown-item class="notify-item">
              <i class="uil-life-ring font-16 me-1"></i>
              <span>How can I help you?</span>
            </b-dropdown-item>

            <b-dropdown-item class="notify-item">
              <i class="uil-cog font-16 me-1"></i>
              <span>User profile settings</span>
            </b-dropdown-item>

            <b-dropdown-header class="noti-title">
              <h6 class="text-overflow mb-2 text-uppercase">Users</h6>
            </b-dropdown-header>

            <b-dropdown-item class="notify-item">
              <div class="d-flex">
                <img
                    class="d-flex me-2 rounded-circle"
                    src="@/assets/images/users/avatar-2.jpg"
                    alt="Generic placeholder image"
                    height="32"
                />
                <div class="w-100">
                  <h5 class="m-0 font-14">Erwin Brown</h5>
                  <span class="font-12 mb-0">UI Designer</span>
                </div>
              </div>
            </b-dropdown-item>

            <b-dropdown-item class="notify-item">
              <div class="d-flex">
                <img
                    class="d-flex me-2 rounded-circle"
                    src="@/assets/images/users/avatar-5.jpg"
                    alt="Generic placeholder image"
                    height="32"
                />
                <div class="w-100">
                  <h5 class="m-0 font-14">Jacob Deo</h5>
                  <span class="font-12 mb-0">Developer</span>
                </div>
              </div>
            </b-dropdown-item>
          </div>
        </b-nav-item-dropdown>
      </div>

      <ul class="topbar-menu d-flex align-items-center gap-3">
        <li class="dropdown d-lg-none">
          <a
              class="nav-link dropdown-toggle arrow-none"
              data-bs-toggle="dropdown"
              role="button"
              aria-haspopup="false"
              aria-expanded="false"
          >
            <i class="ri-search-line font-22"></i>
          </a>
          <div class="dropdown-menu dropdown-menu-animated dropdown-lg p-0">
            <b-form class="p-3">
              <b-form-input
                  type="search"
                  placeholder="Search ..."
                  aria-label="Recipient's username"
              />
            </b-form>
          </div>
        </li>


        <b-nav-item-dropdown
            class="notification-list"
            toggle-class="arrow-none"
            menu-class="dropdown-menu dropdown-menu-end dropdown-menu-animated py-0 dropdown-lg"
        >
          <template
              #button-content
              class="nav-link dropdown-toggle arrow-none"
          >
            <i class="ri-notification-3-line font-22"></i>
            <span class="noti-icon-badge"></span>
          </template>
          <div style="width: 320px">

            <div class="p-2 border-top-0 border-start-0 border-end-0 border-dashed border">
              <b-row class="align-items-center">
                <b-col>
                  <h6 class="m-0 font-16 fw-semibold">Notification</h6>
                </b-col>
                <b-col class="col-auto">
                  <a class="text-dark text-decoration-underline" @click.prevent="clearAllNotifications">
                    <small>Clear All</small>
                  </a>
                </b-col>
              </b-row>
            </div>

            <simplebar style="max-height: 300px" class="px-2 pt-2 overflow-x-hidden">

              <b-dropdown-item v-for="item in notificationItems"
                               :key="item.id"
                               class="p-0 mb-2 notify-item unread-noti card m-0 shadow-none"
              >
                <div class="card-body" style="width: inherit">
                  <span class="float-end noti-close-btn text-muted" @click.stop.prevent="markNotificationRead(item.id)"><i class="mdi mdi-close"></i></span>
                  <div class="d-flex align-items-center">
                    <div class="flex-shrink-0">
                      <div class="notify-icon" :class="`bg-primary`">
                        <i class="mdi mdi-bell-outline"></i>
                      </div>
                    </div>
                    <div class="flex-grow-1 text-truncate ms-2">
                      <h5 class="noti-item-title fw-semibold font-14">
                        {{ item.text }}
                      </h5>
                      <small class="noti-item-subtitle text-muted"
                      >{{ item.subText }}</small
                      >
                    </div>
                  </div>
                </div>
              </b-dropdown-item>
              <div v-if="isLoadingNotifications" class="text-center">
                <i class="mdi mdi-dots-circle mdi-spin text-muted h3 mt-0"></i>
              </div>
              <div v-if="!isLoadingNotifications && notificationItems.length === 0" class="text-center text-muted py-2">
                <small>No unread notifications</small>
              </div>
            </simplebar>
            <!-- All-->
            <b-dropdown-item
                class="text-center text-primary text-decoration-underline fw-bold p-0"
                link-class=" border-top"
                @click="goToActivity"
            >
              <div class="py-2">View All</div>
            </b-dropdown-item>
          </div>
        </b-nav-item-dropdown>

        <b-nav-item-dropdown
            toggle-class="arrow-none"
            class="d-none d-sm-inline-block"
            menu-class="dropdown-menu dropdown-menu-end dropdown-menu-animated p-0 dropdown-lg"
        >
          <template
              #button-content
              class="nav-link dropdown-toggle arrow-none"
          >
            <i class="ri-apps-2-line font-22"></i>
          </template>

          <div class="p-2" style="width: 320px">
            <b-row class="g-0">
              <b-col>
                <a class="dropdown-icon-item">
                  <img src="@/assets/images/brands/slack.png" alt="slack"/>
                  <span>Slack</span>
                </a>
              </b-col>

              <b-col>
                <a class="dropdown-icon-item">
                  <img src="@/assets/images/brands/github.png" alt="Github"/>
                  <span>GitHub</span>
                </a>
              </b-col>
              <b-col>
                <a class="dropdown-icon-item">
                  <img
                      src="@/assets/images/brands/dribbble.png"
                      alt="dribbble"
                  />
                  <span>Dribbble</span>
                </a>
              </b-col>

            </b-row>

            <b-row class="g-0">
              <b-col>
                <a class="dropdown-icon-item">
                  <img
                      src="@/assets/images/brands/bitbucket.png"
                      alt="bitbucket"
                  />
                  <span>Bitbucket</span>
                </a>
              </b-col>
              <b-col>
                <a class="dropdown-icon-item">
                  <img src="@/assets/images/brands/dropbox.png" alt="dropbox"/>
                  <span>Dropbox</span>
                </a>
              </b-col>

              <b-col>
                <a class="dropdown-icon-item">
                  <img src="@/assets/images/brands/g-suite.png" alt="Behance"/>
                  <span>G Suite</span>
                </a>
              </b-col>
            </b-row>
          </div >
        </b-nav-item-dropdown>

        <li class="d-none d-sm-inline-block">
          <a class="nav-link" @click="toggleRightSidebar">
            <i class="ri-settings-3-line font-22"></i>
          </a>
        </li>

        <li class="d-none d-sm-inline-block">
          <div class="nav-link" id="light-dark-mode" v-b-tooltip.hover.left
               title="Theme Mode">
            <i class="ri-moon-line font-22"></i>
          </div>
        </li>


        <li class="d-none d-md-inline-block">
          <button class="nav-link" @click="fullScreenListener">
            <i class="ri-fullscreen-line font-22"></i>
          </button>
        </li>

        <b-nav-item-dropdown
            toggle-class="arrow-none"
            class="dropdown"
            menu-class="dropdown-menu dropdown-menu-end dropdown-menu-animated profile-dropdown"
        >
          <template
              #button-content
              data-bs-toggle="dropdown"
              role="button"
              aria-haspopup="false"
              aria-expanded="false"
          >
            <div class="nav-link arrow-none nav-user px-2">
              <span class="account-user-avatar">
                <img
                    :src="avatarSrc"
                    alt="user-image"
                    width="32"
                    class="rounded-circle"
                />
              </span>
              <span class="d-lg-flex flex-column gap-1 d-none">
                <h5 class="my-0">{{ displayName }}</h5>
                <h6 class="my-0 fw-normal text-start">{{ displayRole }}</h6>
              </span>
            </div>
          </template>

          <b-dropdown-header class="noti-title">
            <h6 class="text-overflow m-0">Welcome !</h6>
          </b-dropdown-header>

          <b-dropdown-item href="#" class="">
            <i class="ri-account-circle-line fs-18 align-middle me-1"></i>
            <span>My Account</span>
          </b-dropdown-item>

          <b-dropdown-item href="#" class="">
            <i class="ri-settings-4-line fs-18 align-middle me-1"></i>
            <span>Settings</span>
          </b-dropdown-item>

          <b-dropdown-item href="#" class="">
            <i class="ri-customer-service-2-line fs-18 align-middle me-1"></i>
            <span>Support</span>
          </b-dropdown-item>

          <b-dropdown-item href="#" class="">
            <i class="ri-lock-password-line fs-18 align-middle me-1"></i>
            <span>Lock Screen</span>
          </b-dropdown-item>

          <b-dropdown-item @click="handleLogout">
            <i class="ri-logout-box-line fs-18 align-middle me-1"></i>
            <span>Logout</span>
          </b-dropdown-item>
        </b-nav-item-dropdown>
      </ul>
    </div>
  </div>
</template>

<script lang="ts">
import simplebar from 'simplebar-vue'
import {useLayoutStore} from "@/stores/layout";
import { useDjangoAuthStore } from '@/stores/djangoAuth'
import http from '@/lib/http'
import defaultAvatar from '@/assets/images/users/avatar-1.jpg'

type TopbarNotificationItem = {
  id: number
  text: string
  subText: string
}

function formatRelativeTime(dateStr: string): string {
  if (!dateStr) return ''
  try {
    const date = new Date(dateStr)
    const now = new Date()
    const diffMs = now.getTime() - date.getTime()
    const diffSec = Math.floor(diffMs / 1000)
    const diffMin = Math.floor(diffSec / 60)
    const diffHr = Math.floor(diffMin / 60)
    const diffDay = Math.floor(diffHr / 24)

    if (diffSec < 60) return 'Just now'
    if (diffMin < 60) return `${diffMin} min ago`
    if (diffHr < 24) return `${diffHr} hr ago`
    if (diffDay < 7) return `${diffDay} day${diffDay > 1 ? 's' : ''} ago`

    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: date.getFullYear() !== now.getFullYear() ? 'numeric' : undefined,
    })
  } catch {
    return dateStr
  }
}

export default {
  components: {simplebar},
  data() {
    let useLayout = useLayoutStore()
    return {
      useLayout,
      // Pinia Django auth store instance (initialized in src/main.ts)
      auth: useDjangoAuthStore(),
      notificationItems: [] as TopbarNotificationItem[],
      isLoadingNotifications: false,
    }
  },

  computed: {
    // Current authenticated user from the Django auth store
    currentUser(): any {
      return this.auth?.user
    },
    // Safe avatar source: user's profile picture or the default avatar
    avatarSrc(): string {
      return this.currentUser?.profile_picture || defaultAvatar
    },
    // Friendly display name using first/last/username/email fallbacks
    displayName(): string {
      const u = this.currentUser
      if (!u) return 'User'
      const full = [u.first_name, u.last_name].filter(Boolean).join(' ').trim()
      return full || u.username || u.email || 'User'
    },
    // Simple role mapping from Django flags; fallback to Member
    displayRole(): string {
      const u = this.currentUser
      if (!u) return 'Member'
      return u.is_superuser || u.is_staff ? 'Admin' : 'Member'
    },
  },
  async mounted() {
    await this.loadUnreadNotifications()
  },
  methods: {
    async loadUnreadNotifications() {
      this.isLoadingNotifications = true
      try {
        const res = await http.get('/core/notifications/unread/')
        const data = (res as any)?.data
        const rows = Array.isArray(data) ? data : (data?.results || [])

        this.notificationItems = rows.map((n: any) => {
          return {
            id: n.id,
            text: n.title || 'Notification',
            subText: formatRelativeTime(n.created_at),
          }
        })
      } catch (e) {
        console.error('Failed to load notifications:', e)
        this.notificationItems = []
      } finally {
        this.isLoadingNotifications = false
      }
    },
    async markNotificationRead(notificationId: number) {
      try {
        await http.post(`/core/notifications/${notificationId}/mark-read/`)
      } catch (e) {
        console.error('Failed to mark notification read:', e)
      } finally {
        this.notificationItems = this.notificationItems.filter((n: any) => n.id !== notificationId)
      }
    },
    async clearAllNotifications() {
      try {
        await http.post('/core/notifications/clear-all/')
      } catch (e) {
        console.error('Failed to clear notifications:', e)
      } finally {
        this.notificationItems = []
      }
    },
    goToActivity() {
      this.$router.push('/pages/activity')
    },
    toggleRightSidebar() {
      this.useLayout.isRightSidebarOpen = !this.useLayout.isRightSidebarOpen
    },
    fullScreenListener() {
      document.body.classList.toggle("fullscreen-enable");
      if (!document.fullscreenElement) {
        if (document.documentElement.requestFullscreen) {
          document.documentElement.requestFullscreen();
        }
      } else {
        if (document["exitFullscreen"]) {
          document["exitFullscreen"]();
        }
      }
    },
    /**
     * Handle user logout
     * Calls the Django auth store logout method and redirects to login page
     */
    async handleLogout() {
      try {
        // Call the Django auth store logout method (clears token, user data, etc.)
        await this.auth.logout();
        
        // Redirect to login page
        this.$router.push('/auth/login');
      } catch (error) {
        console.error('Logout error:', error);
        // Still redirect to login even if logout API call fails
        this.$router.push('/auth/login');
      }
    },
  },

}
</script>