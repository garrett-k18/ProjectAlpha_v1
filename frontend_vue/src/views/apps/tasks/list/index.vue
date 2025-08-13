<template>
  <Layout>
    <b-row>
      <b-col xxl="8">
        <!-- start page title -->
        <div class="page-title-box">
          <div class="page-title-right">

            <b-form>
              <div class="input-group">
                <input type="text" class="form-control" placeholder="Search..."/>

                <b-dropdown variant="secondary" right>
                  <template v-slot:button-content>
                      <i class='uil uil-sort-amount-down'></i>
                  </template>
                  <b-dropdown-item href="javascript: void(0);">Due Date</b-dropdown-item>
                  <b-dropdown-item href="javascript: void(0);">Added Date</b-dropdown-item>
                  <b-dropdown-item href="javascript: void(0);">Assignee</b-dropdown-item>
                </b-dropdown>
              </div>
            </b-form>
          </div>
          <h4 class="page-title">Tasks <a href="#" class="btn btn-success btn-sm ms-3">Add New</a></h4>
        </div>
        <!-- end page title -->

        <Panel/>
        <!-- end row -->
      </b-col>
      <!-- end col -->
      <b-col xxl="4">
        <Detail/>
      </b-col>
    </b-row>
    <!-- end row -->
  </Layout>
</template>

<script lang="ts">
import Layout from "@/components/layouts/layout.vue";
import Panel from "@/views/apps/tasks/list/panel.vue";
import Detail from "@/views/apps/tasks/list/detail.vue";


export default {
  components: {Detail, Panel, Layout,},
  mounted() {
    this.useMeta({
      title: "Tasks",
    });
  }
}
</script>