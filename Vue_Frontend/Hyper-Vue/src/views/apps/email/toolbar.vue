<template>
  <div>
    <div class="btn-group">
      <b-button variant="secondary" >
        <i class="mdi mdi-archive font-16"></i>
      </b-button>
      <b-button variant="secondary" >
        <i class="mdi mdi-alert-octagon font-16"></i>
      </b-button>
      <b-button variant="secondary" >
        <i class="mdi mdi-delete-variant font-16"></i>
      </b-button>
    </div>

    <b-dropdown class="btn-group ms-1" toggle-class="arrow-none" variant="secondary">
      <template v-slot:button-content>
        <i class="mdi mdi-folder font-16"></i>
        <i class="mdi mdi-chevron-down"></i>
      </template>
      <span class="dropdown-header">Move to:</span>
      <b-dropdown-item href="javascript: void(0);">Social</b-dropdown-item>
      <b-dropdown-item href="javascript: void(0);">Promotions</b-dropdown-item>
      <b-dropdown-item href="javascript: void(0);">Updates</b-dropdown-item>
      <b-dropdown-item href="javascript: void(0);">Forums</b-dropdown-item>
    </b-dropdown>

    <b-dropdown class="btn-group ms-1" toggle-class="arrow-none" variant="secondary">
      <template v-slot:button-content>
        <i class="mdi mdi-label font-16"></i>
        <i class="mdi mdi-chevron-down"></i>
      </template>
      <span class="dropdown-header">Label as:</span>
      <b-dropdown-item href="javascript: void(0);">Updates</b-dropdown-item>
      <b-dropdown-item href="javascript: void(0);">Social</b-dropdown-item>
      <b-dropdown-item href="javascript: void(0);">Promotions</b-dropdown-item>
      <b-dropdown-item href="javascript: void(0);">Forums</b-dropdown-item>
    </b-dropdown>

    <b-dropdown class="btn-group ms-1" toggle-class="arrow-none" variant="secondary">
      <template v-slot:button-content>
        <i class="mdi mdi-dots-horizontal font-16"></i>
        More
        <i class="mdi mdi-chevron-down"></i>
      </template>
      <span class="dropdown-header">More Option :</span>
      <b-dropdown-item href="javascript: void(0);">Mark as Unread</b-dropdown-item>
      <b-dropdown-item href="javascript: void(0);">Add to Tasks</b-dropdown-item>
      <b-dropdown-item href="javascript: void(0);">Add Star</b-dropdown-item>
      <b-dropdown-item href="javascript: void(0);">Mute</b-dropdown-item>
    </b-dropdown>
  </div>
</template>