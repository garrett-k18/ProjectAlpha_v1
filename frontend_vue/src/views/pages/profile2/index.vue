<template>
<Layout>
    <Breadcrumb :items="items" :title="title" />
    <b-row>
        <b-col xl="4" lg="5">
            <Profile />

            <!-- Messages-->
            <Message />
        </b-col> <!-- end col-->

        <b-col xl="8" lg="7">
            <b-card>
                <b-tabs content-class="mt-3" pills justified nav-class="bg-nav-pills">
                    <b-tab title="About" title-link-class="rounded-0">
                        <About />
                    </b-tab>
                    <b-tab active title="Timeline" title-link-class="rounded-0">
                        <Timeline />
                    </b-tab>
                    <b-tab title="Settings" title-link-class="rounded-0">
                        <Settings />
                    </b-tab>
                </b-tabs>
                <!-- end card-body -->
            </b-card>
        </b-col> <!-- end col -->
    </b-row>
</Layout>
<!-- end row-->
</template>

<script lang="ts">
import Layout from '@/components/layouts/layout.vue'
import Breadcrumb from '@/components/breadcrumb.vue'
import Profile from './profile.vue'
import About from './about.vue'
import Timeline from './timeline.vue'
import Settings from './setting.vue'
import Message from './message.vue'
export default {
    components: { Layout, Breadcrumb, Profile, About, Timeline, Settings, Message },
    data() {
        return {
            title: 'Profile 2',
            items: [{
                    text: 'Hyper',
                    href: '/',
                },
                {
                    text: 'Pages',
                    href: '/',
                },
                {
                    text: 'Profile 2',
                    active: true,
                },
            ],
        }
    },
}
</script>
