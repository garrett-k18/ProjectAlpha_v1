<template>
  <div class="card">

      <div class="card-header d-flex justify-content-between align-items-center">
      <h4 class="header-title">{{ title }}</h4>
      <b-dropdown class="float-end" right variant="white" toggle-class="arrow-none card-drop p-0">
        <template v-slot:button-content>
          <i class="mdi mdi-dots-vertical"></i>
        </template>
        <b-dropdown-item href="javascript:void(0);">Settings</b-dropdown-item>
        <b-dropdown-item href="javascript:void(0);">Action</b-dropdown-item>
      </b-dropdown>
      </div>

      <div class="card-body pt-0">
      <div class="inbox-widget">
        <div v-for="message in messages" :key="message.name" class="inbox-item">
          <div class="inbox-item-img">
            <img :src="`${message.image}`" class="rounded-circle" alt />
          </div>
          <p class="inbox-item-author">{{ message.name }}</p>
          <p class="inbox-item-text">{{ message.message }}</p>
          <p class="inbox-item-date">
            <a href="javascript:(0);" class="btn btn-sm btn-link text-info font-13">Reply</a>
          </p>
        </div>
      </div>
      <!-- end inbox-widget -->
    </div>
    </div>
    <!-- end card-body -->
  <!-- end card -->
</template>

<script lang="ts">
/**
 * Messages-widget component
 * 1. User specifies the title of window using the 'title' input property.
 * 2. Messages array specify the profile of id, image, name, message, time.
 *     id - Specify the unique id of messages.
 *     image - Specify the profile of user.
 *     name - Specify the name of chat user.
 *     message - User chat message specify using message.
 *     time - Message receive time specify using time.
 */
export default {
  props: {
    title: {
      type: String,
      default: 'Messages',
    },
    messages: {
      type: Array,
      default: function() {
        return []
      },
    },
  },
}
</script>