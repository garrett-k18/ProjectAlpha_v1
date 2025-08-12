<template>
  <div class="card">
    <div class="card-header d-flex justify-content-between align-items-center">
      <h4 class="mb-3 header-title">{{ title }}</h4>
      <b-dropdown variant="white" class="float-end" toggle-class="arrow-none card-drop p-0" right>
        <template v-slot:button-content>
          <i class="mdi mdi-dots-vertical"></i>
        </template>
        <b-dropdown-item href="javascript:void(0);" >Settings</b-dropdown-item>
        <b-dropdown-item href="javascript:void(0);" >Action</b-dropdown-item>
      </b-dropdown>
    </div>

    <div class="chat-conversation">
      <simplebar class="card-body py-0 mb-3" :style="`max-height:${chatWindowHeight}`">

        <ul class="conversation-list">
          <li
              v-for="(chat, index) in chatMessages"
              :key="chat.id"
              :class="{ odd: index % 2 }"
              class="clearfix"
          >
            <div class="chat-avatar">
              <img :src="`${chat.image}`" alt="male"/>
              <i>{{ chat.time }}</i>
            </div>
            <div class="conversation-text">
              <div class="ctext-wrap">
                <i>{{ chat.name }}</i>
                <p>{{ chat.message }}</p>
              </div>
            </div>
          </li>
        </ul>

      </simplebar>
    </div>
      <b-form @submit.prevent="saveMessage">
        <b-row class="p-3 pt-0">
          <b-col>
            <input
                id="message"
                v-model="chats.message"
                type="text"
                class="form-control"
                placeholder="Enter your text"
                name="message"
                :class="{ 'is-invalid': submitform && $v.chats.message.$error }"
            />
            <div
                v-if="submitform && !$v.chats.message.required"
                class="invalid-feedback"
            >This value is required.
            </div>
          </b-col>

          <b-col class="col-auto d-grid">
            <button type="submit" class="btn btn-danger chat-send">Send</button>
          </b-col>
        </b-row>
        <!-- end row -->
      </b-form>
      <!-- end form -->

  </div>

</template>
<script lang="ts">
import simplebar from 'simplebar-vue'
// import { required } from 'vuelidate/lib/validators'
import avatar5 from '@/assets/images/users/avatar-5.jpg'

/**
 * Chat list - Renders a chat list with a form to enter new message
 * 1. User specifies the title of window using the 'title' input property.
 * 2. Window height set using the 'chatWindowHeight' input property. Height would count in pixel.
 * 3. Messages array specify the id, image, name, message, time.
 *     id - specify the unique id of chat message.
 *     image - Specify the profile of user.
 *     name - Specify the name of chat user.
 *     message - User chat message specify using message.
 *     time - Message sended time specify using time.
 */
export default {
  components: {simplebar},
  props: {
    title: {
      type: String,
      default: 'Chat',
    },
    chatWindowHeight: {
      type: String,
      default: '200',
    },
    chatMessages: {
      type: Array,
      default: function () {
        return []
      },
    },
  },
  data() {
    return {
      chats: {
        message: '',
      },
      submitform: false,
    }
  },
  // validations: {
  //   chats: {
  //     message: { required },
  //   },
  // },
  methods: {
    /**
     * Chat form submit
     */
    saveMessage() {
      this.submitform = true

      // stop here if form is invalid
      this.$v.$touch()
      if (this.$v.$invalid) {
        return
      } else {
        var id = this.chatMessages.length
        const message = this.chats.message
        const currentDate = new Date()

        // Message Push in Chat
        this.chatMessages.push({
          image: avatar5,
          id: id + 1,
          name: 'Smith',
          message,
          time: currentDate.getHours() + ':' + currentDate.getMinutes(),
        })
      }
      this.submitform = false
      this.chats = {}
    },
  },
}
</script>
