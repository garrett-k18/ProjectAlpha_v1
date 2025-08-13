// home
const homeRoute = [
    {
        path: "/",
        name: "home",
        component: () => import("@/1_global/structure/home.vue"),
    },
];

// auth
const authRoutes = [
    {
        path: "/login",
        name: "login",
        // Use the user's custom login component under 1_global structure
        component: () => import("@/1_global/structure/1.login.vue")
    },
    {
        path: "/login-2",
        name: "login-2",
        component: () => import("@/views/authentication/login-2.vue")
    },
    {
        path: "/register",
        name: "register",
        component: () => import("@/views/authentication/register.vue")
    },
    {
        path: "/register-2",
        name: "register-2",
        component: () => import("@/views/authentication/register-2.vue")
    },
    {
        path: "/logout",
        name: "logout",
        component: () => import("@/views/authentication/logout.vue")
    },
    {
        path: "/logout-2",
        name: "logout-2",
        component: () => import("@/views/authentication/logout-2.vue")
    },
    {
        path: "/recoverpw",
        name: "recoverpw",
        component: () => import("@/views/authentication/recoverpw.vue")
    },
    {
        path: "/recoverpw-2",
        name: "recoverpw-2",
        component: () => import("@/views/authentication/recoverpw-2.vue")
    },
    {
        path: "/lock-screen",
        name: "lock-screen",
        component: () => import("@/views/authentication/lock-screen.vue")
    },
    {
        path: "/lock-screen-2",
        name: "lock-screen-2",
        component: () => import("@/views/authentication/lock-screen-2.vue")
    },
    {
        path: "/confirm-mail",
        name: "confirm-mail",
        component: () => import("@/views/authentication/confirm-mail.vue")
    },
    {
        path: "/confirm-mail-2",
        name: "confirm-mail-2",
        component: () => import("@/views/authentication/confirm-mail-2.vue")
    },
]

// error pages
const errorPageRoutes = [
    {
        path: "/error-404",
        name: "error-404",
        component: () => import("@/views/error/error-404.vue")
    },
    {
        path: "/error-404-alt",
        name: "error-404-alt",
        component: () => import("@/views/error/error-404-alt.vue")
    },
    {
        path: "/error-500",
        name: "error-500",
        component: () => import("@/views/error/error-500.vue")
    },
    {
        path: "/:catchAll(.*)",
        redirect: "error-404",
    },
]

// dashboard
const dashboardRoutes = [
    {
        path: '',
        name: 'Dashboards',
        header: 'Navigation',
        icon: 'uil-home-alt',
        badge: {
            text: '5',
            variant: 'success',
        },
        meta: {authRequired: true},
        children: [
            {
                name: 'Analytics',
                path: 'analytics',
                meta: {authRequired: true},
                component: () => import('@/views/dashboards/analytics/index.vue'),
            },
            {
                name: 'Ecommerce',
                path: '',
                meta: {authRequired: true},
                component: () => import('@/views/dashboards/ecommerce/index.vue'),
            },
            {
                name: 'Projects',
                path: 'projects',
                meta: {authRequired: true},
                component: () => import('@/views/dashboards/projects/index.vue'),
            },
            {
                name: 'Dashboard CRM',
                path: 'crm',
                meta: {authRequired: true},
                component: () => import('@/views/dashboards/crm/index.vue'),
            },
            {
                name: 'E-Wallet',
                path: 'e-wallet',
                meta: {authRequired: true},
                component: () => import('@/views/dashboards/wallet/index.vue'),
            },

        ]
    }
]

// apps calendar
const calendarAppsRoutes = [
    {
        path: '/apps/calendar',
        name: 'Calendar',
        header: 'Apps',
        icon: 'uil-calender',
        component: () => import('@/views/apps/calendar/index.vue'),
        meta: {authRequired: true},

    }
];

// apps chat
const chatAppsRoutes = [
    {
        path: '/apps/chat',
        name: 'Chat',
        icon: 'uil-comments-alt',
        component: () => import('@/views/apps/chat/index.vue'),
        meta: {authRequired: true},
    }
];

// apps crm
const crmAppsRoutes = [
    {
        path: '/apps/crm',
        name: 'CRM',
        icon: 'uil-tachometer-fast',
        meta: {authRequired: true},

        children: [
            {
                path: 'projects',
                name: 'CRM Projects',
                component: () => import('@/views/apps/crm/projects/index.vue')
            },
            {
                path: 'orders-list',
                name: 'Order List',
                component: () => import('@/views/apps/crm/order-list/index.vue')
            },
            {
                path: 'clients',
                name: 'Clients',
                component: () => import('@/views/apps/crm/clients/index.vue')
            },
            {
                path: 'management',
                name: 'Management',
                component: () => import('@/views/apps/crm/management/index.vue')
            }
        ]
    }
];

// apps ecommerce
const ecommerceAppsRoutes = [
    {
        path: '/apps/ecommerce',
        name: 'Ecommerce Apps',
        icon: 'uil-store',
        meta: {authRequired: true},
        children: [
            {
                path: 'products',
                name: 'Products',
                component: () => import('@/views/apps/ecommerce/products/index.vue')
            },
            {
                path: 'products-details',
                name: 'Products Detail',
                component: () => import('@/views/apps/ecommerce/products-details.vue')
            },
            {
                path: 'orders',
                name: 'Orders',
                component: () => (import('@/views/apps/ecommerce/orders/index.vue'))
            },
            {
                path: 'order-detail',
                name: 'Order Details',
                component: () => import('@/views/apps/ecommerce/order-detail.vue')
            },
            {
                path: 'customers',
                name: 'Customers',
                component: () => import('@/views/apps/ecommerce/customers/index.vue')
            },
            {
                path: 'shopping-cart',
                name: 'Shopping Cart',
                component: () => import('@/views/apps/ecommerce/shopping-cart.vue')
            },
            {
                path: 'checkout',
                name: 'Checkout',
                component: () => import('@/views/apps/ecommerce/checkout.vue')
            },
            {
                path: 'sellers',
                name: 'Sellers',
                component: () => import('@/views/apps/ecommerce/sellers/index.vue')
            },
        ]
    }
]

// apps email
const emailAppsRoutes = [
    {
        path: '/apps/email',
        name: 'Email',
        icon: 'uil-envelope',
        meta: {authRequired: true},

        children: [
            {
                name: 'Inbox',
                path: 'inbox',
                meta: {authRequired: true},
                component: () => (import('@/views/apps/email/inbox/index.vue')),
            },
            {
                path: 'read',
                name: 'Read Email',
                meta: {authRequired: true},
                component: () => (import('@/views/apps/email/read-email.vue')),
            },
        ],
    }
];

// apps project
const projectAppsRoutes = [
    {
        path: '/apps/projects',
        name: 'Project',
        icon: 'uil-briefcase',
        meta: {authRequired: true},

        children: [
            {
                path: 'list',
                name: 'List',
                component: () => import('@/views/apps/projects/list/index.vue'),
            },
            {
                path: 'details',
                name: 'Details',
                component: () => import('@/views/apps/projects/details/index.vue'),
            },
            {
                path: 'gantt',
                name: 'Gantt',
                component: () => import('@/views/apps/projects/gantt.vue')
            },
            {
                path: 'create',
                name: 'Create Project',
                component: () => import('@/views/apps/projects/create.vue')
            },
        ],
    }
];

// apps tasks
const taskAppsRoutes = [
    {
        path: '/apps/tasks',
        name: 'Tasks',
        icon: 'uil-clipboard-alt',
        meta: {authRequired: true},
        children: [
            {
                path: 'list',
                name: 'Task List',
                component: () => import('@/views/apps/tasks/list/index.vue')
            },
            {
                path: 'details',
                name: 'Detail',
                component: () => import('@/views/apps/tasks/details/index.vue')
            },
            {
                path: 'kanban',
                name: 'Kanban Board',
                component: () => import('@/views/apps/tasks/kanban/index.vue')
            },
        ]
    }
];

// apps social-feed
const socialFeedAppsRoutes = [
    {
        path: '/apps/social-feed',
        name: 'Social Feed',
        icon: 'uil-rss',
        component: () => import('@/views/apps/social-feed/index.vue'),
        meta: {authRequired: true},
    }
];

// apps file-manager
const fileManagerAppsRoutes = [
    {
        path: '/apps/file-manager',
        name: 'File Manager',
        icon: 'uil-folder-plus',
        component: () => import('@/views/apps/file-manager/index.vue'),
        meta: {authRequired: true},
    }
];

// pages
const pagesRoutes = [
    {
        path: "/pages",
        name: "Pages",
        header: 'Custom',
        icon: 'uil-copy-alt',
        meta: {authRequired: true},
        children: [
            {
                path: "profile",
                name: "profile",
                component: () => import ("@/views/pages/profile/index.vue")
            },
            {
                path: "profile-2",
                name: "profile-2",
                component: () => import("@/views/pages/profile2/index.vue")
            },
            {
                path: "invoice",
                name: "invoice",
                component: () => import("@/views/pages/invoice.vue")
            },
            {
                path: "faq",
                name: "faq",
                component: () => import("@/views/pages/faq.vue")
            },
            {
                path: "pricing",
                name: "pricing",
                component: () => import("@/views/pages/pricing.vue")
            },
            {
                path: "maintenance",
                name: "maintenance",
                component: () => import("@/views/pages/maintenance.vue")
            },
            {
                path: "starter",
                name: "starter",
                component: () => import("@/views/pages/starter.vue")
            },
            {
                path: "preloader",
                name: "preloader",
                component: () => import("@/views/pages/preloader.vue")
            },
            {
                path: "timeline",
                name: "timeline",
                component: () => import("@/views/pages/timeline.vue")
            },
        ]
    },
];

// landing
const landingRoutes = [
    {
        path: '/landing',
        name: 'Landing',
        icon: 'uil-globe',
        component: () => import('@/views/landing/index.vue'),
    }
];

// layouts
const layoutRoutes = [
    {
        path: '/layout',
        name: 'Layouts',
        icon: 'uil-window',
        meta: {authRequired: true},
        children: [
            {
                path: "vertical",
                name: "Vertical Layout",
                component: () => import ("@/views/layout-eg/vertical.vue")
            },
            {
                path: "horizontal",
                name: "Horizontal Layout",
                component: () => import ("@/views/layout-eg/horizontal.vue")
            },
            {
                path: "detached",
                name: "Detached Layout",
                component: () => import ("@/views/layout-eg/detached.vue")
            },
            {
                path: "full",
                name: "Full Layout",
                component: () => import ("@/views/layout-eg/full.vue")
            },
            {
                path: "fullscreen",
                name: "FullScreen Layout",
                component: () => import ("@/views/layout-eg/full-screen.vue")
            },
            {
                path: "hover",
                name: "Hover Layout",
                component: () => import ("@/views/layout-eg/hover.vue")
            },
            {
                path: "compact",
                name: "Compact Layout",
                component: () => import ("@/views/layout-eg/compact.vue")
            },
            {
                path: "icon-view",
                name: "Icon View Layout",
                component: () => import ("@/views/layout-eg/icon-view.vue")
            },
        ]
    }
]

// base ui
const uiRoutes = [
    {
        path: '/ui',
        name: 'Base UI',
        header: 'Components',
        icon: 'uil-box',
        meta: {authRequired: true},
        children: [
            {
                path: 'accordions',
                name: 'Accordions',
                component: () => (import('@/views/base-ui/accordions.vue'))
            },
            {
                path: 'alerts',
                name: 'Alerts',
                component: () => (import('@/views/base-ui/alerts.vue'))
            },
            {
                path: 'avatars',
                name: 'Avatars',
                component: () => (import('@/views/base-ui/avatars.vue'))
            },
            {
                path: 'badges',
                name: 'Badges',
                component: () => (import('@/views/base-ui/badges.vue'))
            },

            {
                path: 'breadcrumb',
                name: 'Breadcrumb',
                component: () => (import('@/views/base-ui/breadcrumb.vue'))
            },
            {
                path: 'buttons',
                name: 'Buttons',
                component: () => (import('@/views/base-ui/buttons.vue'))
            },
            {
                path: 'cards',
                name: 'Cards',
                component: () => (import('@/views/base-ui/cards.vue'))
            },
            {
                path: 'carousel',
                name: 'Carousel',
                component: () => (import('@/views/base-ui/carousel.vue'))
            },
            {
                path: 'dropdowns',
                name: 'Dropdowns',
                component: () => (import('@/views/base-ui/dropdowns.vue'))
            },
            {
                path: 'embed-video',
                name: 'Video',
                component: () => (import('@/views/base-ui/embed-video.vue'))
            },
            {
                path: 'grid',
                name: 'Grid',
                component: () => (import('@/views/base-ui/grid.vue'))
            },
            {
                path: 'list-group',
                name: 'List-group',
                component: () => (import('@/views/base-ui/list-group.vue'))
            },
            {
                path: 'modals',
                name: 'Modals',
                component: () => (import('@/views/base-ui/modal/modals.vue'))
            },
            {
                path: 'notifications',
                name: 'Notifications',
                component: () => (import('@/views/base-ui/notifications.vue'))
            },
            {
                path: 'offcanvas',
                name: 'offcanvas',
                component: () => (import('@/views/base-ui/offcanvas.vue'))
            },
            {
                path: 'placeholders',
                name: 'placeholders',
                component: () => (import('@/views/base-ui/placeholders.vue'))
            },
            {
                path: 'pagination',
                name: 'Pagination',
                component: () => (import('@/views/base-ui/pagination.vue'))
            },
            {
                path: 'popovers',
                name: 'Popovers',
                component: () => (import('@/views/base-ui/popovers.vue'))
            },
            {
                path: 'progress',
                name: 'Progress',
                component: () => (import('@/views/base-ui/progress.vue'))
            },
            {
                path: 'ribbons',
                name: 'Ribbons',
                component: () => (import('@/views/base-ui/ribbons.vue'))
            },
            {
                path: 'spinners',
                name: 'Spinners',
                component: () => (import('@/views/base-ui/spinners.vue'))
            },
            {
                path: 'tabs',
                name: 'Tabs',
                component: () => (import('@/views/base-ui/tabs.vue'))
            },
            {
                path: 'tooltips',
                name: 'Tooltips',
                component: () => (import('@/views/base-ui/tooltips.vue'))
            },
            {
                path: 'links',
                name: 'links',
                component: () => (import('@/views/base-ui/links.vue'))
            },
            {
                path: 'typography',
                name: 'Typography',
                component: () => (import('@/views/base-ui/typography.vue'))
            },
            {
                path: 'utilities',
                name: 'utilities',
                component: () => (import('@/views/base-ui/utilities.vue'))
            }
        ],
    }
]

// extended ui
const extendedRoutes = [
    {
        path: '/extended',
        name: 'Extended UI',
        icon: 'uil-package',
        meta: {authRequired: true},

        children: [
            {
                path: 'dragula',
                name: 'Dragula',
                component: () => import('@/views/extended/dragula.vue')
            },
            {
                path: 'range-slider',
                name: 'Range Slider',
                component: () => import('@/views/extended/range-slider.vue')
            },
            {
                path: 'ratings',
                name: 'Ratings',
                component: () => import('@/views/extended/ratings.vue')
            },
            {
                path: 'scrollbar',
                name: 'Scrollbar',
                component: () => import('@/views/extended/scrollbar.vue')
            },
            {
                path: 'scrollspy',
                name: 'Scrollspy',
                component: () => import('@/views/extended/scrollspy.vue')
            },
            {
                path: 'treeview',
                name: 'Treeview',
                component: () => import('@/views/extended/treeview.vue')
            },
        ]
    },
]

// widgets
const widgetRoute = [
    {
        path: '/widgets',
        name: 'Widgets',
        icon: 'uil-layer-group',
        component: () => import('@/views/widgets/index.vue'),
        meta: {authRequired: true},

    },
]

// icons
const iconsRoutes = [
    {
        path: '/icons',
        name: 'Icons',
        icon: 'uil-streering',
        meta: {authRequired: true},
        children: [
            {
                path: 'remix-icons',
                name: 'Remix Icons',
                component: () => import('@/views/icons/remix-icon.vue')
            },
            {
                path: 'mdi',
                name: 'Material Design',
                component: () => import('@/views/icons/material-design-icon.vue')
            },
            {
                path: 'unicons',
                name: 'Unicons',
                component: () => import('@/views/icons/unicon-icon.vue')
            },
        ]
    }
]

// charts
const chartsRoutes = [
    {
        path: '/charts',
        name: 'Charts',
        icon: 'uil-chart',
        meta: {authRequired: true},

        children: [
            {
                path: 'apex',
                name: 'Apex',
                children: [
                    {
                        path: 'area',
                        name: 'Area',
                        component: () => (import('@/views/charts/apex/area/index.vue'))
                    },
                    {
                        path: 'bar',
                        name: 'Bar',
                        component: () => (import('@/views/charts/apex/bar/index.vue'))
                    },
                    {
                        path: 'bubble',
                        name: 'Bubble',
                        component: () => (import('@/views/charts/apex/bubble/index.vue'))
                    },
                    {
                        path: 'candlestick',
                        name: 'Candlestick',
                        component: () => (import('@/views/charts/apex/candlestick/index.vue'))
                    },
                    {
                        path: 'column',
                        name: 'Column',
                        component: () => (import('@/views/charts/apex/column/index.vue'))
                    },
                    {
                        path: 'heatmap',
                        name: 'Heatmap',
                        component: () => (import('@/views/charts/apex/heatmap/index.vue'))
                    },
                    {
                        path: 'line',
                        name: 'Line',
                        component: () => (import('@/views/charts/apex/line/index.vue'))
                    },
                    {
                        path: 'mixed',
                        name: 'Mixed',
                        component: () => (import('@/views/charts/apex/mixed/index.vue'))
                    },
                    {
                        path: 'timeline',
                        name: 'Timeline',
                        component: () => (import('@/views/charts/apex/timeline/index.vue'))
                    },
                    {
                        path: 'boxplot',
                        name: 'Boxplot',
                        component: () => (import('@/views/charts/apex/boxplot/index.vue'))
                    },
                    {
                        path: 'treemap',
                        name: 'Treemap',
                        component: () => (import('@/views/charts/apex/treemap/index.vue'))
                    },
                    {
                        path: 'pie',
                        name: 'Pie',
                        component: () => (import('@/views/charts/apex/pie/index.vue'))
                    },
                    {
                        path: 'radar',
                        name: 'Radar',
                        component: () => (import('@/views/charts/apex/radar/index.vue'))
                    },
                    {
                        path: 'radialbar',
                        name: 'Radialbar',
                        component: () => (import('@/views/charts/apex/radialbar/index.vue'))
                    },
                    {
                        path: 'scatter',
                        name: 'Scatter',
                        component: () => (import('@/views/charts/apex/scatter/index.vue'))
                    },
                    {
                        path: 'polar-area',
                        name: 'polar-area',
                        component: () => (import('@/views/charts/apex/polar-area/index.vue'))
                    },
                ]
            },
            {
                path: 'chartjs',
                name: 'Chartjs',
                children: [
                    {
                        path: 'area',
                        name: 'Chartjs Area',
                        component: () => (import('@/views/charts/chartjs/area/index.vue'))
                    },
                    {
                        path: 'bar',
                        name: 'Chartjs Bar',
                        component: () => (import('@/views/charts/chartjs/bar/index.vue'))
                    },
                    {
                        path: 'line',
                        name: 'Chartjs Line',
                        component: () => (import('@/views/charts/chartjs/line/index.vue'))
                    },
                    {
                        path: 'other',
                        name: 'Chartjs Other',
                        component: () => (import('@/views/charts/chartjs/other/index.vue'))
                    },
                ]
            },
            {
                path: 'sparkline',
                name: 'Sparkline',
                component: () => (import('@/views/charts/sparkline.vue'))
            },
        ]
    }
]

// forms
const formsRoutes = [
    {
        path: '/forms',
        name: 'Forms',
        icon: 'uil-document-layout-center',
        meta: {authRequired: true},
        children: [
            {
                path: 'elements',
                name: 'Basic Elements',
                component: () => import('@/views/form/elements.vue')
            },
            {
                path: 'advanced',
                name: 'Form Advanced',
                component: () => import('@/views/form/advanced/index.vue')
            },
            {
                path: 'validation',
                name: 'Validation',
                component: () => import('@/views/form/validation.vue')
            },
            {
                path: 'wizard',
                name: 'Wizard',
                component: () => import('@/views/form/wizard/index.vue')
            },
            {
                path: 'fileuploads',
                name: 'File Uploads',
                component: () => import('@/views/form/fileuploads.vue')
            },
            {
                path: 'editor',
                name: 'Editors',
                component: () => import('@/views/form/editors.vue')
            },
        ]
    }
]

// tables
const tablesRoutes = [
    {
        path: '/tables',
        name: 'Tables',
        icon: 'uil-table',
        meta: {authRequired: true},

        children: [
            {
                path: 'basic',
                name: 'Basic Tables',
                component: () => import('@/views/tables/basic-table.vue'),
            },
            {
                path: 'datatable',
                name: 'Data Tables',
                component: () => import('@/views/tables/data-table.vue'),
            },
            {
                path: 'advanced',
                name: 'Advanced Tables',
                component: () => import('@/views/tables/advanced-table.vue'),
            },
        ],
    },
]

// map
const mapRoutes = [
    {
        path: '/maps',
        name: 'Maps',
        icon: 'uil-location-point',
        meta: {authRequired: true},
        children: [
            {
                path: 'google-map',
                name: 'Google Maps',
                component: () => import('@/views/maps/google-map.vue'),
            },
            {
                path: 'vector-map',
                name: 'Vector Maps',
                component: () => import('@/views/maps/vector-map.vue'),
            }
        ],
    },

]


const appRoutes = [...calendarAppsRoutes, ...chatAppsRoutes, ...crmAppsRoutes, ...ecommerceAppsRoutes, ...emailAppsRoutes, ...projectAppsRoutes,  ...socialFeedAppsRoutes,...taskAppsRoutes, ...fileManagerAppsRoutes]

const customRoutes = [...pagesRoutes,...landingRoutes,...layoutRoutes]

const componentRoutes = [...uiRoutes, ...extendedRoutes, ...widgetRoute, ...iconsRoutes, ...chartsRoutes, ...formsRoutes, ...tablesRoutes, ...mapRoutes]

export const authProtectedRoutes = [...dashboardRoutes, ...appRoutes, ...customRoutes, ...componentRoutes]

export const allRoutes = [
    ...homeRoute,
    ...landingRoutes,
    ...dashboardRoutes, 
    ...authRoutes, 
    ...errorPageRoutes, 
    ...authProtectedRoutes]
