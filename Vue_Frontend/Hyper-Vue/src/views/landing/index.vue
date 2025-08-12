<template>
<DefaultLayout>

    <Navbar />
    <Hero />
    <Services />

    <Feature1 />
    <Feature2 />

    <pricing />
    <Faq />
    <Contact />

    <Footer />

</DefaultLayout>
</template>

<script lang="ts">
import DefaultLayout from "@/components/layouts/default-layout.vue";
import Footer from "@/views/landing/footer.vue";
import Navbar from './navbar.vue';
import Hero from './hero.vue';
import Services from './services.vue';
import Feature1 from './feature1.vue';
import Feature2 from './feature2.vue';
import Pricing from './pricing.vue';
import Faq from './faq.vue';
import Contact from './contact.vue';

export default {
    components: { Footer, DefaultLayout, Navbar, Hero, Services, Feature1, Feature2, Pricing, Faq, Contact }
}
</script>
