<template>
<!-- START FEATURES 1 -->
<!-- WHAT: Feature showcase section with carousel highlighting key platform capabilities
     WHY: Demonstrates specific features with screenshots and detailed bullet points in an interactive carousel
     WHERE: Landing page, after services section -->
<section id="features" class="py-5 bg-light-lighten border-top border-bottom border-light">
    <b-container>
        <b-row>
            <b-col lg="12">
                <div class="text-center">
                    <h3>Powerful <span class="text-primary">Features</span> for Real Estate Professionals</h3>
                    <p class="text-muted mt-2">ProjectAlpha provides everything you need to manage your real estate investments
                        <br />from acquisition to disposition in one integrated platform.</p>
                </div>
            </b-col>
        </b-row>

        <!-- Feature Carousel -->
        <b-row class="mt-4">
            <b-col lg="12">
                <div class="feature-carousel-wrapper">
                    <b-carousel 
                        v-model="currentSlide" 
                        :interval="0" 
                        controls 
                        indicators 
                        class="feature-carousel"
                        @sliding-start="onSlideStart">
                    
                    <!-- Feature 1: Acquisition Analysis -->
                    <b-carousel-slide>
                        <b-row class="align-items-center py-4">
                            <b-col lg="6" md="6" class="order-2 order-lg-1">
                                <div class="pe-lg-4">
                                    <div class="d-flex align-items-center mb-3">
                                        <div class="avatar-lg me-3">
                                            <span class="avatar-title bg-primary-lighten rounded-circle">
                                                <i class="mdi mdi-chart-line text-primary font-32"></i>
                                            </span>
                                        </div>
                                        <h3 class="mb-0">Acquisition Analysis</h3>
                                    </div>
                                    <p class="text-muted mb-4">Comprehensive acquisition analysis tools for evaluating real estate opportunities with detailed financial modeling, due diligence tracking, and investment decision support.</p>
                                    <ul class="list-unstyled feature-bullets">
                                        <li class="mb-3">
                                            <i class="mdi mdi-check-circle text-success me-2"></i>
                                            <strong>Due Diligence Tracking:</strong> Systematic tracking of all due diligence items, documents, and requirements throughout the acquisition process
                                        </li>
                                        <li class="mb-3">
                                            <i class="mdi mdi-check-circle text-success me-2"></i>
                                            <strong>Financial Modeling:</strong> Advanced financial models with ROI, IRR, NPV calculations, cash flow projections, and sensitivity analysis
                                        </li>
                                        <li class="mb-3">
                                            <i class="mdi mdi-check-circle text-success me-2"></i>
                                            <strong>Loan-Level Analysis:</strong> Detailed property and loan information including terms, balances, rates, and payment schedules
                                        </li>
                                        <li class="mb-3">
                                            <i class="mdi mdi-check-circle text-success me-2"></i>
                                            <strong>Assumptions Management:</strong> Configurable assumptions for property types, HOA fees, foreclosure timelines, and market conditions
                                        </li>
                                    </ul>
                                </div>
                            </b-col>
                            <b-col lg="6" md="6" class="order-1 order-lg-2">
                                <div class="text-center">
                                    <img 
                                        src="@/assets/images/svg/features-1.svg" 
                                        alt="Acquisition Analysis" 
                                        class="img-fluid rounded shadow-lg"
                                        style="max-height: 500px;" />
                                </div>
                            </b-col>
                        </b-row>
                    </b-carousel-slide>

                    <!-- Feature 2: Asset Management -->
                    <b-carousel-slide>
                        <b-row class="align-items-center py-4">
                            <b-col lg="6" md="6" class="order-2 order-lg-2">
                                <div class="text-center">
                                    <img 
                                        src="@/assets/images/svg/features-2.svg" 
                                        alt="Asset Management" 
                                        class="img-fluid rounded shadow-lg"
                                        style="max-height: 500px;" />
                                </div>
                            </b-col>
                            <b-col lg="6" md="6" class="order-1 order-lg-1">
                                <div class="ps-lg-4">
                                    <div class="d-flex align-items-center mb-3">
                                        <div class="avatar-lg me-3">
                                            <span class="avatar-title bg-primary-lighten rounded-circle">
                                                <i class="mdi mdi-home-analytics text-primary font-32"></i>
                                            </span>
                                        </div>
                                        <h3 class="mb-0">Asset Management</h3>
                                    </div>
                                    <p class="text-muted mb-4">Track and manage your entire real estate portfolio with comprehensive asset information, performance metrics, and operational data.</p>
                                    <ul class="list-unstyled feature-bullets">
                                        <li class="mb-3">
                                            <i class="mdi mdi-check-circle text-success me-2"></i>
                                            <strong>Portfolio Overview:</strong> Centralized dashboard showing all assets with key metrics and status
                                        </li>
                                        <li class="mb-3">
                                            <i class="mdi mdi-check-circle text-success me-2"></i>
                                            <strong>Property Tracking:</strong> Detailed property records with photos, documents, and historical data
                                        </li>
                                        <li class="mb-3">
                                            <i class="mdi mdi-check-circle text-success me-2"></i>
                                            <strong>Performance Monitoring:</strong> Track cash flows, expenses, and returns for each asset
                                        </li>
                                        <li class="mb-3">
                                            <i class="mdi mdi-check-circle text-success me-2"></i>
                                            <strong>Document Management:</strong> Secure storage and organization of all property-related documents
                                        </li>
                                    </ul>
                                </div>
                            </b-col>
                        </b-row>
                    </b-carousel-slide>

                    <!-- Feature 3: Portfolio Reporting -->
                    <b-carousel-slide>
                        <b-row class="align-items-center py-4">
                            <b-col lg="6" md="6" class="order-2 order-lg-1">
                                <div class="pe-lg-4">
                                    <div class="d-flex align-items-center mb-3">
                                        <div class="avatar-lg me-3">
                                            <span class="avatar-title bg-primary-lighten rounded-circle">
                                                <i class="mdi mdi-chart-box text-primary font-32"></i>
                                            </span>
                                        </div>
                                        <h3 class="mb-0">Portfolio Reporting</h3>
                                    </div>
                                    <p class="text-muted mb-4">Generate comprehensive reports and analytics to track performance, analyze trends, and make data-driven decisions.</p>
                                    <ul class="list-unstyled feature-bullets">
                                        <li class="mb-3">
                                            <i class="mdi mdi-check-circle text-success me-2"></i>
                                            <strong>By Trade Reports:</strong> Analyze performance by acquisition trade or transaction
                                        </li>
                                        <li class="mb-3">
                                            <i class="mdi mdi-check-circle text-success me-2"></i>
                                            <strong>By Status Reports:</strong> Track assets by current status (active, sold, in foreclosure, etc.)
                                        </li>
                                        <li class="mb-3">
                                            <i class="mdi mdi-check-circle text-success me-2"></i>
                                            <strong>By Fund/Entity:</strong> Financial reporting organized by fund, entity, or legal structure
                                        </li>
                                        <li class="mb-3">
                                            <i class="mdi mdi-check-circle text-success me-2"></i>
                                            <strong>Custom Dashboards:</strong> Create personalized dashboards with key metrics and visualizations
                                        </li>
                                    </ul>
                                </div>
                            </b-col>
                            <b-col lg="6" md="6" class="order-1 order-lg-2">
                                <div class="text-center">
                                    <img 
                                        src="@/assets/images/svg/startup.svg" 
                                        alt="Portfolio Reporting" 
                                        class="img-fluid rounded shadow-lg"
                                        style="max-height: 500px;" />
                                </div>
                            </b-col>
                        </b-row>
                    </b-carousel-slide>

                    <!-- Feature 4: CRM & Relationships -->
                    <b-carousel-slide>
                        <b-row class="align-items-center py-4">
                            <b-col lg="6" md="6" class="order-2 order-lg-2">
                                <div class="text-center">
                                    <img 
                                        src="@/assets/images/svg/features-1.svg" 
                                        alt="CRM & Relationships" 
                                        class="img-fluid rounded shadow-lg"
                                        style="max-height: 500px;" />
                                </div>
                            </b-col>
                            <b-col lg="6" md="6" class="order-1 order-lg-1">
                                <div class="ps-lg-4">
                                    <div class="d-flex align-items-center mb-3">
                                        <div class="avatar-lg me-3">
                                            <span class="avatar-title bg-primary-lighten rounded-circle">
                                                <i class="mdi mdi-account-group text-primary font-32"></i>
                                            </span>
                                        </div>
                                        <h3 class="mb-0">CRM & Relationships</h3>
                                    </div>
                                    <p class="text-muted mb-4">Manage your network of trading partners, brokers, and business relationships with integrated CRM functionality.</p>
                                    <ul class="list-unstyled feature-bullets">
                                        <li class="mb-3">
                                            <i class="mdi mdi-check-circle text-success me-2"></i>
                                            <strong>Trading Partners:</strong> Comprehensive database of brokers, investors, and business contacts
                                        </li>
                                        <li class="mb-3">
                                            <i class="mdi mdi-check-circle text-success me-2"></i>
                                            <strong>MSA Assignments:</strong> Assign brokers to specific markets and track coverage
                                        </li>
                                        <li class="mb-3">
                                            <i class="mdi mdi-check-circle text-success me-2"></i>
                                            <strong>Contact Management:</strong> Store contact information, notes, and interaction history
                                        </li>
                                        <li class="mb-3">
                                            <i class="mdi mdi-check-circle text-success me-2"></i>
                                            <strong>Relationship Tracking:</strong> Monitor deals, assignments, and business relationships
                                        </li>
                                    </ul>
                                </div>
                            </b-col>
                        </b-row>
                    </b-carousel-slide>

                    <!-- Feature 5: Valuation Center -->
                    <b-carousel-slide>
                        <b-row class="align-items-center py-4">
                            <b-col lg="6" md="6" class="order-2 order-lg-1">
                                <div class="pe-lg-4">
                                    <div class="d-flex align-items-center mb-3">
                                        <div class="avatar-lg me-3">
                                            <span class="avatar-title bg-primary-lighten rounded-circle">
                                                <i class="mdi mdi-cash-multiple text-primary font-32"></i>
                                            </span>
                                        </div>
                                        <h3 class="mb-0">Valuation Center</h3>
                                    </div>
                                    <p class="text-muted mb-4">Accurate property valuations using comparable sales, lease comparables, and advanced valuation methodologies.</p>
                                    <ul class="list-unstyled feature-bullets">
                                        <li class="mb-3">
                                            <i class="mdi mdi-check-circle text-success me-2"></i>
                                            <strong>Sales Comparables:</strong> Compare properties using recent sales data and market trends
                                        </li>
                                        <li class="mb-3">
                                            <i class="mdi mdi-check-circle text-success me-2"></i>
                                            <strong>Lease Comparables:</strong> Analyze rental rates and lease terms for income properties
                                        </li>
                                        <li class="mb-3">
                                            <i class="mdi mdi-check-circle text-success me-2"></i>
                                            <strong>Valuation Grades:</strong> Quality scoring system for valuation accuracy and reliability
                                        </li>
                                        <li class="mb-3">
                                            <i class="mdi mdi-check-circle text-success me-2"></i>
                                            <strong>Market Analysis:</strong> Geographic and market intelligence for informed valuations
                                        </li>
                                    </ul>
                                </div>
                            </b-col>
                            <b-col lg="6" md="6" class="order-1 order-lg-2">
                                <div class="text-center">
                                    <img 
                                        src="@/assets/images/svg/features-2.svg" 
                                        alt="Valuation Center" 
                                        class="img-fluid rounded shadow-lg"
                                        style="max-height: 500px;" />
                                </div>
                            </b-col>
                        </b-row>
                    </b-carousel-slide>

                    <!-- Feature 6: Data Integration -->
                    <b-carousel-slide>
                        <b-row class="align-items-center py-4">
                            <b-col lg="6" md="6" class="order-2 order-lg-2">
                                <div class="text-center">
                                    <img 
                                        src="@/assets/images/svg/startup.svg" 
                                        alt="Data Integration" 
                                        class="img-fluid rounded shadow-lg"
                                        style="max-height: 500px;" />
                                </div>
                            </b-col>
                            <b-col lg="6" md="6" class="order-1 order-lg-1">
                                <div class="ps-lg-4">
                                    <div class="d-flex align-items-center mb-3">
                                        <div class="avatar-lg me-3">
                                            <span class="avatar-title bg-primary-lighten rounded-circle">
                                                <i class="mdi mdi-database-sync text-primary font-32"></i>
                                            </span>
                                        </div>
                                        <h3 class="mb-0">Data Integration</h3>
                                    </div>
                                    <p class="text-muted mb-4">Seamlessly import and sync data from multiple sources with automated ETL processes and validation.</p>
                                    <ul class="list-unstyled feature-bullets">
                                        <li class="mb-3">
                                            <i class="mdi mdi-check-circle text-success me-2"></i>
                                            <strong>Excel/CSV Import:</strong> Bulk import data from spreadsheets with automatic mapping
                                        </li>
                                        <li class="mb-3">
                                            <i class="mdi mdi-check-circle text-success me-2"></i>
                                            <strong>Outlook Integration:</strong> Import data directly from Outlook emails and attachments
                                        </li>
                                        <li class="mb-3">
                                            <i class="mdi mdi-check-circle text-success me-2"></i>
                                            <strong>Data Validation:</strong> Automatic validation and error checking during import
                                        </li>
                                        <li class="mb-3">
                                            <i class="mdi mdi-check-circle text-success me-2"></i>
                                            <strong>API Access:</strong> RESTful API for programmatic data access and integrations
                                        </li>
                                    </ul>
                                </div>
                            </b-col>
                        </b-row>
                    </b-carousel-slide>

                    </b-carousel>
                </div>
            </b-col>
        </b-row>
    </b-container>
</section>
<!-- END FEATURES 1 -->
</template>

<script>
export default {
    name: 'Feature1',
    data() {
        return {
            // WHAT: Current active slide index for the carousel
            // WHY: Tracks which feature slide is currently displayed
            currentSlide: 0
        }
    },
    methods: {
        // WHAT: Handle carousel slide change event
        // WHY: Update current slide index when user navigates
        // WHERE: Called when carousel starts sliding to a new slide
        onSlideStart(newIndex) {
            this.currentSlide = newIndex;
        }
    }
}
</script>

<style scoped>
/* WHAT: Custom styles for feature carousel section
     WHY: Enhance visual appearance and spacing of feature slides, ensure content is not cut off
     WHERE: Applied to feature1 component */
.feature-carousel-wrapper {
    background: #f8f9fa;
    border-radius: 8px;
    padding: 30px;
    margin-top: 20px;
    overflow: visible;
    border: none !important;
    box-shadow: none !important;
    outline: none;
}

/* Remove any inherited borders */
.feature-carousel-wrapper * {
    border: none !important;
}

.feature-carousel {
    min-height: 650px;
    background: transparent;
    overflow: visible;
    border: none !important;
}

.feature-carousel :deep(.carousel) {
    border: none !important;
}

.feature-carousel :deep(.carousel-inner) {
    min-height: 600px;
    overflow: visible;
}

.feature-carousel :deep(.carousel-item) {
    min-height: 600px;
    padding: 30px 0;
    overflow: visible;
}

.feature-carousel :deep(.carousel-item.active) {
    display: block;
}

/* Ensure rows and columns don't cut off content */
.feature-carousel :deep(.row) {
    margin-left: 0;
    margin-right: 0;
    min-height: 540px;
}

.feature-carousel :deep(.col) {
    padding-left: 15px;
    padding-right: 15px;
}

.feature-bullets {
    margin-bottom: 0;
    padding-left: 0;
}

.feature-bullets li {
    font-size: 15px;
    line-height: 1.8;
    margin-bottom: 12px;
}

.feature-bullets li:last-child {
    margin-bottom: 0;
}

.feature-bullets i {
    font-size: 20px;
    vertical-align: middle;
    flex-shrink: 0;
}

/* Ensure images are responsive and maintain aspect ratio */
.feature-carousel img {
    max-width: 100%;
    height: auto;
    object-fit: contain;
    max-height: 500px;
}

/* Carousel controls styling */
.feature-carousel :deep(.carousel-control-prev),
.feature-carousel :deep(.carousel-control-next) {
    width: 50px;
    height: 50px;
    background-color: rgba(0, 0, 0, 0.5);
    border-radius: 50%;
    top: 50%;
    transform: translateY(-50%);
    z-index: 10;
}

.feature-carousel :deep(.carousel-control-prev) {
    left: 20px;
}

.feature-carousel :deep(.carousel-control-next) {
    right: 20px;
}

/* Carousel indicators - position at bottom with proper spacing */
.feature-carousel :deep(.carousel-indicators) {
    margin-bottom: 20px;
    bottom: 0;
}

/* Ensure content containers have proper spacing */
.feature-carousel :deep(.pe-lg-4),
.feature-carousel :deep(.ps-lg-4) {
    padding-right: 2rem;
    padding-left: 2rem;
}

@media (max-width: 991px) {
    .feature-carousel {
        min-height: auto;
    }
    
    .feature-carousel :deep(.carousel-inner) {
        min-height: auto;
    }
    
    .feature-carousel :deep(.carousel-item) {
        min-height: auto;
        padding: 20px 0;
    }
    
    .feature-carousel :deep(.row) {
        min-height: auto;
    }
}
</style>
