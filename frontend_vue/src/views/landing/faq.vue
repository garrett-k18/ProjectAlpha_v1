<template>
<!-- START FAQ -->
<!-- WHAT: Frequently asked questions section
     WHY: Addresses common questions about ProjectAlpha platform
     WHERE: Landing page, after pricing section -->
<section id="faq" class="py-5">
    <b-container>
        <b-row>
            <b-col lg="12">
                <div class="text-center">
                    <h1 class="mt-0"><i class="mdi mdi-frequently-asked-questions"></i></h1>
                    <h3>Frequently Asked <span class="text-primary">Questions</span></h3>
                    <p class="text-muted mt-2">Here are some common questions about ProjectAlpha. For more
                        <br>information please contact us.</p>

                    <a href="#contact" class="btn btn-success btn-sm mt-2"><i class="mdi mdi-email-outline me-1"></i> Email us your question</a>
                </div>
            </b-col>
        </b-row>

        <b-row class="mt-5">
            <b-col lg="5" offset-lg="1">
                <!-- Question/Answer -->
                <div>
                    <div class="faq-question-q-box">Q.</div>
                    <h4 class="faq-question text-body">What types of real estate assets does ProjectAlpha support?</h4>
                    <p class="faq-answer mb-4 pb-1 text-muted">ProjectAlpha supports residential and commercial real estate assets including single-family, multi-family, and commercial properties. The platform handles loan-level data, property details, and financial analysis for all asset types.</p>
                </div>

                <!-- Question/Answer -->
                <div>
                    <div class="faq-question-q-box">Q.</div>
                    <h4 class="faq-question text-body">Can I import data from my existing systems?</h4>
                    <p class="faq-answer mb-4 pb-1 text-muted">Yes, ProjectAlpha includes ETL tools for importing data from multiple sources including Excel, CSV files, Outlook emails, and other common formats. Our data import system handles validation and mapping automatically.</p>
                </div>

                <!-- Question/Answer -->
                <div>
                    <div class="faq-question-q-box">Q.</div>
                    <h4 class="faq-question text-body">Does ProjectAlpha integrate with other software?</h4>
                    <p class="faq-answer mb-4 pb-1 text-muted">ProjectAlpha provides a RESTful API for integrations and includes built-in SharePoint integration for document management. We can work with you to integrate with your existing systems and workflows.</p>
                </div>

            </b-col>
            <!--/col-lg-5 -->

            <b-col lg="5">
                <!-- Question/Answer -->
                <div>
                    <div class="faq-question-q-box">Q.</div>
                    <h4 class="faq-question text-body">How secure is my data?</h4>
                    <p class="faq-answer mb-4 pb-1 text-muted">Security is a top priority. ProjectAlpha uses secure authentication, encrypted data transmission, and role-based access controls. All data is stored securely in PostgreSQL databases with regular backups and monitoring.</p>
                </div>

                <!-- Question/Answer -->
                <div>
                    <div class="faq-question-q-box">Q.</div>
                    <h4 class="faq-question text-body">What kind of reporting is available?</h4>
                    <p class="faq-answer mb-4 pb-1 text-muted">ProjectAlpha provides comprehensive reporting by trade, status, fund, and entity. Reports include portfolio summaries, financial metrics, asset performance, and custom dashboards. All reports can be exported and customized for your needs.</p>
                </div>

                <!-- Question/Answer -->
                <div>
                    <div class="faq-question-q-box">Q.</div>
                    <h4 class="faq-question text-body">Is training and support included?</h4>
                    <p class="faq-answer mb-4 pb-1 text-muted">Yes, we provide onboarding training, documentation, and ongoing support. Support levels vary by plan, with enterprise customers receiving dedicated support and priority assistance.</p>
                </div>

            </b-col>
            <!--/col-lg-5-->
        </b-row>
        <!-- end row -->

    </b-container> <!-- end container-->
</section>
<!-- END FAQ -->
</template>
