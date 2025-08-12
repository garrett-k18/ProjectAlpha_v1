<template>
  <div class="card d-block">
    <div class="card-body">
      <div class="d-flex justify-content-between align-items-center mb-2">
        <h3 class="mt-0">App design and development</h3>
        <b-dropdown class="float-end" toggle-class="arrow-none card-drop p-0" variant="black" right>
          <template v-slot:button-content>
            <i class="ri-more-fill"></i>
          </template>
          <b-dropdown-item href="javascript:void(0);">
            <i class="mdi mdi-pencil me-1"></i>Edit
          </b-dropdown-item>
          <b-dropdown-item href="javascript:void(0);">
            <i class="mdi mdi-delete me-1"></i>Delete
          </b-dropdown-item>
          <b-dropdown-item href="javascript:void(0);">
            <i class="mdi mdi-email-outline me-1"></i>Invite
          </b-dropdown-item>
          <b-dropdown-item href="javascript:void(0);">
            <i class="mdi mdi-exit-to-app me-1"></i>Leave
          </b-dropdown-item>
        </b-dropdown>
      </div>
      <div class="badge text-bg-secondary mb-3">Ongoing</div>

      <h5>Project Overview:</h5>

      <p class="text-muted mb-2">
        With supporting text below as a natural lead-in to additional contenposuere erat a ante. Voluptates, illo, iste
        itaque voluptas
        corrupti ratione reprehenderit magni similique? Tempore, quos delectus asperiores libero voluptas quod
        perferendis! Voluptate,
        quod illo rerum? Lorem ipsum dolor sit amet.
      </p>

      <p class="text-muted mb-4">
        Voluptates, illo, iste itaque voluptas corrupti ratione reprehenderit magni similique? Tempore, quos delectus
        asperiores
        libero voluptas quod perferendis! Voluptate, quod illo rerum? Lorem ipsum dolor sit amet. With supporting text
        below
        as a natural lead-in to additional contenposuere erat a ante.
      </p>

      <b-row>
        <b-col md="4">
          <div class="mb-4">
            <h5>Start Date</h5>
            <p>
              17 March 2018
              <small class="text-muted">1:00 PM</small>
            </p>
          </div>
        </b-col>
        <b-col md="4">
          <div class="mb-4">
            <h5>End Date</h5>
            <p>
              22 December 2018
              <small class="text-muted">1:00 PM</small>
            </p>
          </div>
        </b-col>
        <b-col md="4">
          <div class="mb-4">
            <h5>Budget</h5>
            <p>$15,800</p>
          </div>
        </b-col>
      </b-row>

      <div>
        <h5>Team Members:</h5>
        <a v-b-tooltip.top href="javascript:void(0);" title="Mat Helme" class="d-inline-block">
          <img
              src="@/assets/images/users/avatar-6.jpg"
              class="rounded-circle img-thumbnail avatar-sm"
              alt="friend"
          />
        </a>

        <a
            v-b-tooltip.top
            href="javascript:void(0);"
            title="Michael Zenaty"
            class="d-inline-block ms-1"
        >
          <img
              src="@/assets/images/users/avatar-7.jpg"
              class="rounded-circle img-thumbnail avatar-sm"
              alt="friend"
          />
        </a>

        <a
            v-b-tooltip.top
            href="javascript:void(0);"
            title="James Anderson"
            class="d-inline-block ms-1"
        >
          <img
              src="@/assets/images/users/avatar-8.jpg"
              class="rounded-circle img-thumbnail avatar-sm"
              alt="friend"
          />
        </a>

        <a v-b-tooltip.top href="javascript:void(0);" title="Mat Helme" class="d-inline-block ms-1">
          <img
              src="@/assets/images/users/avatar-4.jpg"
              class="rounded-circle img-thumbnail avatar-sm"
              alt="friend"
          />
        </a>

        <a
            v-b-tooltip.top
            href="javascript:void(0);"
            title="Michael Zenaty"
            class="d-inline-block ms-1"
        >
          <img
              src="@/assets/images/users/avatar-5.jpg"
              class="rounded-circle img-thumbnail avatar-sm"
              alt="friend"
          />
        </a>

        <a
            v-b-tooltip.top
            href="javascript:void(0);"
            title="James Anderson"
            class="d-inline-block ms-1"
        >
          <img
              src="@/assets/images/users/avatar-3.jpg"
              class="rounded-circle img-thumbnail avatar-sm"
              alt="friend"
          />
        </a>
      </div>
    </div>
    <!-- end card-body-->
  </div>
</template>

<script lang="ts">
</script>