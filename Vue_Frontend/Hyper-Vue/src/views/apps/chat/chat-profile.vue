<template>
  <div class="card">
    <div class="card-body">
        <b-dropdown class="float-end" toggle-class="arrow-none card-drop p-0" variant="white" right>
          <template v-slot:button-content>
            <i class="mdi mdi-dots-horizontal"></i>
          </template>
          <b-dropdown-itema href="javascript:void(0);">View full</b-dropdown-itema>
          <b-dropdown-item href="javascript:void(0);">Edit Contact Info</b-dropdown-item>
          <b-dropdown-item href="javascript:void(0);">Remove</b-dropdown-item>
        </b-dropdown>


      <div class="mt-3 text-center">
        <img
            src="@/assets/images/users/avatar-5.jpg"
            alt="shreyu"
            class="img-thumbnail avatar-lg rounded-circle"
        />
        <h4>Shreyu N</h4>
        <b-button variant="primary" size="sm" class="mt-1">
          <i class="uil uil-envelope-add me-1"></i>Send Email
        </b-button>
        <p class="text-muted mt-2 font-14">
          Last Interacted:
          <strong>Few hours back</strong>
        </p>
      </div>

      <div class="mt-3">
        <hr class/>

        <p class="mt-3 mb-1">
          <strong>
            <i class="uil uil-at"></i> Email:
          </strong>
        </p>
        <p>support@coderthemes.com</p>

        <p class="mt-3 mb-1">
          <strong>
            <i class="uil uil-phone"></i> Phone Number:
          </strong>
        </p>
        <p>+1 456 9595 9594</p>

        <p class="mt-3 mb-1">
          <strong>
            <i class="uil uil-location"></i> Location:
          </strong>
        </p>
        <p>California, USA</p>

        <p class="mt-3 mb-1">
          <strong>
            <i class="uil uil-globe"></i> Languages:
          </strong>
        </p>
        <p>English, German, Spanish</p>

        <p class="mt-3 mb-2">
          <strong>
            <i class="uil uil-users-alt"></i> Groups:
          </strong>
        </p>
        <p class="mb-1">
          <span class="badge badge-success-lighten p-1 font-14">Work</span>
          <span class="badge badge-primary-lighten p-1 font-14 ml-1">Friends</span>
        </p>
      </div>
    </div>
    <!-- end card-body -->
  </div>
  <!-- end card-->
</template>