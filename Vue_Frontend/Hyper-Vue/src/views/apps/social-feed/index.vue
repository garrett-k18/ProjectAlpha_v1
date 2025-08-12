<template xmlns="">
  <Layout>
    <Breadcrumb :title="title" :items="items" />
    <b-row>
      <b-col xl="3" lg="6" class="order-lg-1 order-xl-1">
        <!-- start profile info -->
        <div class="card">
          <div class="card-body">
            <b-dropdown
              class="float-end"
              variant="white"
              right
              toggle-class="arrow-none card-drop p-0"
            >
              <template v-slot:button-content>
                <i class="mdi mdi-dots-horizontal"></i>
              </template>

              <b-dropdown-item href="javascript:void(0);"
                >Edit Profile</b-dropdown-item
              >

              <b-dropdown-item href="javascript:void(0);"
                >Settings</b-dropdown-item
              >
            </b-dropdown>
            <div class="d-flex align-self-start">
              <img
                class="d-flex align-self-start rounded me-2"
                src="@/assets/images/users/avatar-5.jpg"
                alt="Dominic Keller"
                height="48"
              />
              <div class="w-100 overflow-hidden">
                <h5 class="mt-1 mb-0">Dominic Keller</h5>
                <p class="mb-1 mt-1 text-muted">California, USA</p>
              </div>
            </div>

            <div class="list-group list-group-flush mt-2">
              <a
                href="javascript:void(0);"
                class="list-group-item list-group-item-action text-primary border-0"
              >
                <i class="uil uil-images me-1"></i> News Feed
              </a>
              <a
                href="javascript:void(0);"
                class="list-group-item list-group-item-action border-0"
              >
                <i class="uil uil-comment-alt-message me-1"></i> Messages
              </a>
              <a
                href="javascript:void(0);"
                class="list-group-item list-group-item-action border-0"
              >
                <i class="uil uil-calendar-alt me-1"></i> Events
              </a>
              <a
                href="javascript:void(0);"
                class="list-group-item list-group-item-action border-0"
              >
                <i class="uil uil-users-alt me-1"></i> Groups
              </a>
              <a
                href="javascript:void(0);"
                class="list-group-item list-group-item-action border-0"
              >
                <i class="uil uil-copy me-1"></i> Pages
              </a>
            </div>
          </div>
        </div>
        <!-- end profile info -->

        <!-- event info -->
        <div class="card">
          <div class="card-body p-2">
            <div class="list-group list-group-flush my-2">
              <a
                href="javascript:void(0);"
                class="list-group-item list-group-item-action border-0"
              >
                <i class="uil uil-calendar-alt me-1"></i> 3 events this week
              </a>
              <a
                href="javascript:void(0);"
                class="list-group-item list-group-item-action border-0"
              >
                <i class="uil uil-calender me-1"></i> Eva's birthday today
              </a>
              <a
                href="javascript:void(0);"
                class="list-group-item list-group-item-action border-0"
              >
                <i class="uil uil-bookmark me-1"></i> Jenny's wedding tomorrow
              </a>
            </div>
          </div>
        </div>
        <!-- end event info -->

        <!-- news -->
        <div class="card">
          <div class="card-body">
            <div class="d-flex justify-content-between align-items-center mb-2">
              <h4 class="header-title">Trending</h4>
              <b-dropdown
                class="float-end"
                toggle-class="arrow-none card-drop p-0"
                right
                variant="black"
              >
                <template v-slot:button-content>
                  <i class="mdi mdi-dots-horizontal"></i>
                </template>

                <b-dropdown-item href="javascript:void(0);"
                  >Today</b-dropdown-item
                >

                <b-dropdown-item href="javascript:void(0);"
                  >Yesterday</b-dropdown-item
                >

                <b-dropdown-item href="javascript:void(0);"
                  >Last Week</b-dropdown-item
                >

                <b-dropdown-item href="javascript:void(0);"
                  >Last Month</b-dropdown-item
                >
              </b-dropdown>
            </div>

            <div class="d-flex mt-3">
              <i class="uil uil-arrow-growth me-2 font-18 text-primary"></i>
              <div>
                <a class="mt-1 font-14" href="javascript:void(0);">
                  <strong>Golden Globes:</strong>
                  <span class="text-muted">
                    The 27 Best moments from the Golden Globe Awards
                  </span>
                </a>
              </div>
            </div>

            <div class="d-flex mt-3">
              <i class="uil uil-arrow-growth me-2 font-18 text-primary"></i>
              <div>
                <a class="mt-1 font-14" href="javascript:void(0);">
                  <strong>World Cricket:</strong>
                  <span class="text-muted">
                    India has won ICC T20 World Cup Yesterday
                  </span>
                </a>
              </div>
            </div>

            <div class="d-flex mt-3">
              <i class="uil uil-arrow-growth me-2 font-18 text-primary"></i>
              <div>
                <a class="mt-1 font-14" href="javascript:void(0);">
                  <strong>Antartica:</strong>
                  <span class="text-muted">
                    Metling of Totten Glacier could cause high risk to areas
                    near by sea
                  </span>
                </a>
              </div>
            </div>
          </div>
          <!-- end card-body-->
        </div>
        <!-- end card-->
      </b-col>
      <!-- end col -->

      <b-col xl="6" lg="12" class="order-lg-2 order-xl-1">
        <!-- new post -->
        <div class="card">
          <div class="card-body p-0">
            <b-tabs nav-class="nav-tabs nav-bordered" content-class="p-3">
              <b-tab title-link-class="px-3 py-2">
                <template v-slot:title>
                  <i
                    class="mdi mdi-pencil-box-multiple font-18 d-md-none d-block"
                  ></i>
                  <span class="d-none d-sm-inline-block">Create Post</span>
                </template>
                <div class="border rounded">
                  <form action="#" class="comment-area-box">
                    <textarea
                      rows="4"
                      class="form-control border-0 resize-none"
                      placeholder="Write something...."
                    ></textarea>
                    <div
                      class="p-2 bg-light d-flex justify-content-between align-items-center"
                    >
                      <div>
                        <a href="#" class="btn btn-sm px-2 font-16 btn-light">
                          <i class="uil uil-scenery"></i>
                        </a>
                        <a href="#" class="btn btn-sm px-2 font-16 btn-light">
                          <i class="uil uil-location"></i>
                        </a>
                        <a href="#" class="btn btn-sm px-2 font-16 btn-light">
                          <i class="uil uil-paperclip"></i>
                        </a>
                      </div>
                      <button type="submit" class="btn btn-sm btn-success">
                        <i class="uil uil-message me-1"></i>Post
                      </button>
                    </div>
                  </form>
                </div>
              </b-tab>
              <b-tab title-link-class="px-3 py-2">
                <template v-slot:title>
                  <i class="mdi mdi-image font-18 d-md-none d-block"></i>
                  <span class="d-none d-md-block">Photos/Videos</span>
                </template>
                <div class="border rounded">
                  <form action="#" class="comment-area-box">
                    <textarea
                      rows="4"
                      class="form-control border-0 resize-none"
                      placeholder="Write something...."
                    ></textarea>
                    <div
                      class="p-2 bg-light d-flex justify-content-between align-items-center"
                    >
                      <div>
                        <a href="#" class="btn btn-sm px-2 font-16 btn-light">
                          <i class="uil uil-scenery"></i>
                        </a>
                        <a href="#" class="btn btn-sm px-2 font-16 btn-light">
                          <i class="uil uil-location"></i>
                        </a>
                        <a href="#" class="btn btn-sm px-2 font-16 btn-light">
                          <i class="uil uil-paperclip"></i>
                        </a>
                      </div>
                      <button type="submit" class="btn btn-sm btn-success">
                        <i class="uil uil-message me-1"></i>Post
                      </button>
                    </div>
                  </form>
                </div>
              </b-tab>
              <b-tab title-link-class="px-3 py-2">
                <template v-slot:title>
                  <i
                    class="mdi mdi-book-open-variant font-18 d-md-none d-block"
                  ></i>
                  <span class="d-none d-md-block">Story</span>
                </template>
                <div class="border rounded">
                  <form action="#" class="comment-area-box">
                    <textarea
                      rows="4"
                      class="form-control border-0 resize-none"
                      placeholder="Write something...."
                    ></textarea>
                    <div
                      class="p-2 bg-light d-flex justify-content-between align-items-center"
                    >
                      <div>
                        <a href="#" class="btn btn-sm px-2 font-16 btn-light">
                          <i class="uil uil-scenery"></i>
                        </a>
                        <a href="#" class="btn btn-sm px-2 font-16 btn-light">
                          <i class="uil uil-location"></i>
                        </a>
                        <a href="#" class="btn btn-sm px-2 font-16 btn-light">
                          <i class="uil uil-paperclip"></i>
                        </a>
                      </div>
                      <b-button variant="success" size="sm" type="submit">
                        <i class="uil uil-message me-1"></i>Post
                      </b-button>
                    </div>
                  </form>
                </div>
              </b-tab>
            </b-tabs>
            <!-- end tabs -->
          </div>
          <!-- end card-body -->
        </div>
        <!-- end new post -->

        <!-- start news feeds -->
        <div class="card">
          <div class="card-body pb-1">
            <div class="d-flex">
              <img
                class="me-2 rounded"
                src="@/assets/images/users/avatar-3.jpg"
                alt="Generic placeholder image"
                height="32"
              />
              <div class="w-100">
                <b-dropdown
                  class="float-end text-muted"
                  variant="black"
                  right
                  toggle-class="arrow-none card-drop p-0"
                >
                  <template v-slot:button-content>
                    <i class="mdi mdi-dots-horizontal"></i>
                  </template>

                  <b-dropdown-item href="javascript:void(0);"
                    >Edit</b-dropdown-item
                  >

                  <b-dropdown-item href="javascript:void(0);"
                    >Delete</b-dropdown-item
                  >
                </b-dropdown>
                <h5 class="m-0">Jeremy Tomlinson</h5>
                <p class="text-muted">
                  <small>
                    about 2 minuts ago
                    <span class="mx-1">⚬</span>
                    <span>Public</span>
                  </small>
                </p>
              </div>
            </div>

            <hr class="m-0" />

            <div class="font-16 text-center text-dark my-3">
              <i class="mdi mdi-format-quote-open font-20"></i> Leave one wolf
              alive and the sheep are never safe. When people ask you what
              happened here, tell them the North remembers. Tell them winter
              came for House Frey.
            </div>

            <hr class="m-0" />

            <div class="my-1">
              <a
                href="javascript: void(0);"
                class="btn btn-sm btn-link text-muted pl-0"
              >
                <i class="mdi mdi-heart text-danger"></i> 2k Likes
              </a>
              <a
                href="javascript: void(0);"
                class="btn btn-sm btn-link text-muted"
              >
                <i class="uil uil-comments-alt"></i> 200 Comments
              </a>
              <a
                href="javascript: void(0);"
                class="btn btn-sm btn-link text-muted"
              >
                <i class="uil uil-share-alt"></i> Share
              </a>
            </div>

            <hr class="m-0" />

            <div class="mt-3">
              <div class="d-flex">
                <img
                  class="me-2 rounded"
                  src="@/assets/images/users/avatar-9.jpg"
                  alt="Generic placeholder image"
                  height="32"
                />
                <div>
                  <h5 class="m-0">Sansa Stark</h5>
                  <p class="text-muted mb-0">
                    <small>2 mins ago</small>
                  </p>

                  <p class="my-1">
                    This is awesome! Proud of sis :) Waiting for you to come
                    back to winterfall
                  </p>

                  <div>
                    <a
                      href="javascript: void(0);"
                      class="btn btn-sm btn-link text-muted p-0"
                    >
                      <i class="uil uil-heart me-1"></i> Like
                    </a>
                    <a
                      href="javascript: void(0);"
                      class="btn btn-sm btn-link text-muted p-0 pl-2"
                    >
                      <i class="uil uil-comments-alt ms-1"></i> Reply
                    </a>
                  </div>
                  <div class="d-flex mt-3">
                    <img
                      class="me-2 rounded"
                      src="@/assets/images/users/avatar-8.jpg"
                      alt="Generic placeholder image"
                      height="32"
                    />
                    <div>
                      <h5 class="m-0">Cersei Lannister</h5>
                      <p class="text-muted mb-0">
                        <small>1 min ago</small>
                      </p>

                      <p class="my-1">
                        I swear! She won't be able to reach to winterfall
                      </p>
                    </div>
                  </div>
                </div>
              </div>

              <hr />
              <div class="d-flex mb-2">
                <img
                  src="@/assets/images/users/avatar-1.jpg"
                  height="32"
                  class="align-self-start rounded me-2"
                  alt="Arya Stark"
                />
                <div class="w-100">
                  <input
                    type="text"
                    class="form-control border-0 form-control-sm"
                    placeholder="Write a comment"
                  />
                </div>
              </div>
            </div>
          </div>
          <!-- end card-body -->
        </div>
        <!-- end card -->

        <div class="card">
          <div class="card-body pb-1">
            <div class="d-flex">
              <img
                class="me-2 rounded"
                src="@/assets/images/users/avatar-5.jpg"
                alt="Generic placeholder image"
                height="32"
              />

              <div class="w-100">
                <b-dropdown
                  class="float-end text-muted"
                  variant="black"
                  right
                  toggle-class="arrow-none card-drop p-0"
                >
                  <template v-slot:button-content>
                    <i class="mdi mdi-dots-horizontal"></i>
                  </template>

                  <b-dropdown-item href="javascript:void(0);"
                    >Edit</b-dropdown-item
                  >

                  <b-dropdown-item href="javascript:void(0);"
                    >Delete</b-dropdown-item
                  >
                </b-dropdown>
                <h5 class="m-0">Jon Snow</h5>
                <p class="text-muted">
                  <small>
                    20 min ago
                    <span class="mx-1">⚬</span>
                    <span>Public</span>
                  </small>
                </p>
              </div>
            </div>

            <hr class="m-0" />

            <div class="my-3">
              <p>"Feeling awesome at the wall!"</p>
              <b-row>
                <b-col sm="8">
                  <img
                    src="@/assets/images/small/small-4.jpg"
                    alt="post-img"
                    class="rounded me-1 mb-3 mb-sm-0 img-fluid"
                  />
                </b-col>
                <b-col>
                  <img
                    src="@/assets/images/small/small-2.jpg"
                    alt="post-img"
                    class="rounded me-1 img-fluid mb-3"
                  />
                  <img
                    src="@/assets/images/small/small-3.jpg"
                    alt="post-img"
                    class="rounded me-1 img-fluid"
                  />
                </b-col>
              </b-row>
            </div>

            <div class="mt-1 mb-1">
              <a
                href="javascript: void(0);"
                class="btn btn-sm btn-link text-muted pl-0"
              >
                <i class="mdi mdi-heart text-danger"></i> 1.2k Likes
              </a>
              <a
                href="javascript: void(0);"
                class="btn btn-sm btn-link text-muted"
              >
                <i class="uil uil-comments-alt"></i> 148 Comments
              </a>
              <a
                href="javascript: void(0);"
                class="btn btn-sm btn-link text-muted"
              >
                <i class="uil uil-share-alt"></i> Share
              </a>
            </div>
            <hr class="m-0" />

            <div class="mt-3">
              <div class="d-flex">
                <img
                  class="me-2 rounded"
                  src="@/assets/images/users/avatar-9.jpg"
                  alt="Generic placeholder image"
                  height="32"
                />
                <div class="w-100">
                  <h5 class="m-0">Sansa Stark</h5>
                  <p class="text-muted mb-0">
                    <small>2 mins ago</small>
                  </p>

                  <p class="my-1">
                    This is awesome! Proud of sis :) Waiting for you to come
                    back to winterfall
                  </p>

                  <div>
                    <a
                      href="javascript: void(0);"
                      class="btn btn-sm btn-link text-muted p-0"
                    >
                      <i class="uil uil-heart me-1"></i> Like
                    </a>
                    <a
                      href="javascript: void(0);"
                      class="btn btn-sm btn-link text-muted p-0 pl-2"
                    >
                      <i class="uil uil-comments-alt me-1"></i> Reply
                    </a>
                  </div>
                </div>
              </div>

              <hr />
              <div class="d-flex mb-2">
                <img
                  src="@/assets/images/users/avatar-1.jpg"
                  height="32"
                  class="align-self-start rounded me-2"
                  alt="Arya Stark"
                />
                <div class="w-100">
                  <input
                    type="text"
                    class="form-control border-0 form-control-sm"
                    placeholder="Write a comment"
                  />
                </div>
              </div>
            </div>
          </div>
          <!-- end card-body -->
        </div>
        <!-- end card -->
        <!-- end news feeds -->

        <!-- loader -->
        <div class="text-center mb-3">
          <a href="javascript:void(0);" class="text-danger">
            <i class="mdi mdi-spin mdi-loading me-1 font-16"></i> Load more
          </a>
        </div>
        <!-- end loader -->
      </b-col>

      <b-col xl="3" lg="6" class="order-lg-1 order-xl-2">
        <!-- video -->
        <div class="card">
          <div class="card-body">
            <b-dropdown
              class="float-end"
              variant="black"
              right
              toggle-class="arrow-none card-drop p-0"
            >
              <template v-slot:button-content>
                <i class="mdi mdi-dots-horizontal"></i>
              </template>

              <b-dropdown-item href="javascript:void(0);"
                >Today</b-dropdown-item
              >
              <b-dropdown-item href="javascript:void(0);"
                >Yesterday</b-dropdown-item
              >
              <b-dropdown-item href="javascript:void(0);"
                >Last Week</b-dropdown-item
              >
              <b-dropdown-item href="javascript:void(0);"
                >Last Month</b-dropdown-item
              >
            </b-dropdown>

            <h4 class="header-title mb-1">Featured Video For You</h4>

            <div class="mt-3">
              <div class="embed-responsive embed-responsive-16by9">
                <iframe
                  class="embed-responsive-item"
                  src="https://www.youtube.com/embed/9_eqq0HlN9g?autohide=0&showinfo=0&controls=0"
                ></iframe>
              </div>
            </div>
          </div>
          <!-- end card-body -->
        </div>
        <!-- end video -->

        <!-- video -->
        <div class="card">
          <div class="card-body pb-0">
            <b-dropdown
              class="float-end"
              variant="black"
              right
              toggle-class="arrow-none card-drop p-0"
            >
              <template v-slot:button-content>
                <i class="mdi mdi-dots-horizontal"></i>
              </template>

              <b-dropdown-item href="javascript:void(0);"
                >View All</b-dropdown-item
              >
            </b-dropdown>
            <h4 class="header-title mb-3">People you may know</h4>

            <div class="inbox-widget">
              <div class="inbox-item">
                <div class="inbox-item-img">
                  <img
                    src="@/assets/images/users/avatar-2.jpg"
                    class="rounded-circle"
                    alt=""
                  />
                </div>
                <p class="inbox-item-author">Robb Stark</p>
                <p class="inbox-item-text">The first king in the North</p>
                <p class="inbox-item-date">
                  <button
                    type="button"
                    class="btn btn-sm btn-outline-primary px-1 py-0"
                  >
                    <i class="uil uil-user-plus font-16"></i>
                  </button>
                </p>
              </div>
              <div class="inbox-item">
                <div class="inbox-item-img">
                  <img
                    src="@/assets/images/users/avatar-3.jpg"
                    class="rounded-circle"
                    alt=""
                  />
                </div>
                <p class="inbox-item-author">Stillnot David</p>
                <p class="inbox-item-text">Lady of winterfall</p>
                <p class="inbox-item-date">
                  <button
                    type="button"
                    class="btn btn-sm btn-outline-primary px-1 py-0"
                  >
                    <i class="uil uil-user-plus font-16"></i>
                  </button>
                </p>
              </div>
              <div class="inbox-item">
                <div class="inbox-item-img">
                  <img
                    src="@/assets/images/users/avatar-4.jpg"
                    class="rounded-circle"
                    alt=""
                  />
                </div>
                <p class="inbox-item-author">Cersei Lannister</p>
                <p class="inbox-item-text">Queen of the Seven Kingdoms</p>
                <p class="inbox-item-date">
                  <button
                    type="button"
                    class="btn btn-sm btn-outline-primary px-1 py-0"
                  >
                    <i class="uil uil-user-plus font-16"></i>
                  </button>
                </p>
              </div>

              <div class="inbox-item">
                <div class="inbox-item-img">
                  <img
                    src="@/assets/images/users/avatar-5.jpg"
                    class="rounded-circle"
                    alt=""
                  />
                </div>
                <p class="inbox-item-author">Daenerys Targaryen</p>
                <p class="inbox-item-text">Hey! there I'm available...</p>
                <p class="inbox-item-date">
                  <button
                    type="button"
                    class="btn btn-sm btn-outline-primary px-1 py-0"
                  >
                    <i class="uil uil-user-plus font-16"></i>
                  </button>
                </p>
              </div>
              <div class="inbox-item">
                <div class="inbox-item-img">
                  <img
                    src="@/assets/images/users/avatar-6.jpg"
                    class="rounded-circle"
                    alt=""
                  />
                </div>
                <p class="inbox-item-author">Adhamd Annaway</p>
                <p class="inbox-item-text">Queen Daenerys</p>
                <p class="inbox-item-date">
                  <button
                    type="button"
                    class="btn btn-sm btn-outline-primary px-1 py-0"
                  >
                    <i class="uil uil-user-plus font-16"></i>
                  </button>
                </p>
              </div>
            </div>
            <!-- end inbox-widget -->

            <div class="mt-2 mb-3 text-center">
              <a href="">
                View More
                <i class="uil uil-arrow-right ml-1"></i>
              </a>
            </div>
          </div>
          <!-- end card-body -->
        </div>
        <!-- end video -->
      </b-col>
      <!-- end col -->
    </b-row>
    <!--end row -->
  </Layout>
</template>

<script lang="ts">
import Layout from "@/components/layouts/layout.vue";
import Breadcrumb from "@/components/breadcrumb.vue";

export default {
  components: { Breadcrumb, Layout },
  data() {
    return {
      title: "Social",
      items: [
        {
          text: "Hyper",
          href: "/",
        },
        {
          text: "Social",
          href: "/",
        },
        {
          text: "Feed",
          active: true,
        },
      ],
    };
  },
};
</script>
