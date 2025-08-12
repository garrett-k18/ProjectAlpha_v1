<template>
<Layout>
    <Breadcrumb :items="items" :title="title" />

    <b-row>
        <b-col sm="12">
            <div class="text-center">
                <h3 class="">Frequently Asked Questions</h3>
                <p class="text-muted mt-3"> Nisi praesentium similique totam odio obcaecati, reprehenderit,
                    dignissimos rem temporibus ea inventore alias!<br /> Beatae animi nemo ea
                    tempora, temporibus laborum facilis ut!</p>

                <b-button class="mt-2" size="sm" variant="success"><i class="mdi mdi-email-outline me-1"></i> Email us your question</b-button>
                <b-button class="mt-2 ms-1" size="sm" variant="info"><i class="mdi mdi-twitter me-1"></i> Send us a tweet</b-button>
            </div>
        </b-col><!-- end col -->
    </b-row><!-- end row -->

    <b-row class="pt-5">
        <b-col lg="5" offset-lg="1">
            <!-- Question/Answer -->
            <div>
                <div class="faq-question-q-box">Q.</div>
                <h4 class="faq-question" data-wow-delay=".1s">What is Lorem Ipsum?</h4>
                <p class="faq-answer mb-4">Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s.</p>
            </div>

            <!-- Question/Answer -->
            <div>
                <div class="faq-question-q-box">Q.</div>
                <h4 class="faq-question">Why use Lorem Ipsum?</h4>
                <p class="faq-answer mb-4">Lorem ipsum dolor sit amet, in mea nonumes dissentias dissentiunt, pro te solet oratio iriure. Cu sit consetetur moderatius intellegam, ius decore accusamus te. Ne primis suavitate disputando nam. Mutat convenirete.</p>
            </div>

            <!-- Question/Answer -->
            <div>
                <div class="faq-question-q-box">Q.</div>
                <h4 class="faq-question">How many variations exist?</h4>
                <p class="faq-answer mb-4">Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s.</p>
            </div>

            <!-- Question/Answer -->
            <div>
                <div class="faq-question-q-box">Q.</div>
                <h4 class="faq-question" data-wow-delay=".1s">What is Lorem Ipsum?</h4>
                <p class="faq-answer mb-4">Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s.</p>
            </div>

        </b-col>
        <!--/col-md-5 -->

        <b-col lg="5">
            <!-- Question/Answer -->
            <div>
                <div class="faq-question-q-box">Q.</div>
                <h4 class="faq-question">Is safe use Lorem Ipsum?</h4>
                <p class="faq-answer mb-4">Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s.</p>
            </div>

            <!-- Question/Answer -->
            <div>
                <div class="faq-question-q-box">Q.</div>
                <h4 class="faq-question">When can be used?</h4>
                <p class="faq-answer mb-4">Lorem ipsum dolor sit amet, in mea nonumes dissentias dissentiunt, pro te solet oratio iriure. Cu sit consetetur moderatius intellegam, ius decore accusamus te. Ne primis suavitate disputando nam. Mutat convenirete.</p>
            </div>

            <!-- Question/Answer -->
            <div>
                <div class="faq-question-q-box">Q.</div>
                <h4 class="faq-question">License &amp; Copyright</h4>
                <p class="faq-answer mb-4">Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s.</p>
            </div>

            <!-- Question/Answer -->
            <div>
                <div class="faq-question-q-box">Q.</div>
                <h4 class="faq-question">Is safe use Lorem Ipsum?</h4>
                <p class="faq-answer mb-4">Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s.</p>
            </div>

        </b-col>
        <!--/col-md-5-->
    </b-row>
    <!-- end row -->

</Layout>
</template>

<script>
import Layout from '@/components/layouts/layout.vue'
import Breadcrumb from '@/components/breadcrumb.vue'
export default {
    components: { Layout, Breadcrumb },
    data() {
        return {
            title: 'FAQ',
            items: [{
                    text: 'Hyper',
                    href: '/',
                },
                {
                    text: 'Pages',
                    href: '/',
                },
                {
                    text: 'FAQ',
                    active: true,
                },
            ],
        }
    },

}
</script>
