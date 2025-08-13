<template>
<Layout>
    <Breadcrumb :title="title" :items="items" />

    <b-row>
        <b-col xl="6">
            <CustomSyntax title="Simple Popover">
                <template v-slot:sub-text>
                    Popover is a component which displays a box with a content after a click on an
                    element - similar to the tooltip but can contain more content.
                </template>
                <template v-slot:preview>
                    <b-button variant="danger" v-b-popover.click.right="`And here's some amazing content. It's very engaging. Right?`" title="Popover title">Click to toggle
                        popover</b-button>
                </template>
            </CustomSyntax>

            <CustomSyntax title="Dismiss on Next Click">
                <template v-slot:sub-text>
                    Use the <code>focus</code> trigger to dismiss popovers
                    on the user’s next click of a different element than the toggle element.
                </template>
                <template v-slot:preview>
                    <b-button variant="success" v-b-popover.click.right="`And here's some amazing content. It's very engaging. Right?`" trigger="focus" title="Dismissible popover">
                        Dismissible popover
                    </b-button>
                </template>
            </CustomSyntax>

            <CustomSyntax title="Hover">
                <template v-slot:sub-text>
                    Use the attribute <code>data-bs-trigger="hover"</code>
                    to show the popover on hovering the element.
                </template>
                <template v-slot:preview>
                    <b-button variant="dark" id="hover" title="Ohh Wow !">
                        Please Hover Me
                    </b-button>
                  <b-popover target="hover" placement="right">
                    <template #title>Ohh Wow!</template>
                    And here's some amazing content. It's very engaging. Right?
                  </b-popover>
                </template>
            </CustomSyntax>

        </b-col> <!-- end col -->

        <b-col xl="6">
            <CustomSyntax title="Four Directions">
                <template v-slot:sub-text>
                    Four options are available: top, right, bottom, and
                    left aligned.
                </template>
                <template v-slot:preview>

                    <b-button variant="primary" v-b-popover.click="`Vivamus sagittis lacus vel augue laoreet rutrum faucibus.`" title="">
                        Popover on top
                    </b-button>

                    <b-button variant="primary" v-b-popover.click.bottom="'Vivamus sagittis lacus vel augue laoreet rutrum faucibus.'" title="" class="ms-1">
                        Popover on bottom
                    </b-button>

                    <b-button variant="primary" v-b-popover.click.right="'Vivamus sagittis lacus vel augue laoreet rutrum faucibus.'" title="" class="ms-1">
                        Popover on right
                    </b-button>

                    <b-button variant="primary" v-b-popover.click.left="'Vivamus sagittis lacus vel augue laoreet rutrum faucibus.'" title="Popover title" class="ms-1">
                        Popover on left
                    </b-button>

                </template>
            </CustomSyntax>

            <CustomSyntax title="Custom Popovers">
                <template v-slot:sub-text>
                    You can customize the appearance of popovers using CSS variables. We set a custom class with
                    <code>data-bs-custom-class="primary-popover"</code> to scope our custom appearance and use it to override some of the
                    local CSS variables.
                </template>
                <template v-slot:preview>
                    <div class="d-flex flex-wrap gap-1">
                        <b-button variant="primary" id="popover-1">
                            Primary popover
                        </b-button>
                        <b-popover target="popover-1" custom-class="primary-popover" placement="right">
                            <template #title>Primary popover</template>
                            This popover is themed via CSS variables.
                        </b-popover>

                        <b-button variant="success" id="popover-2">
                            Success popover
                        </b-button>
                        <b-popover target="popover-2" custom-class="success-popover" placement="right">
                            <template #title>Success popover</template>
                            This popover is themed via CSS variables.
                        </b-popover>

                        <b-button variant="danger" id="popover-3">
                            Danger popover
                        </b-button>
                        <b-popover target="popover-3" custom-class="danger-popover" placement="right">
                            <template #title>Danger popover</template>
                            This popover is themed via CSS variables.
                        </b-popover>
                        <b-button variant="info" id="popover-4"> Info popover </b-button>
                        <b-popover target="popover-4" custom-class="info-popover" placement="right">
                            <template #title>Info popover</template>
                            This popover is themed via CSS variables.
                        </b-popover>
                    </div>
                </template>
            </CustomSyntax>

            <CustomSyntax title="Disabled Elements">
                <template v-slot:sub-text>
                    Elements with the <code>disabled</code> attribute
                    aren’t interactive, meaning users cannot hover or click them to trigger a
                    popover (or tooltip). As a workaround, you’ll want to trigger the popover from a
                    wrapper <code>&lt;div&gt;</code> or <code>&lt;span&gt;</code> and override the
                    <code>pointer-events</code> on the disabled element.
                </template>
                <template v-slot:preview>
                    <span class="d-inline-block" data-bs-toggle="popover" data-bs-content="Disabled popover" data-bs-container="#disabled-popover-preview">
                        <b-button variant="primary" style="pointer-events: none;" disabled>Disabled button</b-button>
                    </span>
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
    components: { Layout, CustomSyntax, Breadcrumb },
    data() {
        return {
          title: 'Popovers',
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
              text: 'Popovers',
              active: true,
            },
          ],

            show: false
        }
    },
}
</script>
