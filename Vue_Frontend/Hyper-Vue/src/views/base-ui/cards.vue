<template>
<Layout>
    <Breadcrumb :title="title" :items="items" />

    <b-row>
        <b-col sm="6" lg="3">
            <!-- Simple card -->
            <div class="card d-block">
                <img class="card-img-top" src="@/assets/images/small/small-1.jpg" alt="Card image cap">
                <div class="card-body">
                    <h5 class="card-title">Card title</h5>
                    <p class="card-text">Some quick example text to build on the card title and make
                        up the bulk of the card's content. Some quick example text to build on the card title and make up.</p>
                    <a href="javascript: void(0);" class="btn btn-primary">Button</a>
                </div> <!-- end card-body-->
            </div> <!-- end card-->
        </b-col><!-- end col -->

        <b-col sm="6" lg="3">
            <div class="card d-block">
                <img class="card-img-top" src="@/assets/images/small/small-2.jpg" alt="Card image cap">
                <div class="card-body">
                    <h5 class="card-title">Card title</h5>
                    <p class="card-text">Some quick example text to build on the card..</p>
                </div>
                <ul class="list-group list-group-flush">
                    <li class="list-group-item">Cras justo odio</li>
                </ul>
                <div class="card-body">
                    <a href="javascript: void(0);" class="card-link text-custom">Card link</a>
                    <a href="javascript: void(0);" class="card-link text-custom">Another link</a>
                </div> <!-- end card-body-->
            </div> <!-- end card-->
        </b-col><!-- end col -->

        <b-col sm="6" lg="3">
            <div class="card d-block">
                <img class="card-img-top" src="@/assets/images/small/small-3.jpg" alt="Card image cap">
                <div class="card-body">
                    <p class="card-text">Some quick example text to build on the card title and make
                        up the bulk of the card's content. Some quick example text to build on the card title and make up.</p>
                    <a href="javascript: void(0);" class="btn btn-primary">Button</a>
                </div> <!-- end card-body-->
            </div> <!-- end card-->
        </b-col><!-- end col -->

        <b-col sm="6" lg="3">
            <div class="card d-block">
                <div class="card-body">
                    <h5 class="card-title">Card title</h5>
                    <h6 class="card-subtitle text-muted">Support card subtitle</h6>
                </div>
                <img class="img-fluid" src="@/assets/images/small/small-4.jpg" alt="Card image cap">
                <div class="card-body">
                    <p class="card-text">Some quick example text to build on the card title and make
                        up the bulk of the card's content.</p>
                    <a href="javascript: void(0);" class="card-link text-custom">Card link</a>
                    <a href="javascript: void(0);" class="card-link text-custom">Another link</a>
                </div> <!-- end card-body-->
            </div> <!-- end card-->
        </b-col><!-- end col -->
    </b-row>
    <!-- end row -->

    <b-row>
        <b-col sm="6">
            <div class="card card-body">
                <h5 class="card-title">Special title treatment</h5>
                <p class="card-text">With supporting text below as a natural lead-in to additional
                    content.</p>
                <a href="javascript: void(0);" class="btn btn-primary">Go somewhere</a>
            </div> <!-- end card-->
        </b-col> <!-- end col-->
        <b-col sm="6">
            <div class="card card-body">
                <h5 class="card-title">Special title treatment</h5>
                <p class="card-text">With supporting text below as a natural lead-in to additional
                    content.</p>
                <a href="javascript: void(0);" class="btn btn-primary">Go somewhere</a>
            </div> <!-- end card-->
        </b-col> <!-- end col-->
    </b-row>
    <!-- end row -->

    <b-row>
        <b-col md="4">
            <div class="card">
                <h6 class="card-header bg-light">Featured</h6>
                <div class="card-body">
                    <h5 class="card-title">Special title treatment</h5>
                    <p class="card-text">With supporting text below as a natural lead-in to
                        additional content.</p>
                    <a href="javascript: void(0);" class="btn btn-primary">Go somewhere</a>
                </div> <!-- end card-body-->
            </div> <!-- end card-->
        </b-col> <!-- end col-->

        <b-col md="4">
            <div class="card">
                <div class="card-header bg-light">
                    Quote
                </div>
                <div class="card-body">
                    <blockquote class="card-bodyquote">
                        <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Integer posuere
                            erat a ante.</p>
                        <footer>Someone famous in <cite title="Source Title">Source Title</cite>
                        </footer>
                    </blockquote>
                </div> <!-- end card-body-->
            </div> <!-- end card-->
        </b-col> <!-- end col-->

        <b-col md="4">
            <div class="card">
                <div class="card-header bg-light">
                    Featured
                </div>
                <div class="card-body">
                    <a href="javascript: void(0);" class="btn btn-primary">Go somewhere</a>
                </div>
                <div class="card-footer border-top border-light text-muted">
                    2 days ago
                </div>
            </div> <!-- end card-->
        </b-col> <!-- end col-->
    </b-row>
    <!-- end row -->

    <b-row>
        <b-col cols="12">
            <h4 class="mb-4">Card Colored</h4>
        </b-col> <!-- end col -->
    </b-row>
    <!-- end row -->

    <b-row>
        <b-col lg="4" sm="6">
            <div class="card text-bg-secondary">
                <div class="card-body">
                    <h5 class="card-title">Special title treatment</h5>
                    <p class="card-text">With supporting text below as a natural lead-in to
                        additional content.</p>
                    <a href="javascript: void(0);" class="btn btn-primary btn-sm">Button</a>
                </div> <!-- end card-body-->
            </div> <!-- end card-->
        </b-col> <!-- end col-->

        <b-col lg="4" sm="6">
            <div class="card text-bg-primary">
                <div class="card-body">
                    <blockquote class="card-bodyquote">
                        <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Integer posuere
                            erat a ante.</p>
                        <footer>Someone famous in <cite title="Source Title">Source Title</cite>
                        </footer>
                    </blockquote>
                </div> <!-- end card-body-->
            </div> <!-- end card-->
        </b-col> <!-- end col-->

        <b-col lg="4" sm="6">
            <div class="card text-bg-success">
                <div class="card-body">
                    <blockquote class="card-bodyquote">
                        <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Integer posuere
                            erat a ante.</p>
                        <footer>Someone famous in <cite title="Source Title">Source Title</cite>
                        </footer>
                    </blockquote>
                </div> <!-- end card-body-->
            </div> <!-- end card-->
        </b-col> <!-- end col-->

        <b-col lg="4" sm="6">
            <div class="card text-bg-info">
                <div class="card-body">
                    <blockquote class="card-bodyquote mb-0">
                        <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Integer posuere
                            erat a ante.</p>
                        <footer>Someone famous in <cite title="Source Title">Source Title</cite>
                        </footer>
                    </blockquote>
                </div> <!-- end card-body-->
            </div> <!-- end card-->
        </b-col> <!-- end col-->

        <b-col lg="4" sm="6">
            <div class="card text-bg-warning">
                <div class="card-body">
                    <blockquote class="card-bodyquote mb-0">
                        <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Integer posuere
                            erat a ante.</p>
                        <footer>Someone famous in <cite title="Source Title">Source Title</cite>
                        </footer>
                    </blockquote>
                </div> <!-- end card-body-->
            </div> <!-- end card-->
        </b-col> <!-- end col-->

        <b-col lg="4" sm="6">
            <div class="card text-bg-danger">
                <div class="card-body">
                    <blockquote class="card-bodyquote mb-0">
                        <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Integer posuere
                            erat a ante.</p>
                        <footer>Someone famous in <cite title="Source Title">Source Title</cite>
                        </footer>
                    </blockquote>
                </div> <!-- end card-body-->
            </div> <!-- end card-->
        </b-col> <!-- end col-->
    </b-row>
    <!-- end row -->

    <b-row>
        <b-col cols="12">
            <h4 class="mb-4">Card Bordered</h4>
        </b-col> <!-- end col -->
    </b-row>
    <!-- end row -->

    <b-row>
        <b-col md="4">
            <div class="card border-secondary border">
                <div class="card-body">
                    <h5 class="card-title">Special title treatment</h5>
                    <p class="card-text">With supporting text below as a natural lead-in to
                        additional content.</p>
                    <a href="javascript: void(0);" class="btn btn-secondary btn-sm">Button</a>
                </div> <!-- end card-body-->
            </div> <!-- end card-->
        </b-col> <!-- end col-->

        <b-col md="4">
            <div class="card border-primary border">
                <div class="card-body">
                    <h5 class="card-title text-primary">Special title treatment</h5>
                    <p class="card-text">With supporting text below as a natural lead-in to
                        additional content.</p>
                    <a href="javascript: void(0);" class="btn btn-primary btn-sm">Button</a>
                </div> <!-- end card-body-->
            </div> <!-- end card-->
        </b-col> <!-- end col-->

        <b-col md="4">
            <div class="card border-success border">
                <div class="card-body">
                    <h5 class="card-title text-success">Special title treatment</h5>
                    <p class="card-text">With supporting text below as a natural lead-in to
                        additional content.</p>
                    <a href="javascript: void(0);" class="btn btn-success btn-sm">Button</a>
                </div> <!-- end card-body-->
            </div> <!-- end card-->
        </b-col> <!-- end col-->
    </b-row>
    <!-- end row -->

    <b-row>
        <b-col cols="12">
            <h4 class="mb-4">Horizontal Card</h4>
        </b-col> <!-- end col -->
    </b-row>
    <!-- end row -->

    <b-row>
        <b-col lg="6">
            <div class="card">
                <div class="row g-0 align-items-center">
                    <div class="col-md-4">
                        <img src="@/assets/images/small/small-4.jpg" class="img-fluid rounded-start" alt="...">
                    </div>
                    <div class="col-md-8">
                        <div class="card-body">
                            <h5 class="card-title">Card title</h5>
                            <p class="card-text">This is a wider card with supporting text below as a natural lead-in to additional content. This content is a little bit longer.</p>
                            <p class="card-text"><small class="text-muted">Last updated 3 mins ago</small></p>
                        </div> <!-- end card-body-->
                    </div> <!-- end col -->
                </div> <!-- end row-->
            </div> <!-- end card-->
        </b-col> <!-- end col-->
        <b-col lg="6">
            <div class="card">
                <div class="row g-0 align-items-center">
                    <div class="col-md-8">
                        <div class="card-body">
                            <h5 class="card-title">Card title</h5>
                            <p class="card-text">This is a wider card with supporting text below as a natural lead-in to additional content. This content is a little bit longer.</p>
                            <p class="card-text"><small class="text-muted">Last updated 3 mins ago</small></p>
                        </div> <!-- end card-body -->
                    </div> <!-- end col -->
                    <div class="col-md-4">
                        <img src="@/assets/images/small/small-1.jpg" class="img-fluid rounded-end" alt="...">
                    </div> <!-- end col -->
                </div> <!-- end row-->
            </div> <!-- end card -->
        </b-col> <!-- end col-->
    </b-row>
    <!-- end row -->

    <b-row>
        <b-col cols="12">
            <h4 class="mb-4">Stretched link</h4>
        </b-col> <!-- end col -->
    </b-row>
    <!-- end row -->

    <b-row>
        <b-col sm="6" lg="3">
            <div class="card">
                <img src="@/assets/images/small/small-2.jpg" class="card-img-top" alt="...">
                <div class="card-body">
                    <h5 class="card-title">Card with stretched link</h5>
                    <a href="#" class="btn btn-primary mt-2 stretched-link">Go somewhere</a>
                </div> <!-- end card-body -->
            </div> <!-- end card -->
        </b-col> <!-- end col-->
        <b-col sm="6" lg="3">
            <div class="card">
                <img src="@/assets/images/small/small-3.jpg" class="card-img-top" alt="...">
                <div class="card-body">
                    <h5 class="card-title"><a href="#" class="text-success stretched-link">Card with stretched link</a></h5>
                    <p class="card-text">
                        Some quick example text to build on the card up the bulk of the card's content.
                    </p>
                </div> <!-- end card-body -->
            </div> <!-- end card -->
        </b-col> <!-- end col-->
        <b-col sm="6" lg="3">
            <div class="card">
                <img src="@/assets/images/small/small-4.jpg" class="card-img-top" alt="...">
                <div class="card-body">
                    <h5 class="card-title">Card with stretched link</h5>
                    <a href="#" class="btn btn-info mt-2 stretched-link">Go somewhere</a>
                </div> <!-- end card-body -->
            </div> <!-- end card -->
        </b-col> <!-- end col-->
        <b-col sm="6" lg="3">
            <div class="card">
                <img src="@/assets/images/small/small-1.jpg" class="card-img-top" alt="...">
                <div class="card-body">
                    <h5 class="card-title"><a href="#" class="stretched-link">Card with stretched link</a></h5>
                    <p class="card-text">
                        Some quick example text to build on the card up the bulk of the card's content.
                    </p>
                </div> <!-- end card-body -->
            </div> <!-- end card -->
        </b-col> <!-- end col-->
    </b-row>
    <!-- end row -->

    <b-row>
        <b-col cols="12">
            <h4 class="mb-4">Card Group</h4>
        </b-col> <!-- end col -->
    </b-row>
    <!-- end row -->

    <b-row>
        <b-col cols="12">
            <div class="card-group">
                <div class="card d-block">
                    <img class="card-img-top" src="@/assets/images/small/small-1.jpg" alt="Card image cap">
                    <div class="card-body">
                        <h5 class="card-title">Card title</h5>
                        <p class="card-text">This is a wider card with supporting text below as a
                            natural lead-in to additional content. This content is a little bit
                            longer.</p>
                        <p class="card-text">
                            <small class="text-muted">Last updated 3 mins ago</small>
                        </p>
                    </div>
                </div>
                <div class="card d-block">
                    <img class="card-img-top" src="@/assets/images/small/small-2.jpg" alt="Card image cap">
                    <div class="card-body">
                        <h5 class="card-title">Card title</h5>
                        <p class="card-text">This card has supporting text below as a natural
                            lead-in to additional content.</p>
                        <p class="card-text">
                            <small class="text-muted">Last updated 3 mins ago</small>
                        </p>
                    </div>
                </div>
                <div class="card d-block">
                    <img class="card-img-top" src="@/assets/images/small/small-3.jpg" alt="Card image cap">
                    <div class="card-body">
                        <h5 class="card-title">Card title</h5>
                        <p class="card-text">This is a wider card with supporting text below as a
                            natural lead-in to additional content. This card has even longer content
                            than the first to show that equal height action.</p>
                        <p class="card-text">
                            <small class="text-muted">Last updated 3 mins ago</small>
                        </p>
                    </div>
                </div>
            </div> <!-- end card-group-->
        </b-col> <!-- end col-->
    </b-row>
    <!-- end row -->

    <b-row>
        <b-col cols="12">
            <h4 class="my-4">Custom Card Portlets</h4>
        </b-col> <!-- end col -->
    </b-row>
    <!-- end row -->

    <b-row>
        <b-col cols="12">
            <CustomSyntax title="">
                <template v-slot:sub-text>
                </template>
                <template v-slot:preview>
                    <b-row>
                        <b-col md="4">
                            <!-- Portlet card -->
                            <b-card class="mb-md-0 mb-3">
                                <div class="card-widgets">
                                    <a href="javascript:;" data-bs-toggle="reload"><i class="mdi mdi-refresh"></i></a>
                                    <a v-b-toggle="'cardCollpase1'"><i class="mdi mdi-minus"></i></a>
                                    <a href="#" data-bs-toggle="remove"><i class="ri-close-line"></i></a>
                                </div>
                                <h5 class="card-title mb-0">Card title</h5>

                                <b-collapse id="cardCollpase1" class="pt-3 show">
                                    Anim pariatur cliche reprehenderit, enim eiusmod high life accusamus terry richardson ad squid. 3 wolf moon officia aute,
                                    non cupidatat skateboard dolor brunch. Food truck quinoa nesciunt laborum eiusmod. Brunch 3 wolf moon tempor, sunt aliqua
                                    put a bird on it squid single-origin coffee nulla assumenda shoreditch et. Nihil anim keffiyeh helvetica, craft beer
                                    labore wes anderson cred nesciunt sapiente ea proident. Ad vegan excepteur butcher vice lomo. Leggings occaecat craft
                                    beer farm-to-table, raw denim aesthetic synth nesciunt you probably haven't heard of them accusamus labore sustainable
                                    VHS.
                                </b-collapse>
                            </b-card> <!-- end card-->
                        </b-col><!-- end col -->

                        <b-col md="4">
                            <!-- Portlet card -->
                            <b-card class="bg-primary text-white mb-md-0 mb-3">
                                <div class="card-widgets">
                                    <a href="javascript:;" data-bs-toggle="reload"><i class="mdi mdi-refresh"></i></a>
                                    <a data-bs-toggle="collapse" href="#cardCollpase2" role="button" aria-expanded="false" aria-controls="cardCollpase2"><i class="mdi mdi-minus"></i></a>
                                    <a href="#" data-bs-toggle="remove"><i class="mdi mdi-close"></i></a>
                                </div>
                                <h5 class="card-title mb-0">Card title</h5>

                                <div id="cardCollpase2" class="collapse pt-3 show">
                                    Anim pariatur cliche reprehenderit, enim eiusmod high life accusamus terry richardson ad squid. 3 wolf moon officia aute,
                                    non cupidatat skateboard dolor brunch. Food truck quinoa nesciunt laborum eiusmod. Brunch 3 wolf moon tempor, sunt aliqua
                                    put a bird on it squid single-origin coffee nulla assumenda shoreditch et. Nihil anim keffiyeh helvetica, craft beer
                                    labore wes anderson cred nesciunt sapiente ea proident. Ad vegan excepteur butcher vice lomo. Leggings occaecat craft
                                    beer farm-to-table, raw denim aesthetic synth nesciunt you probably haven't heard of them accusamus labore sustainable
                                    VHS.
                                </div>
                            </b-card> <!-- end card-->
                        </b-col><!-- end col -->

                        <b-col md="4">
                            <!-- Portlet card -->
                            <b-card class="bg-success text-white mb-0">
                                <div class="card-widgets">
                                    <a href="javascript:;" data-bs-toggle="reload"><i class="mdi mdi-refresh"></i></a>
                                    <a data-bs-toggle="collapse" href="#cardCollpase3" role="button" aria-expanded="false" aria-controls="cardCollpase3"><i class="mdi mdi-minus"></i></a>
                                    <a href="#" data-bs-toggle="remove"><i class="mdi mdi-close"></i></a>
                                </div>
                                <h5 class="card-title mb-0">Card title</h5>

                                <div id="cardCollpase3" class="collapse pt-3 show">
                                    Anim pariatur cliche reprehenderit, enim eiusmod high life accusamus terry richardson ad squid. 3 wolf moon officia aute,
                                    non cupidatat skateboard dolor brunch. Food truck quinoa nesciunt laborum eiusmod. Brunch 3 wolf moon tempor, sunt aliqua
                                    put a bird on it squid single-origin coffee nulla assumenda shoreditch et. Nihil anim keffiyeh helvetica, craft beer
                                    labore wes anderson cred nesciunt sapiente ea proident. Ad vegan excepteur butcher vice lomo. Leggings occaecat craft
                                    beer farm-to-table, raw denim aesthetic synth nesciunt you probably haven't heard of them accusamus labore sustainable
                                    VHS.
                                </div>
                            </b-card> <!-- end card-->
                        </b-col><!-- end col -->
                    </b-row>
                    <!-- end row -->
                </template>
            </CustomSyntax>
        </b-col> <!-- end col -->
    </b-row>
    <!-- end row -->
</Layout>
</template>

<script lang="ts">
import Layout from "@/components/layouts/layout.vue";
import Breadcrumb from "@/components/breadcrumb.vue";
import CustomSyntax from "@/components/custom/custom-syntax.vue";
export default {
    components: { Layout, Breadcrumb, CustomSyntax },
  data() {
    return {
      title: 'Cards',
      items: [
        {
          text: 'Hyper',
          href: '/',
        },
        {
          text: 'Base UI',
          href: '/',
        },
        {
          text: 'Cards',
          active: true,
        },
      ],
    }
  },
}
</script>
