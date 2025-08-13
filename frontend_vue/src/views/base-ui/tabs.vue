<template>
  <Layout>
    <Breadcrumb :title="title" :items="items"/>

    <b-row>
      <b-col xl="6">
        <CustomSyntax title="Default Tabs">
          <template v-slot:sub-text>
            Simple widget of tabbable panes of local content.
          </template>
          <template v-slot:preview>
            <b-tabs content-class="mt-3">
              <b-tab title="Home" id="home">
                <p>
                  Food truck quinoa dolor sit amet, consectetuer adipiscing elit.
                  Aenean commodo ligula eget dolor. Aenean massa. Cum sociis
                  natoque penatibus et magnis dis parturient montes, nascetur
                  ridiculus mus. Donec quam felis, ultricies nec, pellentesque eu,
                  pretium quis, sem. Nulla consequat massa quis enim.
                </p>
                <p class="mb-0">
                  Donec pede justo, fringilla vel, aliquet nec, vulputate eget,
                  arcu. In enim justo, rhoncus ut, imperdiet a, venenatis vitae,
                  justo. Nullam dictum felis eu pede mollis pretium. Integer
                  tincidunt.Cras dapibus. Vivamus elementum semper nisi. Aenean
                  vulputate eleifend tellus. Aenean leo ligula, porttitor eu,
                  consequat vitae, eleifend ac, enim.
                </p>
              </b-tab>
              <b-tab title="Profile" active id="profile">
                <p>
                  Donec pede justo, fringilla vel, aliquet nec, vulputate eget,
                  arcu. In enim justo, rhoncus ut, imperdiet a, venenatis vitae,
                  justo. Nullam dictum felis eu pede mollis pretium. Integer
                  tincidunt.Cras dapibus. Vivamus elementum semper nisi. Aenean
                  vulputate eleifend tellus. Aenean leo ligula, porttitor eu,
                  consequat vitae, eleifend ac, enim.
                </p>
                <p class="mb-0">
                  Food truck quinoa dolor sit amet, consectetuer adipiscing elit.
                  Aenean commodo ligula eget dolor. Aenean massa. Cum sociis
                  natoque penatibus et magnis dis parturient montes, nascetur
                  ridiculus mus. Donec quam felis, ultricies nec, pellentesque eu,
                  pretium quis, sem. Nulla consequat massa quis enim.
                </p>
              </b-tab>
              <b-tab title="Settings" id="settings">
                <p>
                  Food truck quinoa dolor sit amet, consectetuer adipiscing elit.
                  Aenean commodo ligula eget dolor. Aenean massa. Cum sociis
                  natoque penatibus et magnis dis parturient montes, nascetur
                  ridiculus mus. Donec quam felis, ultricies nec, pellentesque eu,
                  pretium quis, sem. Nulla consequat massa quis enim.
                </p>
                <p class="mb-0">
                  Donec pede justo, fringilla vel, aliquet nec, vulputate eget,
                  arcu. In enim justo, rhoncus ut, imperdiet a, venenatis vitae,
                  justo. Nullam dictum felis eu pede mollis pretium. Integer
                  tincidunt.Cras dapibus. Vivamus elementum semper nisi. Aenean
                  vulputate eleifend tellus. Aenean leo ligula, porttitor eu,
                  consequat vitae, eleifend ac, enim.
                </p>
              </b-tab>
            </b-tabs>
          </template>
        </CustomSyntax>

      </b-col> <!-- end col -->

      <b-col xl="6">
        <CustomSyntax title="Tabs Justified">
          <template v-slot:sub-text>
            Using class <code>.nav-justified</code>, you can force your <code>tab menu items</code> to use the full
            available width.
          </template>
          <template v-slot:preview>
            <b-tabs justified pills content-class="mt-3" nav-class="bg-light">
              <b-tab title="Home" id="home1">
                <p>
                  Leggings occaecat dolor sit amet, consectetuer adipiscing elit.
                  Aenean commodo ligula eget dolor. Aenean massa. Cum sociis
                  natoque penatibus et magnis dis parturient montes, nascetur
                  ridiculus mus. Donec quam felis, ultricies nec, pellentesque eu,
                  pretium quis, sem. Nulla consequat massa quis enim.
                </p>
                <p class="mb-0">
                  Donec pede justo, fringilla vel, aliquet nec, vulputate eget,
                  arcu. In enim justo, rhoncus ut, imperdiet a, venenatis vitae,
                  justo. Nullam dictum felis eu pede mollis pretium. Integer
                  tincidunt.Cras dapibus. Vivamus elementum semper nisi. Aenean
                  vulputate eleifend tellus. Aenean leo ligula, porttitor eu,
                  consequat vitae, eleifend ac, enim.
                </p>
              </b-tab>
              <b-tab title="Profile" active id="profile1">
                <p>
                  Donec pede justo, fringilla vel, aliquet nec, vulputate eget,
                  arcu. In enim justo, rhoncus ut, imperdiet a, venenatis vitae,
                  justo. Nullam dictum felis eu pede mollis pretium. Integer
                  tincidunt.Cras dapibus. Vivamus elementum semper nisi. Aenean
                  vulputate eleifend tellus. Aenean leo ligula, porttitor eu,
                  consequat vitae, eleifend ac, enim.
                </p>
                <p class="mb-0">
                  Leggings occaecat dolor sit amet, consectetuer adipiscing elit.
                  Aenean commodo ligula eget dolor. Aenean massa. Cum sociis
                  natoque penatibus et magnis dis parturient montes, nascetur
                  ridiculus mus. Donec quam felis, ultricies nec, pellentesque eu,
                  pretium quis, sem. Nulla consequat massa quis enim.
                </p>
              </b-tab>
              <b-tab title="Settings" id="settings1">
                <p>
                  Food truck quinoa dolor sit amet, consectetuer adipiscing elit.
                  Aenean commodo ligula eget dolor. Aenean massa. Cum sociis
                  natoque penatibus et magnis dis parturient montes, nascetur
                  ridiculus mus. Donec quam felis, ultricies nec, pellentesque eu,
                  pretium quis, sem. Nulla consequat massa quis enim.
                </p>
                <p class="mb-0">
                  Donec pede justo, fringilla vel, aliquet nec, vulputate eget,
                  arcu. In enim justo, rhoncus ut, imperdiet a, venenatis vitae,
                  justo. Nullam dictum felis eu pede mollis pretium. Integer
                  tincidunt.Cras dapibus. Vivamus elementum semper nisi. Aenean
                  vulputate eleifend tellus. Aenean leo ligula, porttitor eu,
                  consequat vitae, eleifend ac, enim.
                </p>
              </b-tab>
            </b-tabs>
          </template>
        </CustomSyntax>

      </b-col> <!-- end col -->
    </b-row>
    <!-- end row -->

    <b-row>
      <b-col xl="6">
        <CustomSyntax title="Tabs Vertical Left">
          <template v-slot:sub-text>
            You can stack your navigation by changing the flex item direction with the <code>.flex-column</code>
            utility.
          </template>
          <template v-slot:preview>
            <b-row>
              <b-tabs pills vertical>
                <b-tab title="Home" active id="v-pills-home">
                  <p class="mb-0">
                    Cillum ad ut irure tempor velit nostrud occaecat ullamco
                    aliqua anim Leggings sint. Veniam sint duis incididunt do esse
                    magna mollit excepteur laborum qui. Id id reprehenderit sit
                    est eu aliqua occaecat quis et velit excepteur laborum mollit
                    dolore eiusmod. Ipsum dolor in occaecat commodo et voluptate
                    minim reprehenderit mollit pariatur. Deserunt non laborum enim
                    et cillum eu deserunt excepteur ea incididunt minim occaecat.
                  </p>
                </b-tab>
                <b-tab title="Profile" id="v-pills-profile">
                  <p class="mb-0">
                    Culpa dolor voluptate do laboris laboris irure reprehenderit
                    id incididunt duis pariatur mollit aute magna pariatur
                    consectetur. Eu veniam duis non ut dolor deserunt commodo et
                    minim in quis laboris ipsum velit id veniam. Quis ut
                    consectetur adipisicing officia excepteur non sit. Ut et elit
                    aliquip labore Leggings enim eu. Ullamco mollit occaecat
                    dolore ipsum id officia mollit qui esse anim eiusmod do sint
                    minim consectetur qui.
                  </p>
                </b-tab>
                <b-tab title="Settings" id="v-pills-settings">
                  <p class="mb-0">
                    Food truck quinoa dolor sit amet, consectetuer adipiscing
                    elit. Aenean commodo ligula eget dolor. Aenean massa. Cum
                    sociis natoque penatibus et magnis dis parturient montes,
                    nascetur ridiculus mus. Donec quam felis, ultricies nec,
                    pellentesque eu, pretium quis, sem. Nulla consequat massa quis
                    enim. Cillum ad ut irure tempor velit nostrud occaecat ullamco
                    aliqua anim Leggings sint. Veniam sint duis incididunt do esse
                    magna mollit excepteur laborum qui.
                  </p>
                </b-tab>
              </b-tabs>
            </b-row>
            <!-- end row-->
          </template>
        </CustomSyntax>

      </b-col> <!-- end col -->

      <b-col xl="6">
        <CustomSyntax title="Tabs Vertical Right">
          <template v-slot:sub-text>
            You can stack your navigation by changing the flex item direction with the <code>.flex-column</code>
            utility.
          </template>
          <template v-slot:preview>
            <b-row>
              <b-tabs pills vertical end>
                <b-tab title="Home" active id="v-pills-home">
                  <p class="mb-0">
                    Cillum ad ut irure tempor velit nostrud occaecat ullamco
                    aliqua anim Leggings sint. Veniam sint duis incididunt do esse
                    magna mollit excepteur laborum qui. Id id reprehenderit sit
                    est eu aliqua occaecat quis et velit excepteur laborum mollit
                    dolore eiusmod. Ipsum dolor in occaecat commodo et voluptate
                    minim reprehenderit mollit pariatur. Deserunt non laborum enim
                    et cillum eu deserunt excepteur ea incididunt minim occaecat.
                  </p>
                </b-tab>
                <b-tab title="Profile" id="v-pills-profile">
                  <p class="mb-0">
                    Culpa dolor voluptate do laboris laboris irure reprehenderit
                    id incididunt duis pariatur mollit aute magna pariatur
                    consectetur. Eu veniam duis non ut dolor deserunt commodo et
                    minim in quis laboris ipsum velit id veniam. Quis ut
                    consectetur adipisicing officia excepteur non sit. Ut et elit
                    aliquip labore Leggings enim eu. Ullamco mollit occaecat
                    dolore ipsum id officia mollit qui esse anim eiusmod do sint
                    minim consectetur qui.
                  </p>
                </b-tab>
                <b-tab title="Settings" id="v-pills-settings">
                  <p class="mb-0">
                    Food truck quinoa dolor sit amet, consectetuer adipiscing
                    elit. Aenean commodo ligula eget dolor. Aenean massa. Cum
                    sociis natoque penatibus et magnis dis parturient montes,
                    nascetur ridiculus mus. Donec quam felis, ultricies nec,
                    pellentesque eu, pretium quis, sem. Nulla consequat massa quis
                    enim. Cillum ad ut irure tempor velit nostrud occaecat ullamco
                    aliqua anim Leggings sint. Veniam sint duis incididunt do esse
                    magna mollit excepteur laborum qui.
                  </p>
                </b-tab>
              </b-tabs>
            </b-row>
          </template>
        </CustomSyntax>

      </b-col> <!-- end col -->
    </b-row>
    <!-- end row -->

    <b-row>
      <b-col xl="6">
        <CustomSyntax title="Tabs Bordered">
          <template v-slot:sub-text>
            The navigation item can have a simple bottom border as well. Just specify the class
            <code>.nav-bordered</code>.
          </template>
          <template v-slot:preview>
            <b-tabs content-class="mt-3">
              <b-tab title="Home" id="home-b1">
                <p>
                  Leggings occaecat dolor sit amet, consectetuer adipiscing elit.
                  Aenean commodo ligula eget dolor. Aenean massa. Cum sociis
                  natoque penatibus et magnis dis parturient montes, nascetur
                  ridiculus mus. Donec quam felis, ultricies nec, pellentesque eu,
                  pretium quis, sem. Nulla consequat massa quis enim.
                </p>
                <p class="mb-0">
                  Donec pede justo, fringilla vel, aliquet nec, vulputate eget,
                  arcu. In enim justo, rhoncus ut, imperdiet a, venenatis vitae,
                  justo. Nullam dictum felis eu pede mollis pretium. Integer
                  tincidunt.Cras dapibus. Vivamus elementum semper nisi. Aenean
                  vulputate eleifend tellus. Aenean leo ligula, porttitor eu,
                  consequat vitae, eleifend ac, enim.
                </p>
              </b-tab>
              <b-tab title="Profile" active id="profile-b1">
                <p>
                  Donec pede justo, fringilla vel, aliquet nec, vulputate eget,
                  arcu. In enim justo, rhoncus ut, imperdiet a, venenatis vitae,
                  justo. Nullam dictum felis eu pede mollis pretium. Integer
                  tincidunt.Cras dapibus. Vivamus elementum semper nisi. Aenean
                  vulputate eleifend tellus. Aenean leo ligula, porttitor eu,
                  consequat vitae, eleifend ac, enim.
                </p>
                <p class="mb-0">
                  Leggings occaecat dolor sit amet, consectetuer adipiscing elit.
                  Aenean commodo ligula eget dolor. Aenean massa. Cum sociis
                  natoque penatibus et magnis dis parturient montes, nascetur
                  ridiculus mus. Donec quam felis, ultricies nec, pellentesque eu,
                  pretium quis, sem. Nulla consequat massa quis enim.
                </p>
              </b-tab>
              <b-tab title="Settings" id="settings-b1">
                <p>
                  Food truck quinoa dolor sit amet, consectetuer adipiscing elit.
                  Aenean commodo ligula eget dolor. Aenean massa. Cum sociis
                  natoque penatibus et magnis dis parturient montes, nascetur
                  ridiculus mus. Donec quam felis, ultricies nec, pellentesque eu,
                  pretium quis, sem. Nulla consequat massa quis enim.
                </p>
                <p class="mb-0">
                  Donec pede justo, fringilla vel, aliquet nec, vulputate eget,
                  arcu. In enim justo, rhoncus ut, imperdiet a, venenatis vitae,
                  justo. Nullam dictum felis eu pede mollis pretium. Integer
                  tincidunt.Cras dapibus. Vivamus elementum semper nisi. Aenean
                  vulputate eleifend tellus. Aenean leo ligula, porttitor eu,
                  consequat vitae, eleifend ac, enim.
                </p>
              </b-tab>
            </b-tabs>
          </template>
        </CustomSyntax>

      </b-col> <!-- end col -->

      <b-col xl="6">
        <CustomSyntax title="Tabs Bordered Justified">
          <template v-slot:sub-text>
            The navigation item with a simple bottom border and justified
          </template>
          <template v-slot:preview>
            <b-tabs content-class="mt-3" justified>
              <b-tab title="Home" id="home-b1">
                <p>
                  Leggings occaecat dolor sit amet, consectetuer adipiscing elit.
                  Aenean commodo ligula eget dolor. Aenean massa. Cum sociis
                  natoque penatibus et magnis dis parturient montes, nascetur
                  ridiculus mus. Donec quam felis, ultricies nec, pellentesque eu,
                  pretium quis, sem. Nulla consequat massa quis enim.
                </p>
                <p class="mb-0">
                  Donec pede justo, fringilla vel, aliquet nec, vulputate eget,
                  arcu. In enim justo, rhoncus ut, imperdiet a, venenatis vitae,
                  justo. Nullam dictum felis eu pede mollis pretium. Integer
                  tincidunt.Cras dapibus. Vivamus elementum semper nisi. Aenean
                  vulputate eleifend tellus. Aenean leo ligula, porttitor eu,
                  consequat vitae, eleifend ac, enim.
                </p>
              </b-tab>
              <b-tab title="Profile" active id="profile-b1">
                <p>
                  Donec pede justo, fringilla vel, aliquet nec, vulputate eget,
                  arcu. In enim justo, rhoncus ut, imperdiet a, venenatis vitae,
                  justo. Nullam dictum felis eu pede mollis pretium. Integer
                  tincidunt.Cras dapibus. Vivamus elementum semper nisi. Aenean
                  vulputate eleifend tellus. Aenean leo ligula, porttitor eu,
                  consequat vitae, eleifend ac, enim.
                </p>
                <p class="mb-0">
                  Leggings occaecat dolor sit amet, consectetuer adipiscing elit.
                  Aenean commodo ligula eget dolor. Aenean massa. Cum sociis
                  natoque penatibus et magnis dis parturient montes, nascetur
                  ridiculus mus. Donec quam felis, ultricies nec, pellentesque eu,
                  pretium quis, sem. Nulla consequat massa quis enim.
                </p>
              </b-tab>
              <b-tab title="Settings" id="settings-b1">
                <p>
                  Food truck quinoa dolor sit amet, consectetuer adipiscing elit.
                  Aenean commodo ligula eget dolor. Aenean massa. Cum sociis
                  natoque penatibus et magnis dis parturient montes, nascetur
                  ridiculus mus. Donec quam felis, ultricies nec, pellentesque eu,
                  pretium quis, sem. Nulla consequat massa quis enim.
                </p>
                <p class="mb-0">
                  Donec pede justo, fringilla vel, aliquet nec, vulputate eget,
                  arcu. In enim justo, rhoncus ut, imperdiet a, venenatis vitae,
                  justo. Nullam dictum felis eu pede mollis pretium. Integer
                  tincidunt.Cras dapibus. Vivamus elementum semper nisi. Aenean
                  vulputate eleifend tellus. Aenean leo ligula, porttitor eu,
                  consequat vitae, eleifend ac, enim.
                </p>
              </b-tab>
            </b-tabs>
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
  components: {Layout, CustomSyntax, Breadcrumb},
  data() {
    return {
      title: 'Tabs',
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
          text: 'Tabs',
          active: true,
        },
      ],
    }
  },
}
</script>
