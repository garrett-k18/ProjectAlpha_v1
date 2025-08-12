<template>
  <CustomSyntax title="Colored Header Modals">
    <template v-slot:sub-text>
      A rendered modal with header having contexual background color.
    </template>
    <template v-slot:preview>
      <b-modal v-model="coloredHeaderModal" body-class="p-0" header-class="p-0" hide-header hide-footer>
        <div class="modal-header modal-colored-header" :class="headerClass">
          <h4 class="modal-title" id="primary-header-modalLabel">
            Modal Heading
          </h4>
          <button class="btn-close btn-close-white" @click="coloredHeaderModal = !coloredHeaderModal"></button>
        </div>

        <div class="modal-body">
          <h5 class="mt-0">Primary Background</h5>
          <p>
            Cras mattis consectetur purus sit amet fermentum. Cras justo
            odio, dapibus ac facilisis in, egestas eget quam. Morbi leo
            risus, porta ac consectetur ac, vestibulum at eros.
          </p>
          <p>
            Praesent commodo cursus magna, vel scelerisque nisl
            consectetur et. Vivamus sagittis lacus vel augue laoreet
            rutrum faucibus dolor auctor.
          </p>
        </div>
        <div class="modal-footer">
          <b-button variant="light" @click="coloredHeaderModal = !coloredHeaderModal">
            Close
          </b-button>
          <b-button :variant="buttonVariant">
            Save changes
          </b-button>
        </div>
      </b-modal>

      <div class="d-flex flex-wrap gap-2">
        <b-button variant="primary" @click="openModal('primary')"> Primary Header</b-button>
        <b-button variant="success" @click="openModal('success')"> Success Header</b-button>
        <b-button variant="info" @click="openModal('info')"> Info Header</b-button>
        <b-button variant="warning" @click="openModal('warning')"> Warning Header</b-button>
        <b-button variant="danger" @click="openModal('danger')"> Danger Header</b-button>
        <b-button variant="dark" @click="openModal('dark')"> Dark Header</b-button>
      </div>
    </template>
  </CustomSyntax>
</template>

<script lang="ts">
import CustomSyntax from '@/components/custom/custom-syntax.vue'

export default {
  components: {CustomSyntax},
  data() {
    return {
      coloredHeaderModal: false,
      buttonVariant: '',
      headerClass: '',
    }
  },
  methods: {
    openModal(color: string) {
      this.coloredHeaderModal = true
      this.buttonVariant = color
      this.headerClass = 'bg-' + color
    },
  },
}
</script>
