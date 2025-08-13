<template>
  <!--- Sidemenu -->

  <ul data-simplebar id="menu-bar" class="metismenu side-nav">
    <template v-for="item in menuItems" :key="item.name">
      <template v-if="item.header && mode !== 'horizontal'">
        <li
            :key="`item-${item.name}-header`"
            class="side-nav-title"
        >
          {{ item.header }}
        </li>
      </template>

      <li v-if="item.name"
          :key="`item-${item.name}`"
          class="side-nav-item"
      >
        <template v-if="hasItems(item)">
          <a
              href="#"
              v-b-toggle="item.icon + '-collapse'"
              class="side-nav-link">
            <i
                v-if="item.icon"
                :class="item.icon"
            ></i>
            <span>{{ item.name }}</span>
            <span v-if="!item.badge" class="menu-arrow"></span>
            <span
                v-if="item.badge"
                :class="'badge bg-' + item.badge.variant + ' float-end'">{{ item.badge.text }}</span>
          </a>
          <b-collapse :id="item.icon + '-collapse'">
            <ul class="side-nav-second-level">
              <li
                  v-for="subitem in item.children"
                  :key="`sub-item-${subitem.name}`"
                  class="side-nav-item"
              >
                <template v-if="hasItems(subitem)">
                  <a
                      href="#"
                      v-b-toggle="subitem.name + '-collapse'"
                      class="side-nav-link-ref side-sub-nav-link"
                  >
                    {{ subitem.name }}
                    <span class="menu-arrow"></span>
                  </a>
                  <b-collapse :id="subitem.name + '-collapse'">
                    <ul class="side-nav-third-level">
                      <li
                          v-for="subSubitem in subitem.children"
                          :key="`sub-sub-item-${subSubitem.name}`">

                        <template v-if="hasItems(subSubitem)">
                          <a
                              href="javascript:void(0);"
                              class="side-nav-link-ref has-arrow side-sub-nav-link"
                          >
                            {{ subSubitem.name }}
                          </a>
                          <ul
                              class="side-nav-forth-level"
                              aria-expanded="false"
                          >
                            <li
                                v-for="subSubitemChild in subSubitem.children"
                                :key="`sub-sub-sub-item-${subSubitemChild.name}`"
                            >
                              <router-link
                                  tag="a"
                                  :to="`${item.path}/${subitem.path}/${subSubitem.path}/${subSubitemChild.path}`"
                                  class="side-sub-nav-link side-nav-link-ref"
                              >{{ subSubitemChild.name }}
                              </router-link>

                            </li>
                          </ul>
                        </template>

                        <template v-else>
                          <router-link
                              tag="a"
                              :to="`${item.path}/${subitem.path}/${subSubitem.path}`"
                              class="side-sub-nav-link side-nav-link-ref"
                          >{{ subSubitem.name }}
                          </router-link>

                        </template>
                      </li>
                    </ul>
                  </b-collapse>
                </template>

                <template v-else>
                  <router-link
                      tag="a"
                      :to="`${item.path}/${subitem.path}`"
                      class="side-sub-nav-link side-nav-link-ref"
                  >{{ subitem.name }}
                  </router-link>

                </template>
              </li>
            </ul>
          </b-collapse>
        </template>

        <template v-else>
          <router-link
              tag="a"
              :to="`${item.path}`"
              class="side-nav-link side-nav-link-ref"
          >
            <i
                v-if="item.icon"
                :class="item.icon"
            ></i>
            <span>{{ item.name }}</span>
            <span
                v-if="item.badge"
                :class="'badge bg-' + item.badge.variant + ' float-end'">{{ item.badge.text }}</span>
          </router-link>
        </template>

      </li>
    </template>
  </ul>
</template>

<script lang="ts">
import {authProtectedRoutes} from "@/router/routes";

import {MetisMenu} from 'metismenujs';

export default {
  components: {},
  props: {
    mode: {
      type: String,
      default: 'vertical',
    },
  },
  data() {
    return {
      menuItems: authProtectedRoutes,
      menuRef: null,
    }
  },

  mounted: function () {
    // eslint-disable-next-line no-unused-vars

    if (this.mode === 'horizontal') {
      const menuRef = new MetisMenu('#menu-bar').on('shown.metisMenu', function (
          event
      ) {
        window.addEventListener('click', function menuClick(e) {
          if (!event.target.contains(e.target)) {
            menuRef.hide(event.detail.shownElement)
            window.removeEventListener('click', menuClick)
          }
        })
      })
      this.menuRef = menuRef
    } else {
      this.menuRef = new MetisMenu('#menu-bar')
    }

    const activeClass = this.mode === 'horizontal' ? 'active' : 'show'
    const dropdownActiveClass =
        this.mode === 'horizontal' ? 'active' : 'menuitem-active'
    this.activateMenuItems(activeClass, dropdownActiveClass)
  },
  methods: {
    /**
     * Returns true or false if given menu item has child or not
     * @param item menuItem
     */
    hasItems(item) {
      return item && item.children !== undefined
          ? item.children.length > 0
          : false
    },

    /**
     * Activate menu items
     */
    activateMenuItems(activeClass, dropdownActiveClass) {
      const links = document.getElementsByClassName('side-nav-link-ref')

      let menuItemEl = null
      // tslint:disable-next-line: prefer-for-of
      for (let i = 0; i < links.length; i++) {
        // tslint:disable-next-line: no-string-literal
        if (window.location.pathname === links[i]['pathname']) {
          menuItemEl = links[i]
          break
        }
      }

      if (menuItemEl) {
        menuItemEl.classList.add('active')
        const parentEl = menuItemEl.parentElement

        if (parentEl) {
          parentEl.classList.add(activeClass,dropdownActiveClass)

          const parent2El = parentEl.parentElement
          if (parent2El) {
            parent2El.classList.add(dropdownActiveClass)
          }

          const parent3El = parent2El.parentElement
          if (parent3El) {
            parent3El.classList.add(activeClass)

            if (parent3El.classList.contains('side-nav-item')) {
              const firstAnchor = parent3El.querySelector(
                  '.side-nav-link-a-ref'
              )

              if (firstAnchor) {
                firstAnchor.classList.add('active')
              }
            }

            const parent4El = parent3El.parentElement
            if (parent4El) {
              parent4El.classList.add(dropdownActiveClass)

              const parent5El = parent4El.parentElement
              if (parent5El) {
                parent5El.classList.add(activeClass)

                const parent6El = parent5El.parentElement
                if (parent6El) {
                  parent6El.classList.add(dropdownActiveClass)

                  const parent7El = parent6El.parentElement
                  if (parent7El) {
                    parent7El.classList.add(activeClass)
                  }
                }
              }
            }
          }
        }
      }
    },
  },
}
</script>
