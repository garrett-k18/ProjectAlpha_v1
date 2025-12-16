<template>
<!-- START CONTACT -->
<!-- WHAT: Contact section with form and contact information
     WHY: Allows visitors to reach out for inquiries and support
     WHERE: Landing page, after FAQ section -->
<section id="contact" class="py-5 bg-light-lighten border-top border-bottom border-light">
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
                <p class="text-muted"><span class="fw-bold">Customer Support:</span><br> <span class="d-block mt-1">Contact us via email</span></p>
                <p class="text-muted mt-4"><span class="fw-bold">Email Address:</span><br> <span class="d-block mt-1">info@projectalpha.com</span></p>
                <p class="text-muted mt-4"><span class="fw-bold">Business Hours:</span><br> <span class="d-block mt-1">Monday - Friday: 9:00AM - 6:00PM EST</span></p>
                <p class="text-muted mt-4"><span class="fw-bold">Platform Access:</span><br> <span class="d-block mt-1"><router-link to="/login">Login to your account</router-link></span></p>
            </b-col>

            <b-col md="7">
                <b-form @submit.prevent="handleSubmit">
                    <b-row class="mt-4">
                        <b-col lg="6">
                            <b-form-group label="Your Name" label-for="fullname" class="mb-2">
                                <b-form-input 
                                    class="form-control-light py-2" 
                                    type="text" 
                                    id="fullname" 
                                    v-model="form.name"
                                    placeholder="Name..." 
                                    required />
                            </b-form-group>
                        </b-col>
                        <b-col lg="6">
                            <b-form-group label="Your Email" label-for="emailaddress" class="mb-2">
                                <b-form-input 
                                    class="form-control-light py-2" 
                                    type="email" 
                                    required 
                                    id="emailaddress" 
                                    v-model="form.email"
                                    placeholder="Enter your email..." />
                            </b-form-group>
                        </b-col>
                    </b-row>

                    <b-row class="mt-1">
                        <b-col lg="12">
                            <b-form-group label="Your Subject" label-for="subject" class="mb-2">
                                <b-form-input 
                                    class="form-control-light py-2" 
                                    type="text" 
                                    id="subject" 
                                    v-model="form.subject"
                                    placeholder="Enter subject..." />
                            </b-form-group>
                        </b-col>
                    </b-row>

                    <b-row class="mt-1">
                        <b-col lg="12">
                            <b-form-group label="Message" label-for="comments" class="mb-2">
                                <b-form-textarea 
                                    id="comments" 
                                    rows="4" 
                                    class="form-control-light" 
                                    v-model="form.message"
                                    placeholder="Type your message here..."
                                    required></b-form-textarea>
                            </b-form-group>
                        </b-col>
                    </b-row>

                    <b-row class="mt-2">
                        <b-col cols="12" class="text-end">
                            <b-button type="submit" variant="primary" :disabled="submitting">
                                <span v-if="!submitting">Send a Message <i class="mdi mdi-telegram ms-1"></i></span>
                                <span v-else>Sending...</span>
                            </b-button>
                        </b-col>
                    </b-row>
                </b-form>
            </b-col>
        </b-row>
    </b-container>
</section>
<!-- END CONTACT -->
</template>

<script>
export default {
    name: 'Contact',
    data() {
        return {
            form: {
                name: '',
                email: '',
                subject: '',
                message: ''
            },
            submitting: false
        }
    },
    methods: {
        handleSubmit() {
            // WHAT: Handle contact form submission
            // WHY: Process user inquiries and provide feedback
            // TODO: Connect to backend API endpoint when available
            this.submitting = true;
            console.log('Contact form submitted:', this.form);
            // Simulate API call
            setTimeout(() => {
                alert('Thank you for your message! We will get back to you shortly.');
                this.form = { name: '', email: '', subject: '', message: '' };
                this.submitting = false;
            }, 1000);
        }
    }
}
</script>
