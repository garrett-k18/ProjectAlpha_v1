<template>
<b-card class="text-center">
    <b-avatar src="@/assets/images/users/avatar-1.jpg" variant="light" class="avatar-lg img-thumbnail"  rounded="circle" alt="profile-image" />

    <h4 class="mb-0 mt-2">Dominic Keller</h4>
    <p class="text-muted font-14">Founder</p>

    <b-button class="mb-2 me-1" size="sm" variant="success">Follow</b-button>
    <b-button class="mb-2" size="sm" variant="danger">Message</b-button>

    <div class="text-start mt-3">
        <h4 class="font-13 text-uppercase">About Me :</h4>
        <p class="text-muted font-13 mb-3">
            Hi I'm Johnathn Deo,has been the industry's standard dummy text ever since the
            1500s, when an unknown printer took a galley of type.
        </p>
        <p class="text-muted mb-2 font-13"><strong>Full Name :</strong> <span class="ms-2">Geneva
                D. McKnight</span></p>

        <p class="text-muted mb-2 font-13"><strong>Mobile :</strong><span class="ms-2">(123)
                123 1234</span></p>

        <p class="text-muted mb-2 font-13"><strong>Email :</strong> <span class="ms-2 ">user@email.domain</span></p>

        <p class="text-muted mb-1 font-13"><strong>Location :</strong> <span class="ms-2">USA</span></p>
    </div>

    <ul class="social-list list-inline mt-3 mb-0">
        <li class="list-inline-item">
            <a href="javascript: void(0);" class="social-list-item border-primary text-primary"><i class="mdi mdi-facebook"></i></a>
        </li>
        <li class="list-inline-item">
            <a href="javascript: void(0);" class="social-list-item border-danger text-danger"><i class="mdi mdi-google"></i></a>
        </li>
        <li class="list-inline-item">
            <a href="javascript: void(0);" class="social-list-item border-info text-info"><i class="mdi mdi-twitter"></i></a>
        </li>
        <li class="list-inline-item">
            <a href="javascript: void(0);" class="social-list-item border-secondary text-secondary"><i class="mdi mdi-github"></i></a>
        </li>
    </ul>
</b-card> <!-- end card -->
</template>

<script lang="ts">
export default {

}
</script>
