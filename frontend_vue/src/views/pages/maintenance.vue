<template>
<div>
    <div class="mt-5 mb-5">
        <b-container>
            <b-row class="justify-content-center">
                <b-col xl="10">

                    <div class="text-center">
                        <img src="@/assets/images/svg/maintenance.svg" height="140" alt="File not found Image">
                        <h3 class="mt-4">Site is Under Maintenance</h3>
                        <p class="text-muted">We're making the system more awesome. We'll be back shortly.</p>

                        <b-row class="mt-5">
                            <b-col md="4">
                                <div class="text-center mt-3 ps-1 pe-1">
                                    <i class="ri-vip-diamond-line bg-primary maintenance-icon text-white mb-4"></i>
                                    <h5 class="text-uppercase">Why is the Site Down?</h5>
                                    <p class="text-muted">There are many variations of passages of Lorem Ipsum available, but the majority have suffered alteration.</p>
                                </div>
                            </b-col> <!-- end col-->
                            <b-col md="4">
                                <div class="text-center mt-3 ps-1 pe-1">
                                    <i class="ri-time-line bg-primary maintenance-icon text-white mb-4"></i>
                                    <h5 class="text-uppercase">What is the Downtime?</h5>
                                    <p class="text-muted">Contrary to popular belief, Lorem Ipsum is not simply random text. It has roots in a piece of classical but the majority.</p>
                                </div>
                            </b-col> <!-- end col-->
                            <b-col md="4">
                                <div class="text-center mt-3 ps-1 pe-1">
                                    <i class="ri-question-mark bg-primary maintenance-icon text-white mb-4"></i>
                                    <h5 class="text-uppercase">Do you need Support?</h5>
                                    <p class="text-muted">If you are going to use a passage of Lorem Ipsum, you need to be sure there isn't anything embar.. <a href="mailto:#" class="text-muted fw-bold">no-reply@domain.com</a></p>
                                </div>
                            </b-col> <!-- end col-->
                        </b-row> <!-- end row-->
                    </div> <!-- end /.text-center-->

                </b-col> <!-- end col -->
            </b-row>
            <!-- end row -->
        </b-container>
        <!-- end container -->
    </div>
    <!-- end page -->

    <footer class="footer footer-alt">
      <!-- Footer content removed -->
    </footer>
</div>
</template>

<script lang="ts">
export default {
    computed: {
        year() {
            return new Date().getFullYear()
        }
    }

}
</script>
