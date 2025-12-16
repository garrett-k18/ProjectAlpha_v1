<template>
<!-- NAVBAR START -->
<!-- WHAT: Navigation bar for ProjectAlpha landing page
     WHY: Provides navigation to different sections and login access
     WHERE: Top of landing page, sticky navigation -->
<nav class="navbar navbar-expand-lg py-lg-3 navbar-dark">
    <b-container>

        <!-- logo -->
        <router-link to="/landing" class="navbar-brand me-lg-5">
            <span class="text-white fw-bold fs-3">ProjectAlpha</span>
        </router-link>

        <b-button class="navbar-toggler" v-b-toggle.navbarNavDropdown>
            <i class="mdi mdi-menu"></i>
        </b-button>

        <!-- menus -->
        <b-collapse class="navbar-collapse" id="navbarNavDropdown">

            <!-- left menu -->
            <ul class="navbar-nav me-auto align-items-center">
                <li class="nav-item mx-lg-1">
                    <a class="nav-link active" href="#home">Home</a>
                </li>
                <li class="nav-item mx-lg-1">
                    <a class="nav-link text-white" href="#features">Features</a>
                </li>
                <li class="nav-item mx-lg-1">
                    <a class="nav-link text-white" href="#services">Services</a>
                </li>
                <li class="nav-item mx-lg-1">
                    <a class="nav-link text-white" href="#faq">FAQs</a>
                </li>
                <li class="nav-item mx-lg-1">
                    <a class="nav-link text-white" href="#contact">Contact</a>
                </li>
            </ul>

            <!-- right menu -->
            <ul class="navbar-nav ms-auto align-items-center">
                <li class="nav-item me-0">
                    <router-link to="/login" class="nav-link d-lg-none text-white">Login</router-link>
                    <router-link to="/login" class="btn btn-sm btn-light rounded-pill d-none d-lg-inline-flex">
                        <i class="mdi mdi-login me-2"></i> Login
                    </router-link>
                </li>
            </ul>

        </b-collapse>
    </b-container>
</nav>
<!-- NAVBAR END -->
</template>

<script>
export default {
    name: 'Navbar'
}
</script>
