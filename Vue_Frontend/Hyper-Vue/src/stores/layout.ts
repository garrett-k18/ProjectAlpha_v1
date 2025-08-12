import {defineStore} from "pinia";
import {useStorage} from "@vueuse/core";

export const defaultConfig = {
    layoutType: "vertical",

    theme: "light",

    nav: "vertical",

    layout: {
        mode: "fluid",
        position: "fixed",
    },

    topbar: {
        color: "light",
    },

    menu: {
        color: "dark",
    },

    // This option for only vertical (left Sidebar) layout
    sidenav: {
        size: "default",
        user: false,
    },
};

const html = document.getElementsByTagName("html")[0];

export const useLayoutStore = defineStore("layout", {
    state: () => {
        return {
            isRightSidebarOpen: false,
            config: useStorage("__CONFIG__", {
                layoutType: "vertical",

                theme: "light",

                nav: "vertical",

                layout: {
                    mode: "fluid",
                    position: "fixed",
                },

                topbar: {
                    color: "light",
                },

                menu: {
                    color: "dark",
                },

                // This option for only vertical (left Sidebar) layout
                sidenav: {
                    size: "default",
                    user: false,
                },
            }),
        };
    },
    actions: {
        init() {
            var layoutColor = html.getAttribute('data-bs-theme');
            this.config['theme'] = layoutColor !== null ? layoutColor : this.config.theme;

            var layoutNav = html.getAttribute('data-layout');
            this.config['nav'] = layoutNav != null ? layoutNav == 'topnav' ? 'horizontal' : 'vertical' : this.config.nav;

            var layoutSize = html.getAttribute('data-layout-mode');
            this.config['layout']['mode'] = layoutSize !== null ? layoutSize : this.config.layout.mode;

            var layoutMode = html.getAttribute('data-layout-position');
            this.config['layout']['position'] = layoutMode !== null ? layoutMode : this.config.layout.position;

            var topbarColor = html.getAttribute('data-topbar-color');
            this.config['topbar']['color'] = topbarColor != null ? topbarColor : this.config.topbar.color;

            var leftbarSize = html.getAttribute('data-sidenav-size');
            this.config['sidenav']['size'] = leftbarSize !== null ? leftbarSize : this.config.sidenav.size;

            var sidebarUser = html.getAttribute('data-sidenav-user')
            this.config['sidenav']['user'] = sidebarUser !== null ? true : this.config.sidenav.user;

            var menuColor = html.getAttribute('data-menu-color');
            this.config['menu']['color'] = menuColor !== null ? menuColor : this.config.menu.color;


            if (html.getAttribute("data-layout") == "topnav") {
                this.config.nav = "horizontal"
            } else {
                this.config.nav = "vertical"
            }

            if (this.config) {
                html.setAttribute("data-bs-theme", this.config.theme);
                html.setAttribute("data-layout-mode", this.config.layout.mode);
                html.setAttribute("data-menu-color", this.config.menu.color);
                html.setAttribute("data-topbar-color", this.config.topbar.color);
                html.setAttribute("data-layout-position", this.config.layout.position);
                if (this.config.nav == "vertical") {
                    let size = this.config.sidenav.size;
                    if (window.innerWidth <= 767) {
                        size = "full";
                    } else if (window.innerWidth >= 767 && window.innerWidth <= 1140) {
                        if (this.config.sidenav.size !== 'full' && this.config.sidenav.size !== 'fullscreen') {
                            size = "condensed";
                        }
                    }
                    html.setAttribute("data-sidenav-size", size);
                    if (this.config.sidenav.user && this.config.sidenav.user.toString() === "true") {
                        html.setAttribute("data-sidenav-user", "true");
                    } else {
                        html.removeAttribute("data-sidenav-user");
                    }
                }
            }
        },

        changeLayoutType(type: string) {
            this.config.layoutType = type;
            this.setSwitchFromConfig();
            this.initSwitchListener()
        },

        changeMenuColor(color: string) {
            this.config.menu.color = color;
            html.setAttribute('data-menu-color', color);
            this.setSwitchFromConfig();
        },

        changeLeftbarSize(size: string, save = true) {
            html.setAttribute('data-sidenav-size', size);
            if (save) {
                this.config.sidenav.size = size;
                this.setSwitchFromConfig();
            }
        },

        changeLayoutMode(mode: string, save = true) {
            html.setAttribute('data-layout-mode', mode);
            if (save) {
                this.config.layout.mode = mode;
                this.setSwitchFromConfig();
            }
        },

        changeLayoutPosition(position: string) {
            this.config.layout.position = position;
            html.setAttribute('data-layout-position', position);
            this.setSwitchFromConfig();
        },

        changeLayoutColor(color: string) {
            this.config.theme = color;
            html.setAttribute('data-bs-theme', color);
            this.setSwitchFromConfig();
        },

        changeTopbarColor(color: string) {
            this.config.topbar.color = color;
            html.setAttribute('data-topbar-color', color);
            this.setSwitchFromConfig();
        },

        changeSidebarUser(showUser: boolean) {

            this.config.sidenav.user = showUser;
            if (showUser) {
                html.setAttribute('data-sidenav-user', showUser.toString());
            } else {
                html.removeAttribute('data-sidenav-user');
            }
            this.setSwitchFromConfig();
        },

        resetTheme() {
            this.config.layoutType = defaultConfig.layoutType
            this.changeMenuColor(defaultConfig.menu.color);
            this.changeLeftbarSize(defaultConfig.sidenav.size);
            this.changeLayoutColor(defaultConfig.theme);
            this.changeLayoutMode(defaultConfig.layout.mode);
            this.changeLayoutPosition(defaultConfig.layout.position);
            this.changeTopbarColor(defaultConfig.topbar.color);
            this.changeSidebarUser(defaultConfig.sidenav.user);
            this.setSwitchFromConfig();
            this._adjustLayout();
        },

        initSwitchListener() {
            var self = this;
            document.querySelectorAll<HTMLInputElement>('input[name=data-menu-color]').forEach(function (element) {
                element.addEventListener('change', function (e) {
                    self.changeMenuColor(element.value);
                })
            });

            document.querySelectorAll<HTMLInputElement>('input[name=data-sidenav-size]').forEach(function (element) {
                element.addEventListener('change', function (e) {
                    self.changeLeftbarSize(element.value);
                })
            });

            document.querySelectorAll<HTMLInputElement>('input[name=data-bs-theme]').forEach(function (element) {
                element.addEventListener('change', function (e) {
                    self.changeLayoutColor(element.value);
                })
            });
            document.querySelectorAll<HTMLInputElement>('input[name=data-layout-mode]').forEach(function (element) {
                element.addEventListener('change', function (e) {
                    self.changeLayoutMode(element.value);
                })
            });

            document.querySelectorAll<HTMLInputElement>('input[name=data-layout-position]').forEach(function (element) {
                element.addEventListener('change', function (e) {
                    self.changeLayoutPosition(element.value);
                })
            });
            document.querySelectorAll<HTMLInputElement>('input[name=data-layout]').forEach(function (element) {
                element.addEventListener('change', function (e) {
                    self.changeLayoutType(element.value)
                })
            });
            document.querySelectorAll<HTMLInputElement>('input[name=data-topbar-color]').forEach(function (element) {
                element.addEventListener('change', function (e) {
                    self.changeTopbarColor(element.value);
                })
            });
            document.querySelectorAll<HTMLInputElement>('input[name=sidebar-user]').forEach(function (element) {
                element.addEventListener('change', function (e) {
                    self.changeSidebarUser(element.checked);
                })
            });


            //TopBar Light Dark
            var themeColorToggle = document.getElementById('light-dark-mode');
            if (themeColorToggle) {
                themeColorToggle.addEventListener('click', function (e) {

                    if (self.config.theme === 'light') {
                        self.changeLayoutColor('dark');
                    } else {
                        self.changeLayoutColor('light');
                    }
                });
            }

            var resetBtn = document.querySelector('#reset-layout')
            if (resetBtn) {
                resetBtn.addEventListener('click', function (e) {
                    self.resetTheme();
                });
            }

            var menuToggleBtn = document.querySelector('.button-toggle-menu');
            if (menuToggleBtn) {
                menuToggleBtn.addEventListener('click', function () {
                    var configSize = self.config.sidenav.size;
                    var size = html.getAttribute('data-sidenav-size');

                    if (size === 'full') {
                        self.showBackdrop();
                    } else {
                        if (configSize == 'fullscreen') {
                            if (size === 'fullscreen') {
                                self.changeLeftbarSize(configSize == 'fullscreen' ? 'default' : configSize, false);
                            } else {
                                self.changeLeftbarSize('fullscreen', false);
                            }
                        } else {
                            if (size === 'condensed') {
                                self.changeLeftbarSize(configSize == 'condensed' ? 'default' : configSize, false);
                            } else {
                                self.changeLeftbarSize('condensed', false);
                            }
                        }
                    }

                    // Todo: old implementation
                    html.classList.toggle('sidebar-enable');

                });
            }

            let horizontalMenuToggleBtn = document.querySelector('.horizontal-button-toggle-menu')
            if (horizontalMenuToggleBtn) {
                let horizontalMenu = document.getElementById('topnav-menu-content')
                horizontalMenuToggleBtn.addEventListener('click', () => {
                    if (horizontalMenu?.classList.contains('show')) {
                        return horizontalMenu?.classList.remove('show')
                    }
                    horizontalMenu?.classList.add('show')
                })
            }

            var menuCloseBtn = document.querySelector('.button-close-fullsidebar');
            if (menuCloseBtn) {
                menuCloseBtn.addEventListener('click', function () {
                    html.classList.remove('sidebar-enable');
                    self.hideBackdrop();
                });
            }

            var hoverBtn = document.querySelectorAll('.button-sm-hover');
            hoverBtn.forEach(function (element) {
                element.addEventListener('click', function () {
                    var configSize = self.config.sidenav.size;
                    var size = html.getAttribute('data-sidenav-size');

                    if (size === 'sm-hover-active') {
                        self.changeLeftbarSize('sm-hover', false);
                    } else {
                        self.changeLeftbarSize('sm-hover-active', false);
                    }
                });
            })
        },

        showBackdrop() {
            const backdrop = document.createElement('div');
            backdrop.id = 'custom-backdrop';
            backdrop.classList.add('offcanvas-backdrop', 'fade', 'show')
            document.body.appendChild(backdrop);
            document.body.style.overflow = "hidden";
            if (window.innerWidth > 767) {
                document.body.style.paddingRight = "15px";
            }
            const self = this
            backdrop.addEventListener('click', function (e) {
                html.classList.remove('sidebar-enable');
                self.hideBackdrop();
            })
        },

        hideBackdrop() {
            var backdrop = document.getElementById('custom-backdrop');
            if (backdrop) {
                document.body.removeChild(backdrop);
                document.body.style.overflow = '';
                document.body.style.paddingRight = '';
            }
        },


        initWindowSize() {
            var self = this;
            window.addEventListener('resize', function (e) {
                self._adjustLayout();
            })
        },

        _adjustLayout() {
            var self = this;

            if (window.innerWidth <= 767.98) {
                self.changeLeftbarSize('full', false);
            } else if (window.innerWidth >= 767 && window.innerWidth <= 1140) {
                if (self.config.sidenav.size !== 'full' && self.config.sidenav.size !== 'fullscreen') {
                    if (self.config.sidenav.size === 'sm-hover') {
                        self.changeLeftbarSize('condensed');
                    } else {
                        self.changeLeftbarSize('condensed', false);
                    }
                }
            } else {
                self.changeLeftbarSize(self.config.sidenav.size);
                self.changeLayoutMode(self.config.layout.mode);
            }
        },

        setSwitchFromConfig() {

            document.querySelectorAll<HTMLInputElement>('.right-bar input[type=checkbox]').forEach(function (checkbox) {
                checkbox.checked = false;
            })


            var layoutColorSwitch = document.querySelector<HTMLInputElement>('input[type=radio][name=data-bs-theme][value=' + this.config.theme + ']');
            var layoutModeSwitch = document.querySelector<HTMLInputElement>('input[type=radio][name=data-layout-mode][value=' + this.config.layout.mode + ']');
            var topbarColorSwitch = document.querySelector<HTMLInputElement>('input[type=radio][name=data-topbar-color][value=' + this.config.topbar.color + ']');
            var menuColorSwitch = document.querySelector<HTMLInputElement>('input[type=radio][name=data-menu-color][value=' + this.config.menu.color + ']');
            var leftbarSizeSwitch = document.querySelector<HTMLInputElement>('input[type=radio][name=data-sidenav-size][value=' + this.config.sidenav.size + ']');
            var layoutSizeSwitch = document.querySelector<HTMLInputElement>('input[type=radio][name=data-layout-position][value=' + this.config.layout.position + ']');
            var sidebarUserSwitch = document.querySelector<HTMLInputElement>('input[type=checkbox][name=sidebar-user]');
            var layoutNavSwitch = document.querySelector<HTMLInputElement>('input[type=radio][name=data-layout][value=' + this.config.layoutType + ']');

            if (layoutColorSwitch) layoutColorSwitch.checked = true;
            if (layoutModeSwitch) layoutModeSwitch.checked = true;
            if (topbarColorSwitch) topbarColorSwitch.checked = true;
            if (menuColorSwitch) menuColorSwitch.checked = true;
            if (leftbarSizeSwitch) leftbarSizeSwitch.checked = true;
            if (layoutSizeSwitch) layoutSizeSwitch.checked = true;
            if (sidebarUserSwitch && this.config.sidenav.user.toString() === "true") sidebarUserSwitch.checked = true;
            if (layoutNavSwitch) layoutNavSwitch.checked = true;


        },

        initConfig() {
            this.initSwitchListener();
            this.initWindowSize();
            this._adjustLayout();
            this.setSwitchFromConfig();
        }
    },
});
