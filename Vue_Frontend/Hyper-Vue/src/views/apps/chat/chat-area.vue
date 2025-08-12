<template>
  <div class="card">
    <div class="card-body px-0 pb-0">
      <simplebar style="max-height: 550px">
        <ul class="conversation-list px-3">
          <li
            v-for="chat of chatData"
            :key="chat.message"
            :class="{ odd: `${chat.odd}` === 'true' }"
            class="clearfix"
          >
            <div class="chat-avatar">
              <img :src="`${chat.image}`" class="rounded" alt="user-image" />
              <i>{{ chat.time }}</i>
            </div>
            <div class="conversation-text">
              <div class="ctext-wrap">
                <i>{{ chat.name }}</i>
                <p>{{ chat.message }}</p>
              </div>
              <div
                v-if="chat.file"
                class="card mt-2 mb-1 shadow-none border text-left"
              >
                <div class="p-2">
                  <b-row class="align-items-center">
                    <b-col class="col-auto">
                      <div class="avatar-sm">
                        <span class="avatar-title rounded">.ZIP</span>
                      </div>
                    </b-col>
                    <b-col class="pl-0">
                      <a
                        href="javascript:void(0);"
                        class="text-muted font-weight-bold"
                        >Hyper-admin-design.zip</a
                      >
                      <p class="mb-0">2.3 MB</p>
                    </b-col>
                    <b-col class="col-auto">
                      <!-- Button -->
                      <a
                        href="javascript:void(0);"
                        class="btn btn-link btn-lg text-muted"
                      >
                        <i class="dripicons-download"></i>
                      </a>
                    </b-col>
                  </b-row>
                </div>
              </div>
            </div>
            <b-dropdown
              menu-class
              right
              class="conversation-actions"
              toggle-class="btn-sm btn-link arrow-none"
              variant="white"
            >
              <template v-slot:button-content>
                <i class="uil uil-ellipsis-v"></i>
              </template>
              <b-dropdown-item class="mb-0" href="#"
                >Copy Message</b-dropdown-item
              >
              <b-dropdown-item class="mb-0" href="#">Edit</b-dropdown-item>
              <b-dropdown-item class="mb-0" href="#">Delete</b-dropdown-item>
            </b-dropdown>
          </li>
        </ul>
      </simplebar>

      <b-row>
        <b-col>
          <div class="mt-3 bg-light p-3 rounded">
            <form
              id="chat-form"
              class="needs-validation"
              novalidate
              name="chat-form"
            >
              <b-row>
                <b-col class="mb-2 mb-sm-0">
                  <input
                    type="text"
                    class="form-control border-0"
                    placeholder="Enter your text"
                    required
                  />
                  <div class="invalid-feedback">Please enter your messsage</div>
                </b-col>
                <b-col sm="auto" class="col-sm-auto">
                  <div class="btn-group">
                    <a href="#" class="btn btn-light">
                      <i class="uil uil-paperclip"></i>
                    </a>
                    <a href="#" class="btn btn-light">
                      <i class="uil uil-smile"></i>
                    </a>
                    <b-button
                      variant="success"
                      type="submit"
                      class="chat-send btn-block"
                    >
                      <i class="uil uil-message"></i>
                    </b-button>
                  </div>
                </b-col>
              </b-row>
            </form>
          </div>
        </b-col>
      </b-row>
    </div>
  </div>
</template>

<script lang="ts">
import simplebar from "simplebar-vue";

import avatar1 from "@/assets/images/users/avatar-1.jpg";
import avatar5 from "@/assets/images/users/avatar-5.jpg";

export default {
  components: { simplebar },
  data() {
    return {
      chatData: [
        {
          image: avatar5,
          name: "Shreyu N",
          time: "10:00",
          message: "Hello!",
        },
        {
          image: avatar1,
          name: "Dominic",
          time: "10:01",
          message: "Hi, How are you? What about our next meeting?",
          odd: "true",
        },
        {
          image: avatar5,
          name: "Shreyu N",
          time: "10:01",
          message: "Yeah everything is fine",
        },
        {
          image: avatar1,
          name: "Dominic",
          time: "10:02",
          message: "Wow that's great",
          odd: "true",
        },
        {
          image: avatar5,
          name: "Shreyu N",
          time: "10:02",
          message: "Let's have it today if you are free",
        },
        {
          image: avatar1,
          name: "Dominic",
          time: "10:03",
          message: "Sure thing! let me know if 2pm works for you",
          odd: "true",
        },
        {
          image: avatar5,
          name: "Shreyu N",
          time: "10:04",
          message:
            "Sorry, I have another meeting scheduled at 2pm. Can we have it at 3pm instead?",
        },
        {
          image: avatar5,
          name: "Shreyu N",
          time: "10:04",
          message:
            "We can also discuss about the presentation talk format if you have some extra mins",
        },
        {
          image: avatar1,
          name: "Dominic",
          time: "10:05",
          message:
            "3pm it is. Sure, let's discuss about presentation format, it would be great to finalize today. I am attaching the last year format and assets here...",
          odd: "true",
          file: true,
        },
      ],
    };
  },
};
</script>
