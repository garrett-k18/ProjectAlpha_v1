<template>
<Layout>
    <Breadcrumb :items="items" :title="title" />

    <b-row>
        <b-col cols="12">
            <b-card>

                <!-- Invoice Logo-->
                <div class="clearfix">
                    <div class="float-start mb-3">
                        <img src="@/assets/images/logo-dark.png" alt="dark logo" height="22">
                    </div>
                    <div class="float-end">
                        <h4 class="m-0 d-print-none">Invoice</h4>
                    </div>
                </div>

                <!-- Invoice Detail-->
                <b-row>
                    <b-col sm="6">
                        <div class="float-end mt-3">
                            <p><b>Hello, Cooper Hobson</b></p>
                            <p class="text-muted font-13">Please find below a cost-breakdown for the recent work completed. Please make payment at your earliest convenience, and do not hesitate to contact me with any questions.</p>
                        </div>

                    </b-col><!-- end col -->
                    <b-col sm="4" offset-sm="2">
                        <div class="mt-3 float-sm-end">
                            <p class="font-13"><strong>Order Date: </strong> &nbsp;&nbsp;&nbsp; Jan 17, 2018</p>
                            <p class="font-13"><strong>Order Status: </strong>
                                <b-badge variant="success" class="float-end">Paid</b-badge>
                            </p>
                            <p class="font-13"><strong>Order ID: </strong> <span class="float-end">#123456</span></p>
                        </div>
                    </b-col><!-- end col -->
                </b-row>
                <!-- end row -->

                <b-row class="mt-4">
                    <b-col sm="4">
                        <h6>Billing Address</h6>
                        <address>
                            Lynne K. Higby<br>
                            795 Folsom Ave, Suite 600<br>
                            San Francisco, CA 94107<br>
                            <abbr title="Phone">P:</abbr> (123) 456-7890
                        </address>
                    </b-col> <!-- end col-->

                    <b-col sm="4">
                        <h6>Shipping Address</h6>
                        <address>
                            Cooper Hobson<br>
                            795 Folsom Ave, Suite 600<br>
                            San Francisco, CA 94107<br>
                            <abbr title="Phone">P:</abbr> (123) 456-7890
                        </address>
                    </b-col> <!-- end col-->

                    <b-col sm="4">
                        <div class="text-sm-end">
                            <img src="@/assets/images/barcode.png" alt="barcode-image" class="img-fluid me-2" />
                        </div>
                    </b-col> <!-- end col-->
                </b-row>
                <!-- end row -->

                <b-row>
                    <b-col cols="12">
                        <div class="table-responsive">
                            <table class="table mt-4">
                                <thead>
                                    <tr>
                                        <th>#</th>
                                        <th>Item</th>
                                        <th>Quantity</th>
                                        <th>Unit Cost</th>
                                        <th class="text-end">Total</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr>
                                        <td>1</td>
                                        <td>
                                            <b>Laptop</b> <br />
                                            Brand Model VGN-TXN27N/B
                                            11.1" Notebook PC
                                        </td>
                                        <td>1</td>
                                        <td>$1799.00</td>
                                        <td class="text-end">$1799.00</td>
                                    </tr>
                                    <tr>
                                        <td>2</td>
                                        <td>
                                            <b>Warranty</b> <br />
                                            Two Year Extended Warranty -
                                            Parts and Labor
                                        </td>
                                        <td>3</td>
                                        <td>$499.00</td>
                                        <td class="text-end">$1497.00</td>
                                    </tr>
                                    <tr>
                                        <td>3</td>
                                        <td>
                                            <b>LED</b> <br />
                                            80cm (32) HD Ready LED TV
                                        </td>
                                        <td>2</td>
                                        <td>$412.00</td>
                                        <td class="text-end">$824.00</td>
                                    </tr>

                                </tbody>
                            </table>
                        </div> <!-- end table-responsive-->
                    </b-col> <!-- end col -->
                </b-row>
                <!-- end row -->

                <b-row>
                    <b-col sm="6">
                        <div class="clearfix pt-3">
                            <h6 class="text-muted">Notes:</h6>
                            <small>
                                All accounts are to be paid within 7 days from receipt of
                                invoice. To be paid by cheque or credit card or direct payment
                                online. If account is not paid within 7 days the credits details
                                supplied as confirmation of work undertaken will be charged the
                                agreed quoted fee noted above.
                            </small>
                        </div>
                    </b-col> <!-- end col -->
                    <b-col sm="6">
                        <div class="float-end mt-3 mt-sm-0">
                            <p><b>Sub-total:</b> <span class="float-end">$4120.00</span></p>
                            <p><b>VAT (12.5):</b> <span class="float-end">$515.00</span></p>
                            <h3>$4635.00 USD</h3>
                        </div>
                        <div class="clearfix"></div>
                    </b-col> <!-- end col -->
                </b-row>
                <!-- end row-->

                <div class="d-print-none mt-4">
                    <div class="text-end">
                        <a href="javascript:window.print()" class="btn btn-primary"><i class="mdi mdi-printer"></i> Print</a>
                        <a href="javascript: void(0);" class="btn btn-info">Submit</a>
                    </div>
                </div>
                <!-- end buttons -->

            </b-card> <!-- end card -->
        </b-col> <!-- end col-->
    </b-row>
    <!-- end row -->
</Layout>
</template>

<script>
import Layout from '@/components/layouts/layout.vue'
import Breadcrumb from '@/components/breadcrumb.vue'
export default {
    components: { Layout, Breadcrumb },
    data() {
        return {
            title: 'Invoice',
            items: [{
                    text: 'Hyper',
                    href: '/',
                },
                {
                    text: 'Pages',
                    href: '/',
                },
                {
                    text: 'Invoice',
                    active: true,
                },
            ],
        }
    },
}
</script>
ś
