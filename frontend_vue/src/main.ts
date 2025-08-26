import {createApp,type Plugin} from 'vue'
import {createPinia} from 'pinia'
// Ensure authenticated requests include the Token header on startup
import { useDjangoAuthStore } from '@/stores/djangoAuth'

import App from './App.vue'
import router from './router'

import BootstrapVueNext from 'bootstrap-vue-next'
import VueApexCharts from 'vue3-apexcharts'
import VueTheMask from "vue-the-mask";

import jQuery from 'jquery'
window.$ = window.jQuery = jQuery

import moment from 'moment'
window.moment = moment

import 'simplebar'
import 'bootstrap-vue-next/dist/bootstrap-vue-next.css'
import 'admin-resources/jquery.vectormap/jquery-jvectormap-1.2.2.css'
import 'daterangepicker/daterangepicker.css'
import 'vue-multiselect/dist/vue-multiselect.css'
import 'jquery-toast-plugin/dist/jquery.toast.min.css'
import 'frappe-gantt/dist/frappe-gantt.min.css'
import '@vueup/vue-quill/dist/vue-quill.snow.css';
import '@vueup/vue-quill/dist/vue-quill.bubble.css';
import 'jstree/dist/themes/default/style.min.css'
import 'vue3-form-wizard/dist/style.css';
import 'bootstrap-datepicker/dist/css/bootstrap-datepicker.min.css'
import 'bootstrap-timepicker/css/bootstrap-timepicker.min.css'
import 'flatpickr/dist/flatpickr.min.css'

import '@/assets/scss/app-saas.scss'
import '@/assets/scss/icons.scss'

// Global directives
import currencyDirective from '@/lib/directives/currency'

// AG Grid: register all Community features globally before any grid is created.
// Reference: https://www.ag-grid.com/vue-data-grid/getting-started/ (Modules section)
import { ModuleRegistry, AllCommunityModule } from 'ag-grid-community'
ModuleRegistry.registerModules([AllCommunityModule])

const app = createApp(App)

const MetaPlug: Plugin = {
    install: (app: any, options: any) => {
        const useMeta = (item: { [key: string]: any }) => {
            console.info(item);
        };
        app.mixin({
            methods: {
                useMeta(item: { [key: string]: any }) {
                    document.head.querySelector("title")!.innerHTML =
                        item["title"] + " | Hyper - Responsive Bootstrap 5 Admin Dashboard";
                },
            },
        });
    },
};

// Create Pinia instance so we can initialize auth before mounting
const pinia = createPinia()
app.use(pinia)
app.use(router)
app.use(BootstrapVueNext)
app.use(VueApexCharts)
app.use(VueTheMask);
app.use(MetaPlug);

// Register global currency directive: v-currency
app.directive('currency', currencyDirective)

// Initialize authentication from persisted token and attach Authorization header
// This avoids 401s when calling protected APIs (e.g., /api/acq/photos/:id/)
const auth = useDjangoAuthStore(pinia)
auth.setAuthHeader()
// Fire-and-forget fetching of current user; header is already set above
auth.initAuth()

app.mount('#app')
