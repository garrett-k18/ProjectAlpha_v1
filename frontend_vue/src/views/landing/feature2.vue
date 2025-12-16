<template>
<!-- START FEATURES 2 -->
<!-- WHAT: Additional feature highlights with visual elements
     WHY: Showcases platform capabilities with detailed descriptions
     WHERE: Landing page, after feature1 section -->
<section class="py-5">
    <b-container>
        <b-row>
            <b-col lg="12">
                <div class="text-center">
                    <h1 class="mt-0"><i class="mdi mdi-heart-multiple-outline"></i></h1>
                    <h3>Features you'll <span class="text-danger">love</span></h3>
                    <p class="text-muted mt-2">ProjectAlpha is built with modern technology and best practices to deliver
                        <br />a powerful, intuitive experience for real estate professionals
                    </p>
                </div>
            </b-col>
        </b-row>
        <b-row class="mt-2 py-5 align-items-center">
            <b-col lg="5" md="6">
                <img src="@/assets/images/svg/features-1.svg" class="img-fluid" alt="ProjectAlpha Features">
            </b-col>
            <b-col lg="6" offset-md="1" md="5">
                <h3 class="fw-normal">Comprehensive Real Estate Platform</h3>
                <p class="text-muted mt-3">ProjectAlpha provides everything you need to manage your real estate investments from acquisition through disposition. Our integrated modules work together seamlessly to streamline your operations.</p>

                <div class="mt-4">
                    <p class="text-muted"><i class="mdi mdi-circle-medium text-primary"></i> Acquisition Module with Loan-Level Analysis</p>
                    <p class="text-muted"><i class="mdi mdi-circle-medium text-primary"></i> Asset Management & Portfolio Tracking</p>
                    <p class="text-muted"><i class="mdi mdi-circle-medium text-primary"></i> Advanced Reporting & Analytics</p>
                    <p class="text-muted"><i class="mdi mdi-circle-medium text-primary"></i> Integrated CRM for Trading Partners</p>
                </div>

                <router-link to="/login" class="btn btn-primary rounded-pill mt-3">Get Started <i class="mdi mdi-arrow-right ms-1"></i></router-link>

            </b-col>
        </b-row>

        <b-row class="pb-3 pt-5 align-items-center">
            <b-col lg="6" md="5">
                <h3 class="fw-normal">Modern Technology Stack</h3>
                <p class="text-muted mt-3">Built with Vue.js, Django REST Framework, and PostgreSQL for reliability and performance. Our platform is designed to scale with your business and integrate with your existing workflows.</p>

                <div class="mt-4">
                    <p class="text-muted"><i class="mdi mdi-circle-medium text-success"></i> Responsive design for desktop and mobile</p>
                    <p class="text-muted"><i class="mdi mdi-circle-medium text-success"></i> Secure authentication and data protection</p>
                    <p class="text-muted"><i class="mdi mdi-circle-medium text-success"></i> RESTful API for integrations</p>
                    <p class="text-muted"><i class="mdi mdi-circle-medium text-success"></i> Real-time data updates and synchronization</p>
                </div>

                <a href="#contact" class="btn btn-success rounded-pill mt-3">Contact Us <i class="mdi mdi-arrow-right ms-1"></i></a>

            </b-col>
            <b-col lg="5" md="6" offset-md="1">
                <img src="@/assets/images/svg/features-2.svg" class="img-fluid" alt="ProjectAlpha Technology">
            </b-col>
        </b-row>
    </b-container>
</section>
<!-- END FEATURES 2 -->
</template>
