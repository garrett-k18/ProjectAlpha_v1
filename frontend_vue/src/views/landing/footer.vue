<template>
  <!-- START FOOTER -->
  <!-- WHAT: Footer section with company information and links
       WHY: Provides navigation, contact info, and legal information
       WHERE: Bottom of landing page -->
  <footer class="bg-dark py-5">
    <div class="container">
      <div class="row">
        <div class="col-lg-6">
          <span class="text-white fw-bold fs-3">ProjectAlpha</span>
          <p class="text-light text-opacity-50 mt-4">Comprehensive real estate investment and asset management platform.
            <br> Streamline your operations from acquisition through disposition.
            <br> Built for real estate professionals, by real estate professionals.</p>

          <ul class="social-list list-inline mt-3">
            <li class="list-inline-item text-center">
              <a href="javascript: void(0);" class="social-list-item border-primary text-primary"><i
                  class="mdi mdi-linkedin"></i></a>
            </li>
            <li class="list-inline-item text-center">
              <a href="javascript: void(0);" class="social-list-item border-danger text-danger"><i
                  class="mdi mdi-email"></i></a>
            </li>
            <li class="list-inline-item text-center">
              <a href="javascript: void(0);" class="social-list-item border-info text-info"><i
                  class="mdi mdi-twitter"></i></a>
            </li>
          </ul>

        </div>

        <div class="col-lg-2 col-md-4 mt-3 mt-lg-0">
          <h5 class="text-light">Platform</h5>

          <ul class="list-unstyled ps-0 mb-0 mt-3">
            <li class="mt-2"><a href="#features" class="text-light text-opacity-50">Features</a></li>
            <li class="mt-2"><a href="#services" class="text-light text-opacity-50">Services</a></li>
            <li class="mt-2"><router-link to="/login" class="text-light text-opacity-50">Login</router-link></li>
            <li class="mt-2"><a href="#contact" class="text-light text-opacity-50">Contact</a></li>
          </ul>

        </div>

        <div class="col-lg-2 col-md-4 mt-3 mt-lg-0">
          <h5 class="text-light">Modules</h5>

          <ul class="list-unstyled ps-0 mb-0 mt-3">
            <li class="mt-2"><a href="#services" class="text-light text-opacity-50">Acquisition</a></li>
            <li class="mt-2"><a href="#services" class="text-light text-opacity-50">Asset Management</a></li>
            <li class="mt-2"><a href="#services" class="text-light text-opacity-50">Reporting</a></li>
            <li class="mt-2"><a href="#services" class="text-light text-opacity-50">CRM</a></li>
            <li class="mt-2"><a href="#services" class="text-light text-opacity-50">Valuations</a></li>
          </ul>
        </div>

        <div class="col-lg-2 col-md-4 mt-3 mt-lg-0">
          <h5 class="text-light">Support</h5>

          <ul class="list-unstyled ps-0 mb-0 mt-3">
            <li class="mt-2"><a href="#faq" class="text-light text-opacity-50">FAQ</a></li>
            <li class="mt-2"><a href="#contact" class="text-light text-opacity-50">Contact Us</a></li>
            <li class="mt-2"><a href="javascript: void(0);" class="text-light text-opacity-50">Documentation</a></li>
            <li class="mt-2"><a href="javascript: void(0);" class="text-light text-opacity-50">Privacy Policy</a></li>
          </ul>
        </div>
      </div>

      <div class="row">
        <div class="col-lg-12">
          <div class="mt-5">
            <p class="text-light text-opacity-50 mt-4 text-center mb-0">© {{ year }} ProjectAlpha. All rights reserved.
              <br>Built with Vue.js, Django, and PostgreSQL</p>
          </div>
        </div>
      </div>
    </div>
  </footer>
  <!-- END FOOTER -->
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