<template>
<!-- START CONTACT -->
<section class="py-5 bg-light-lighten border-top border-bottom border-light">
    <b-container>
        <b-row>
            <b-col lg="12">
                <div class="text-center">
                    <h3>Get In <span class="text-primary">Touch</span></h3>
                    <p class="text-muted mt-2">Please fill out the following form and we will get back to you shortly. For more
                        <br>information please contact us.</p>
                </div>
            </b-col>
        </b-row>

        <b-row class="align-items-center mt-3">
            <b-col md="4">
                <p class="text-muted"><span class="fw-bold">Customer Support:</span><br> <span class="d-block mt-1">+1 234 56 7894</span></p>
                <p class="text-muted mt-4"><span class="fw-bold">Email Address:</span><br> <span class="d-block mt-1">info@gmail.com</span></p>
                <p class="text-muted mt-4"><span class="fw-bold">Office Address:</span><br> <span class="d-block mt-1">4461 Cedar Street Moro, AR 72368</span></p>
                <p class="text-muted mt-4"><span class="fw-bold">Office Time:</span><br> <span class="d-block mt-1">9:00AM To 6:00PM</span></p>
            </b-col>

            <b-col md="7">
                <b-form>
                    <b-row class="mt-4">
                        <b-col lg="6">
                            <b-form-group label="Your Name" label-for="fullname" class="mb-2">
                                <b-form-input class="form-control-light py-2" type="text" id="fullname" placeholder="Name..." />
                            </b-form-group>
                        </b-col>
                        <b-col lg="6">
                            <b-form-group label="Your Email" label-for="emailaddress" class="mb-2">
                                <b-form-input class="form-control-light py-2" type="email" required id="emailaddress" placeholder="Enter you email..." />
                            </b-form-group>
                        </b-col>
                    </b-row>

                    <b-row class="mt-1">
                        <b-col lg="12">
                            <b-form-group label="Your Subject" label-for="subject" class="mb-2">
                                <b-form-input class="form-control-light py-2" type="text" id="subject" placeholder="Enter subject..." />
                            </b-form-group>
                        </b-col>
                    </b-row>

                    <b-row class="mt-1">
                        <b-col lg="12">
                            <b-form-group label="Message" label-for="comments" class="mb-2">
                                <b-form-textarea id="comments" rows="4" class="form-control-light" placeholder="Type your message here..."></b-form-textarea>
                            </b-form-group>
                        </b-col>
                    </b-row>

                    <b-row class="mt-2">
                        <b-col cols="12" class="text-end">
                            <b-button variant="primary">Send a Message <i class="mdi mdi-telegram ms-1"></i> </b-button>
                        </b-col>
                    </b-row>
                </b-form>
            </b-col>
        </b-row>
    </b-container>
</section>
<!-- END CONTACT -->
</template>
