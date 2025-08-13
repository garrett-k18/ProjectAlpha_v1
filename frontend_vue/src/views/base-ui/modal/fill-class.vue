<template>
<CustomSyntax title="Filled Modals">
    <template v-slot:sub-text>
        A rendered modal with header, body and footer having contexual background color.
    </template>
    <template v-slot:preview>
        <b-modal v-model="filledModal" body-class="p-0" hide-footer hide-header>
            <div class="modal-filled" :class="modalFillClass">
                <div class="modal-header">
                    <h4 class="modal-title">
                        Primary Filled Modal
                    </h4>
                    <button class="btn-close btn-close-white" @click="filledModal = !filledModal"></button>
                </div>
                <div class="modal-body">

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
                    <b-button variant="light" @click="filledModal = !filledModal"> Close </b-button>
                    <b-button variant="outline-light"> Save changes </b-button>
                </div>
            </div>
        </b-modal>

        <div class="d-flex flex-wrap gap-2">
            <!-- Primary header modal -->
            <b-button variant="primary" @click="openModal1('primary')"> Primary Filled </b-button>
            <!-- Success header modal -->
            <b-button variant="success" @click="openModal1('success')"> Success Filled</b-button>
            <!-- Info header modal -->
            <b-button variant="info" @click="openModal1('info')"> Info Filled</b-button>
            <!-- Warning header modal -->
            <b-button variant="warning" @click="openModal1('warning')">Warning Filled</b-button>
            <!-- Danger header modal -->
            <b-button variant="danger" @click="openModal1('danger')"> Danger Filled </b-button>
            <!-- Dark header modal -->
            <b-button variant="dark" @click="openModal1('dark')"> Dark Filled</b-button>
        </div>
    </template>
</CustomSyntax>
</template>

<script lang="ts">
import CustomSyntax from '@/components/custom/custom-syntax.vue'
export default {
    components: { CustomSyntax },
    data() {
        return {
            filledModal: false,
            modalFillClass: ''
        }
    },
    methods: {
        openModal1(color: string) {
            this.filledModal = true
            this.modalFillClass = 'bg-' + color
        }
    },
}
</script>
