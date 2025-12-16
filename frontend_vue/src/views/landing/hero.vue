<template>
<!-- START HERO -->
<!-- WHAT: Hero section for ProjectAlpha landing page
     WHY: First impression section that introduces the platform and value proposition
     WHERE: Top of landing page, immediately visible to visitors -->
<section class="hero-section">
    <b-container>
        <b-row class="align-items-center">
            <b-col md="5">
                <div class="mt-md-4">
                    <div>
                        <b-badge pill variant="success" class="font-13">Platform</b-badge>
                        <span class="text-white-50 ms-1">Comprehensive Real Estate Asset Management</span>
                    </div>
                    <h2 class="text-white fw-normal mb-4 mt-3 lh-base">
                        ProjectAlpha - Complete Real Estate Investment & Asset Management Platform
                    </h2>

                    <p class="mb-4 font-16 text-white-50">Streamline your real estate operations with our integrated platform for acquisition analysis, asset management, portfolio reporting, and CRM. Built for investors, asset managers, and trading partners.</p>

                    <router-link to="/login" class="btn btn-lg font-16 btn-success">Get Started <i class="mdi mdi-arrow-right ms-1"></i></router-link>
                    <a href="#features" class="btn btn-lg font-16 btn-info ms-1">Learn More</a>
                </div>
            </b-col>
            <b-col md="5" offset-md="2">
                <div class="text-md-end mt-3 mt-md-0">
                    <img src="@/assets/images/svg/startup.svg" alt="ProjectAlpha Platform" class="img-fluid" />
                </div>
            </b-col>
        </b-row>
    </b-container>
</section>
<!-- END HERO -->
</template>

<script>
export default {
 name: 'Hero'
}
</script>