<template>
<!-- NAVBAR START -->
<nav class="navbar navbar-expand-lg py-lg-3 navbar-dark">
    <b-container>

        <!-- logo -->
        <router-link to="/" class="navbar-brand me-lg-5">
            <img src="@/assets/images/logo.png" alt="logo" class="logo-dark" height="22" />
        </router-link>

        <b-button class="navbar-toggler" v-b-toggle.navbarNavDropdown>
            <i class="mdi mdi-menu"></i>
        </b-button>

        <!-- menus -->
        <b-collapse class="navbar-collapse" id="navbarNavDropdown">

            <!-- left menu -->
            <ul class="navbar-nav me-auto align-items-center">
                <li class="nav-item mx-lg-1">
                    <router-link class="nav-link active" to="">Home</router-link>
                </li>
                <li class="nav-item mx-lg-1">
                    <router-link class="nav-link text-white" to="">Features</router-link>
                </li>
                <li class="nav-item mx-lg-1">
                    <router-link class="nav-link text-white" to="">Pricing</router-link>
                </li>
                <li class="nav-item mx-lg-1">
                    <router-link class="nav-link text-white" to="">FAQs</router-link>
                </li>
                <li class="nav-item mx-lg-1">
                    <router-link class="nav-link text-white" to="">Clients</router-link>
                </li>
                <li class="nav-item mx-lg-1">
                    <router-link class="nav-link text-white" to="">Contact</router-link>
                </li>
            </ul>

            <!-- right menu -->
            <ul class="navbar-nav ms-auto align-items-center">
                <li class="nav-item me-0">
                    <a href="#" target="_blank" class="nav-link d-lg-none">Purchase now</a>
                    <a href="#" target="_blank" class="btn btn-sm btn-light rounded-pill d-none d-lg-inline-flex">
                        <i class="mdi mdi-basket me-2"></i> Purchase Now
                    </a>
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
