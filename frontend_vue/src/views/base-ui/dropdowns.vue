<template>
<Layout>
    <Breadcrumb :title="title" :items="items" />

    <b-row>
        <b-col xl="6">
            <CustomSyntax title="Single button dropdowns">
                <template v-slot:sub-text>
                    Any single <code>.btn</code> can be turned into a dropdown
                    toggle with some markup changes. Here’s how you can put them to work
                    with either <code>&lt;button&gt;</code>
                    elements:
                </template>
                <template v-slot:preview>
                    <b-row>
                        <b-col class="col-auto">
                            <b-dropdown text="Dropdown button" variant="light">
                                <b-dropdown-item href="#">Action</b-dropdown-item>
                                <b-dropdown-item href="#">Another action</b-dropdown-item>
                                <b-dropdown-item href="#">Something else here</b-dropdown-item>
                            </b-dropdown>
                        </b-col>

                        <b-col class="col-auto">
                            <b-dropdown text="Dropdown link">
                                <b-dropdown-item href="#">Action</b-dropdown-item>
                                <b-dropdown-item href="#">Another action</b-dropdown-item>
                                <b-dropdown-item href="#">Something else here</b-dropdown-item>
                            </b-dropdown>
                        </b-col>
                    </b-row>
                </template>
            </CustomSyntax>

            <CustomSyntax title="Variant">
                <template v-slot:sub-text>
                    The best part is you can do this with any button variant, too:
                </template>
                <template v-slot:preview>
                    <b-dropdown text="Primary" variant="primary" class="mb-2">
                        <b-dropdown-item href="#">Action</b-dropdown-item>
                        <b-dropdown-item href="#">Another action</b-dropdown-item>
                        <b-dropdown-item href="#">Something else here</b-dropdown-item>
                        <b-dropdown-divider></b-dropdown-divider>
                        <b-dropdown-item href="#">Separated link</b-dropdown-item>
                    </b-dropdown>

                    <b-dropdown text="Secondary" variant="light" class="mb-2 ms-1">
                        <b-dropdown-item href="#">Action</b-dropdown-item>
                        <b-dropdown-item href="#">Another action</b-dropdown-item>
                        <b-dropdown-item href="#">Something else here</b-dropdown-item>
                        <b-dropdown-divider></b-dropdown-divider>
                        <b-dropdown-item href="#">Separated link</b-dropdown-item>
                    </b-dropdown>

                    <b-dropdown text="Success" variant="success" class="mb-2 ms-1">
                        <b-dropdown-item href="#">Action</b-dropdown-item>
                        <b-dropdown-item href="#">Another action</b-dropdown-item>
                        <b-dropdown-item href="#">Something else here</b-dropdown-item>
                        <b-dropdown-divider></b-dropdown-divider>
                        <b-dropdown-item href="#">Separated link</b-dropdown-item>
                    </b-dropdown>

                    <b-dropdown text="Info" variant="info" class="mb-2 ms-1">
                        <b-dropdown-item href="#">Action</b-dropdown-item>
                        <b-dropdown-item href="#">Another action</b-dropdown-item>
                        <b-dropdown-item href="#">Something else here</b-dropdown-item>
                        <b-dropdown-divider></b-dropdown-divider>
                        <b-dropdown-item href="#">Separated link</b-dropdown-item>
                    </b-dropdown>

                    <b-dropdown text="Warning" variant="warning" class="mb-2 ms-1">
                        <b-dropdown-item href="#">Action</b-dropdown-item>
                        <b-dropdown-item href="#">Another action</b-dropdown-item>
                        <b-dropdown-item href="#">Something else here</b-dropdown-item>
                        <b-dropdown-divider></b-dropdown-divider>
                        <b-dropdown-item href="#">Separated link</b-dropdown-item>
                    </b-dropdown>

                    <b-dropdown text="Danger" variant="danger" class="mb-2 ms-1">
                        <b-dropdown-item href="#">Action</b-dropdown-item>
                        <b-dropdown-item href="#">Another action</b-dropdown-item>
                        <b-dropdown-item href="#">Something else here</b-dropdown-item>
                        <b-dropdown-divider></b-dropdown-divider>
                        <b-dropdown-item href="#">Separated link</b-dropdown-item>
                    </b-dropdown>

                </template>
            </CustomSyntax>

            <CustomSyntax title="Animated Dropdown">
                <template v-slot:sub-text>
                    Add <code>.dropdown-menu-animated</code>
                    to a <code>.dropdown-menu</code> to have animated dropdown menu.
                </template>
                <template v-slot:preview>
                    <b-dropdown text="Animated Dropdown" variant="light">
                        <b-dropdown-item href="#">Action</b-dropdown-item>
                        <b-dropdown-item href="#">Another action</b-dropdown-item>
                        <b-dropdown-item href="#">Something else here</b-dropdown-item>
                    </b-dropdown>
                </template>
            </CustomSyntax>

            <CustomSyntax title="Dropup variation">
                <template v-slot:sub-text>
                    Trigger dropdown menus above elements
                    by adding <code>.dropup</code> to the parent
                    element.
                </template>
                <template v-slot:preview>
                    <b-dropdown dropup text="Dropup" variant="light">
                        <b-dropdown-item href="#">Action</b-dropdown-item>
                        <b-dropdown-item href="#">Another action</b-dropdown-item>
                        <b-dropdown-item href="#">Something else here</b-dropdown-item>
                        <b-dropdown-divider></b-dropdown-divider>
                        <b-dropdown-item href="#">Separated link</b-dropdown-item>
                    </b-dropdown>

                    <b-dropdown dropup text="Split dropup" split variant="light" class="ms-1">
                        <b-dropdown-item href="#">Action</b-dropdown-item>
                        <b-dropdown-item href="#">Another action</b-dropdown-item>
                        <b-dropdown-item href="#">Something else here</b-dropdown-item>
                        <b-dropdown-divider></b-dropdown-divider>
                        <b-dropdown-item href="#">Separated link</b-dropdown-item>
                    </b-dropdown>
                </template>
            </CustomSyntax>

            <CustomSyntax title="Dropend variation">
                <template v-slot:sub-text>
                    Trigger dropdown menus at the right of the elements by adding <code>.dropend</code> to the parent element.
                </template>
                <template v-slot:preview>
                    <b-dropdown dropend text="Dropend" variant="primary" class="mb-2">
                        <b-dropdown-item href="#">Action</b-dropdown-item>
                        <b-dropdown-item href="#">Another action</b-dropdown-item>
                        <b-dropdown-item href="#">Something else here</b-dropdown-item>
                        <b-dropdown-divider></b-dropdown-divider>
                        <b-dropdown-item href="#">Separated link</b-dropdown-item>
                    </b-dropdown>

                    <b-dropdown dropend text="Split Dropend" split variant="primary" class="mb-2 ms-1">
                        <b-dropdown-item href="#">Action</b-dropdown-item>
                        <b-dropdown-item href="#">Another action</b-dropdown-item>
                        <b-dropdown-item href="#">Something else here</b-dropdown-item>
                        <b-dropdown-divider></b-dropdown-divider>
                        <b-dropdown-item href="#">Separated link</b-dropdown-item>
                    </b-dropdown>

                </template>
            </CustomSyntax>

            <CustomSyntax title="Disabled Item">
                <template v-slot:sub-text>
                    Add <code>.disabled</code> to items in the dropdown to <strong>style them as disabled</strong>.
                </template>
                <template v-slot:preview>
                    <b-dropdown text="Disabled" variant="primary">
                        <b-dropdown-item href="#">Regular link</b-dropdown-item>
                        <b-dropdown-item disabled href="#" tabindex="-1" aria-disabled="true">Disabled link</b-dropdown-item>
                        <b-dropdown-item href="#">Another link</b-dropdown-item>
                    </b-dropdown>
                </template>
            </CustomSyntax>

            <CustomSyntax title="Dark dropdowns">
                <template v-slot:sub-text>
                    Opt into darker dropdowns to match a dark navbar or custom style by adding <code>.dropdown-menu-dark</code>
                    onto an existing <code>.dropdown-menu</code>. No changes are required to the dropdown items.
                </template>
                <template v-slot:preview>
                    <b-dropdown text="Dropdown button" variant="secondary">
                        <li>
                            <b-dropdown-item active href="#">Action</b-dropdown-item>
                        </li>
                        <li>
                            <b-dropdown-item href="#">Another action</b-dropdown-item>
                        </li>
                        <li>
                            <b-dropdown-item href="#">Something else here</b-dropdown-item>
                        </li>
                        <li>
                            <b-dropdown-divider />
                        </li>
                        <li>
                            <b-dropdown-item href="#">Separated link</b-dropdown-item>
                        </li>
                    </b-dropdown>
                </template>
            </CustomSyntax>

            <CustomSyntax title="Dropdown options">
                <template v-slot:sub-text>
                    Use <code>data-bs-offset</code> or <code>data-bs-reference</code> to change the location of the dropdown.
                </template>
                <template v-slot:preview>
                    <div class="d-flex">
                        <b-dropdown offset="10" text="Offset" class="me-1">
                            <b-dropdown-menu>
                                <li>
                                    <b-dropdown-item href="#">Action</b-dropdown-item>
                                </li>
                                <li>
                                    <b-dropdown-item href="#">Another action</b-dropdown-item>
                                </li>
                                <li>
                                    <b-dropdown-item href="#">Something else here</b-dropdown-item>
                                </li>
                            </b-dropdown-menu>
                        </b-dropdown>

                        <b-dropdown split variant="secondary" text="Reference">
                            <li>
                                <b-dropdown-item href="#">Action</b-dropdown-item>
                            </li>
                            <li>
                                <b-dropdown-item href="#">Another action</b-dropdown-item>
                            </li>
                            <li>
                                <b-dropdown-item href="#">Something else here</b-dropdown-item>
                            </li>
                            <li>
                                <b-dropdown-divider />
                            </li>
                            <li>
                                <b-dropdown-item href="#">Separated link</b-dropdown-item>
                            </li>
                        </b-dropdown>
                    </div>

                </template>
            </CustomSyntax>

            <CustomSyntax title="Text">
                <template v-slot:sub-text>
                    Place any freeform text within a dropdown menu with text and use spacing utilities. Note that you’ll likely
                    need additional sizing styles to constrain the menu width.
                </template>
                <template v-slot:preview>
                    <b-dropdown variant="primary" class="p-3 text-muted" text="Text Dropdown" style="max-width: 200px;" >
                        <b-dropdown-item >
                            <p>
                                Some example text that's free-flowing within the dropdown menu.
                            </p>
                            <p class="mb-0">And this is more example text.</p>
                        </b-dropdown-item>
                    </b-dropdown>
                </template>
            </CustomSyntax>
        </b-col> <!-- end col -->

        <b-col xl="6">
            <CustomSyntax title="Menu alignment">
                <template v-slot:sub-text>
                    Add <code>.dropdown-menu-end</code>
                    to a <code>.dropdown-menu</code> to right
                    align the dropdown menu.
                </template>
                <template v-slot:preview>
                    <b-dropdown text="Right-aligned menu" variant="light">
                        <b-dropdown-item href="#">Action</b-dropdown-item>
                        <b-dropdown-item href="#">Another action</b-dropdown-item>
                        <b-dropdown-item href="#">Something else here</b-dropdown-item>
                    </b-dropdown>
                </template>
            </CustomSyntax>

            <CustomSyntax title="Split button dropdowns">
                <template v-slot:sub-text>
                    Similarly, create split button dropdowns with virtually the same markup as single button dropdowns, but with
                    the addition of <code>.dropdown-toggle-split</code> for proper spacing around the dropdown caret.
                </template>
                <template v-slot:preview>
                    <b-dropdown split text="Primary" variant="primary" class="mb-2">
                        <b-dropdown-item href="#">Action</b-dropdown-item>
                        <b-dropdown-item href="#">Another action</b-dropdown-item>
                        <b-dropdown-item href="#">Something else here</b-dropdown-item>
                        <b-dropdown-divider></b-dropdown-divider>
                        <b-dropdown-item href="#">Separated link</b-dropdown-item>
                    </b-dropdown>

                    <b-dropdown split text="Secondary" variant="light" class="mb-2 ms-1">
                        <b-dropdown-item href="#">Action</b-dropdown-item>
                        <b-dropdown-item href="#">Another action</b-dropdown-item>
                        <b-dropdown-item href="#">Something else here</b-dropdown-item>
                        <b-dropdown-divider></b-dropdown-divider>
                        <b-dropdown-item href="#">Separated link</b-dropdown-item>
                    </b-dropdown>

                    <b-dropdown split text="Success" variant="success" class="mb-2 ms-1">
                        <b-dropdown-item href="#">Action</b-dropdown-item>
                        <b-dropdown-item href="#">Another action</b-dropdown-item>
                        <b-dropdown-item href="#">Something else here</b-dropdown-item>
                        <b-dropdown-divider></b-dropdown-divider>
                        <b-dropdown-item href="#">Separated link</b-dropdown-item>
                    </b-dropdown>

                    <b-dropdown split text="Info" variant="info" class="mb-2 ms-1">
                        <b-dropdown-item href="#">Action</b-dropdown-item>
                        <b-dropdown-item href="#">Another action</b-dropdown-item>
                        <b-dropdown-item href="#">Something else here</b-dropdown-item>
                        <b-dropdown-divider></b-dropdown-divider>
                        <b-dropdown-item href="#">Separated link</b-dropdown-item>
                    </b-dropdown>

                    <b-dropdown split text="Warning" variant="warning" class="mb-2 ms-1">
                        <b-dropdown-item href="#">Action</b-dropdown-item>
                        <b-dropdown-item href="#">Another action</b-dropdown-item>
                        <b-dropdown-item href="#">Something else here</b-dropdown-item>
                        <b-dropdown-divider></b-dropdown-divider>
                        <b-dropdown-item href="#">Separated link</b-dropdown-item>
                    </b-dropdown>

                    <b-dropdown split text="Danger" variant="danger" class="mb-2 ms-1">
                        <b-dropdown-item href="#">Action</b-dropdown-item>
                        <b-dropdown-item href="#">Another action</b-dropdown-item>
                        <b-dropdown-item href="#">Something else here</b-dropdown-item>
                        <b-dropdown-divider></b-dropdown-divider>
                        <b-dropdown-item href="#">Separated link</b-dropdown-item>
                    </b-dropdown>
                </template>
            </CustomSyntax>

            <CustomSyntax title="Sizing">
                <template v-slot:sub-text>
                    Button dropdowns work with buttons of all sizes, including default and split dropdown buttons.
                </template>
                <template v-slot:preview>
                    <b-dropdown variant="light" text="Large button" size="lg">
                        <b-dropdown-item href="#">Action</b-dropdown-item>
                        <b-dropdown-item href="#">Another action</b-dropdown-item>
                        <b-dropdown-item href="#">Something else here</b-dropdown-item>
                        <b-dropdown-divider></b-dropdown-divider>
                        <b-dropdown-item href="#">Separated link</b-dropdown-item>
                    </b-dropdown>

                    <b-dropdown split variant="light" text="Large button" size="lg" class="ms-1">
                        <b-dropdown-item href="#">Action</b-dropdown-item>
                        <b-dropdown-item href="#">Another action</b-dropdown-item>
                        <b-dropdown-item href="#">Something else here</b-dropdown-item>
                        <b-dropdown-divider></b-dropdown-divider>
                        <b-dropdown-item href="#">Separated link</b-dropdown-item>
                    </b-dropdown>

                    <b-dropdown variant="light" text="Small button" size="sm" class="ms-1">
                        <b-dropdown-item href="#">Action</b-dropdown-item>
                        <b-dropdown-item href="#">Another action</b-dropdown-item>
                        <b-dropdown-item href="#">Something else here</b-dropdown-item>
                        <b-dropdown-divider></b-dropdown-divider>
                        <b-dropdown-item href="#">Separated link</b-dropdown-item>
                    </b-dropdown>

                    <b-dropdown split variant="light" text="Small button" size="sm" class="ms-1">
                        <b-dropdown-item href="#">Action</b-dropdown-item>
                        <b-dropdown-item href="#">Another action</b-dropdown-item>
                        <b-dropdown-item href="#">Something else here</b-dropdown-item>
                        <b-dropdown-divider></b-dropdown-divider>
                        <b-dropdown-item href="#">Separated link</b-dropdown-item>
                    </b-dropdown>
                </template>
            </CustomSyntax>

            <CustomSyntax title="Dropstart variation">
                <template v-slot:sub-text>
                    Trigger dropdown menus at the right of the elements by adding <code>.dropleft</code> to the parent element.
                </template>
                <template v-slot:preview>
                    <b-dropdown dropstart variant="secondary" text="Dropstart">
                        <b-dropdown-item href="#">Action</b-dropdown-item>
                        <b-dropdown-item href="#">Another action</b-dropdown-item>
                        <b-dropdown-item href="#">Something else here</b-dropdown-item>
                        <b-dropdown-divider />
                        <b-dropdown-item href="#">Separated link</b-dropdown-item>
                    </b-dropdown>

                    <b-dropdown dropstart split variant="secondary" text="Split dropstart" class="ms-1">
                        <b-dropdown-item href="#">Action</b-dropdown-item>
                        <b-dropdown-item href="#">Another action</b-dropdown-item>
                        <b-dropdown-item href="#">Something else here</b-dropdown-item>
                        <b-dropdown-divider />
                        <b-dropdown-item href="#">Separated link</b-dropdown-item>
                    </b-dropdown>
                </template>
            </CustomSyntax>

            <CustomSyntax title="Active Item">
                <template v-slot:sub-text>
                    Add <code>.active</code> to item in the dropdown to <strong>style them as active</strong>.
                </template>
                <template v-slot:preview>
                    <b-dropdown variant="secondary" text="Active Item">
                        <b-dropdown-item href="#">Regular link</b-dropdown-item>
                        <b-dropdown-item active href="#">Active link</b-dropdown-item>
                        <b-dropdown-item href="#">Another link</b-dropdown-item>
                    </b-dropdown>
                </template>
            </CustomSyntax>

            <CustomSyntax title="Headers">
                <template v-slot:sub-text>
                    Add a header to label sections of actions in any dropdown menu.
                </template>
                <template v-slot:preview>
                    <b-dropdown variant="secondary" text="Header">
                        <b-dropdown-header>Dropdown header</b-dropdown-header>
                        <b-dropdown-item href="#">Action</b-dropdown-item>
                        <b-dropdown-item href="#">Another action</b-dropdown-item>
                    </b-dropdown>
                </template>
            </CustomSyntax>

            <CustomSyntax title="Centered dropdowns">
                <template v-slot:sub-text>
                    Make the dropdown menu centered below the toggle with <code>.dropdown-center</code> on the parent element.
                </template>
                <template v-slot:preview>
                    <div class="hstack gap-2">
                        <b-dropdown variant="secondary" text="Centered dropdown">
                            <li>
                                <b-dropdown-item href="#">Action</b-dropdown-item>
                            </li>
                            <li>
                                <b-dropdown-item href="#">Action two</b-dropdown-item>
                            </li>
                            <li>
                                <b-dropdown-item href="#">Action three</b-dropdown-item>
                            </li>
                        </b-dropdown>

                        <div class="dropup-center dropup">
                            <b-dropdown dropup variant="secondary" text="Centered dropup">
                                <li>
                                    <b-dropdown-item href="#">Action</b-dropdown-item>
                                </li>
                                <li>
                                    <b-dropdown-item href="#">Action two</b-dropdown-item>
                                </li>
                                <li>
                                    <b-dropdown-item href="#">Action three</b-dropdown-item>
                                </li>
                            </b-dropdown>
                        </div>
                    </div>
                </template>
            </CustomSyntax>

            <CustomSyntax title="Auto close behavior">
                <template v-slot:sub-text>
                    By default, the dropdown menu is closed when clicking inside or outside the dropdown menu. You can use the
                    <code>autoClose</code> option to change this behavior of the dropdown.
                </template>
                <template v-slot:preview>
                    <div class="hstack gap-2">
                        <b-dropdown variant="secondary" text="Default dropdown">
                            <li>
                                <b-dropdown-item href="#">Menu item</b-dropdown-item>
                            </li>
                            <li>
                                <b-dropdown-item href="#">Menu item</b-dropdown-item>
                            </li>
                            <li>
                                <b-dropdown-item href="#">Menu item</b-dropdown-item>
                            </li>
                        </b-dropdown>

                        <b-dropdown variant="secondary" text="Clickable inside">
                            <li><a class="dropdown-item" href="#">Menu item</a></li>
                            <li><a class="dropdown-item" href="#">Menu item</a></li>
                            <li><a class="dropdown-item" href="#">Menu item</a></li>
                        </b-dropdown>

                        <b-dropdown variant="secondary" text=" Clickable outside">
                            <li><a class="dropdown-item" href="#">Menu item</a></li>
                            <li><a class="dropdown-item" href="#">Menu item</a></li>
                            <li><a class="dropdown-item" href="#">Menu item</a></li>
                        </b-dropdown>

                        <b-dropdown variant="secondary" text="Manual close">
                            <li><a class="dropdown-item" href="#">Menu item</a></li>
                            <li><a class="dropdown-item" href="#">Menu item</a></li>
                            <li><a class="dropdown-item" href="#">Menu item</a></li>
                        </b-dropdown>
                    </div>
                </template>
            </CustomSyntax>

            <CustomSyntax title="Forms">
                <template v-slot:sub-text>
                    Put a form within a dropdown menu, or make it into a dropdown menu, and use margin or padding utilities to
                    give it the negative space you require.
                </template>
                <template v-slot:preview>
                    <b-dropdown text="Form" variant="secondary">
                        <b-form class="px-4 py-3">
                            <b-form-group label="Email address" label-for="exampleDropdownFormEmail1" class="mb-3">
                                <b-form-input type="email" id="exampleDropdownFormEmail1" placeholder="email@example.com" />
                            </b-form-group>
                            <div class="mb-3">
                                <label for="exampleDropdownFormPassword1" class="form-label">Password</label>
                                <b-form-input type="password" id="exampleDropdownFormPassword1" placeholder="Password" />
                            </div>
                            <div class="mb-2">
                                <b-form-checkbox id="dropdownCheck">
                                    Remember me
                                </b-form-checkbox>
                            </div>
                            <b-button type="submit" variant="primary">Sign in</b-button>
                        </b-form>
                        <b-dropdown-divider />
                        <b-dropdown-item href="#">New around here? Sign up</b-dropdown-item>
                        <b-dropdown-item href="#">Forgot password?</b-dropdown-item>
                    </b-dropdown>

                </template>
            </CustomSyntax>

        </b-col> <!-- end col -->
    </b-row>
    <!-- end row -->
</Layout>
</template>

<script lang="ts">
import Layout from '@/components/layouts/layout.vue';
import Breadcrumb from "@/components/breadcrumb.vue";
import CustomSyntax from "@/components/custom/custom-syntax.vue";

export default {
    components: { Layout, Breadcrumb, CustomSyntax },
    data() {
        return {
            title: 'Dropdowns',
            items: [{
                    text: 'Hyper',
                    href: '/',
                },
                {
                    text: 'Base UI',
                    href: '/',
                },
                {
                    text: 'Dropdowns',
                    active: true,
                },
            ],
        }
    }
}
</script>
