<template>
<div>
    <!-- Pre-loader -->
    <div id="preloader" v-if="isLoading">
        <div id="status">
            <div class="bouncing-loader">
                <div></div>
                <div></div>
                <div></div>
            </div>
        </div>
    </div>
    <!-- End Preloader -->
    <CRM />
</div>
</template>

<script lang="ts">
import Layout from "@/components/layouts/layout.vue";
import Breadcrumb from '@/components/breadcrumb.vue';
import CRM from '@/views/dashboards/crm/index.vue'

export default {
    components: { Layout, Breadcrumb, CRM },
    data() {
        const isLoading = true;
        return {
            isLoading,
        }
    },
    mounted() {
        setTimeout(() => {
            this.isLoading = false;
        }, 1500);
    },
}
</script>
