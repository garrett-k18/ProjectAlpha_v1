<template>
<b-form>
    <h5 class="mb-4 text-uppercase"><i class="mdi mdi-account-circle me-1"></i> Personal Info</h5>
    <b-row>
        <b-col md="6">
            <b-form-group label="First Name" label-for="firstname" class="mb-3">
                <b-form-input type="text" class="form-control" id="firstname" placeholder="Enter first name" />
            </b-form-group>
        </b-col>
        <b-col md="6">
            <b-form-group label="Last Name" label-for="lastname" class="mb-3">
                <b-form-input type="text" class="form-control" id="lastname" placeholder="Enter last name" />
            </b-form-group>
        </b-col> <!-- end col -->
    </b-row> <!-- end row -->

    <b-row>
        <b-col cols="12">
            <b-form-group label="Bio" label-for="userbio" class="mb-3">
                <b-form-textarea class="form-control" id="userbio" rows="4" placeholder="Write something..."></b-form-textarea>
            </b-form-group>
        </b-col> <!-- end col -->
    </b-row> <!-- end row -->

    <b-row>
        <b-col md="6">
            <b-form-group label="Email Address" label-for="useremail" class="mb-3">
                <b-form-input type="email" id="useremail" placeholder="Enter email" />
                <span class="form-text text-muted"><small>If you want to change email please <a href="javascript: void(0);">click</a> here.</small></span>
            </b-form-group>
        </b-col>
        <b-col md="6">
            <div class="mb-3">
                <label for="userpassword" class="form-label">Password</label>
                <b-form-input type="password" class="form-control" id="userpassword" placeholder="Enter password" />
                <span class="form-text text-muted"><small>If you want to change password please <a href="javascript: void(0);">click</a> here.</small></span>
            </div>
        </b-col> <!-- end col -->
    </b-row> <!-- end row -->

    <h5 class="mb-3 text-uppercase bg-light p-2"><i class="mdi mdi-office-building me-1"></i> Company Info</h5>
    <b-row>
        <b-col md="6">
            <b-form-group label="Company Name" label-for="companyname" class="mb-3">
                <b-form-input type="text" id="companyname" placeholder="Enter company name" />
            </b-form-group>
        </b-col>
        <b-col md="6">
            <b-form-group label="Website" label-for="cwebsite" class="mb-3">
                <b-form-input type="text" id="cwebsite" placeholder="Enter website url" />
            </b-form-group>
        </b-col> <!-- end col -->
    </b-row> <!-- end row -->

    <h5 class="mb-3 text-uppercase bg-light p-2"><i class="mdi mdi-earth me-1"></i> Social</h5>
    <b-row>
        <b-col md="6">
            <b-form-group label="Facebook" label-for="social-fb" class="mb-3">
                <div class="input-group">
                    <span class="input-group-text"><i class="mdi mdi-facebook"></i></span>
                    <b-form-input type="text" class="form-control" id="social-fb" placeholder="Url" />
                </div>
            </b-form-group>
        </b-col>
        <b-col md="6">
            <b-form-group label="Twitter" label-for="social-tw" class="mb-3">
                <div class="input-group">
                    <span class="input-group-text"><i class="mdi mdi-twitter"></i></span>
                    <b-form-input type="text" class="form-control" id="social-tw" placeholder="Username" />
                </div>
            </b-form-group>
        </b-col> <!-- end col -->
    </b-row> <!-- end row -->

    <b-row>
        <b-col md="6">
            <b-form-group label="Instagram" label-for="social-insta" class="mb-3">
                <div class="input-group">
                    <span class="input-group-text"><i class="mdi mdi-instagram"></i></span>
                    <b-form-input type="text" class="form-control" id="social-insta" placeholder="Url" />
                </div>
            </b-form-group>
        </b-col>
        <b-col md="6">
            <b-form-group label="Linkedin" label-for="social-lin" class="mb-3">
                <div class="input-group">
                    <span class="input-group-text"><i class="mdi mdi-linkedin"></i></span>
                    <b-form-input type="text" class="form-control" id="social-lin" placeholder="Url" />
                </div>
            </b-form-group>
        </b-col> <!-- end col -->
    </b-row> <!-- end row -->

    <b-row>
        <b-col md="6">
            <b-form-group label="Skype" label-for="social-sky" class="mb-3">
                <div class="input-group">
                    <span class="input-group-text"><i class="mdi mdi-skype"></i></span>
                    <b-form-input type="text" class="form-control" id="social-sky" placeholder="@username" />
                </div>
            </b-form-group>
        </b-col>
        <b-col md="6">
            <b-form-group label="Github" label-for="social-gh" class="mb-3">
                <div class="input-group">
                    <span class="input-group-text"><i class="mdi mdi-github"></i></span>
                    <b-form-input type="text" class="form-control" id="social-gh" placeholder="Username" />
                </div>
            </b-form-group>
        </b-col> <!-- end col -->
    </b-row> <!-- end row -->

    <div class="text-end">
        <b-button type="submit" class="mt-2" variant="success"><i class="mdi mdi-content-save"></i> Save</b-button>
    </div>
</b-form>
</template>

<script>
export default {

}
</script>
