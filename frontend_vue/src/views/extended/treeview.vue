<template>
  <Layout>
    <Breadcrumb :title="title" :items="items"/>
    <div class="row">
      <div class="col-md-6">

        <CustomSyntax title="Basic Treeview">
          <template v-slot:sub-text>
          </template>
          <template v-slot:preview>
            <CustomTreeview id="jstree-1" :option="option1">
              <ul>
                <li>
                  Root node 1
                  <ul>
                    <li data-jstree='{ "selected" : true }'>
                      <a href="javascript:;"> Initially selected </a>
                    </li>
                    <li data-jstree='{ "icon" : "ri-home-4-line text-success " }'>
                      custom icon URL
                    </li>
                    <li data-jstree='{ "opened" : true }'>
                      initially open
                      <ul>
                        <li data-jstree='{ "disabled" : true }'>
                          Disabled Node
                        </li>
                        <li data-jstree='{ "type" : "file" }'>
                          Another node
                        </li>
                      </ul>
                    </li>
                    <li data-jstree='{ "icon" : "ri-vip-diamond-line text-danger" }'>
                      Custom icon class (bootstrap)
                    </li>
                  </ul>
                </li>
                <li data-jstree='{ "type" : "link" }'>
                  <a href="https://coderthemes.com/"> Clickable link node </a>
                </li>
              </ul>
            </CustomTreeview>
          </template>
        </CustomSyntax>

        <CustomSyntax title="Custom Icons & Clickable Nodes">
          <template v-slot:sub-text>
          </template>
          <template v-slot:preview>
            <CustomTreeview id="jstree-2" :option="option2">
              <ul>
                <li>
                  Root node 1
                  <ul>
                    <li data-jstree='{ "selected" : true }'>
                      <a href="javascript:;"> Initially selected </a>
                    </li>
                    <li data-jstree='{ "icon" : "ri-article-line text-success " }'>
                      custom icon URL
                    </li>
                    <li data-jstree='{ "opened" : true }'>
                      initially open
                      <ul>
                        <li data-jstree='{ "disabled" : true }'>
                          Disabled Node
                        </li>
                        <li data-jstree='{ "type" : "file" }'>
                          Another node
                        </li>
                      </ul>
                    </li>
                    <li data-jstree='{ "icon" : "ri-user-line text-danger" }'>
                      Custom icon class (bootstrap)
                    </li>
                  </ul>
                </li>
                <li data-jstree='{ "type" : "link" }'>
                  <a href="https://coderthemes.com/"> Clickable link node </a>
                </li>
              </ul>
            </CustomTreeview>
          </template>
        </CustomSyntax>

        <CustomSyntax title="Checkable Tree">
          <template v-slot:sub-text>
          </template>
          <template v-slot:preview>
            <CustomTreeview id="jstree-3" :option="option3"/>
          </template>
        </CustomSyntax>

      </div>

      <div class="col-md-6">

        <CustomSyntax title="Contextual Menu">
          <template v-slot:sub-text>
          </template>
          <template v-slot:preview>
            <CustomTreeview id="jstree-4" :option="option4"/>
          </template>
        </CustomSyntax>

        <CustomSyntax title="Drag & Drop">
          <template v-slot:sub-text>
          </template>
          <template v-slot:preview>
            <CustomTreeview id="jstree-5" :option="option5"/>
          </template>
        </CustomSyntax>

        <CustomSyntax title="Ajax Data">
          <template v-slot:sub-text>
          </template>
          <template v-slot:preview>
            <CustomTreeview id="jstree-6" :option="option6"/>
          </template>
        </CustomSyntax>

      </div>
    </div>
  </Layout>
</template>

<script lang="ts">
import Layout from "@/components/layouts/layout.vue";
import Breadcrumb from "@/components/breadcrumb.vue";
import CustomTreeview from "@/components/custom/custom-treeview.vue";
import CustomSyntax from "@/components/custom/custom-syntax.vue";

export default {
  components: {CustomSyntax, CustomTreeview, Breadcrumb, Layout},
  data() {
    return {
      title: 'Treeview',
      items: [
        {
          text: 'Hyper',
          href: '/',
        },
        {
          text: 'Extended UI',
          href: '/',
        },
        {
          text: 'Treeview',
          active: true,
        },
      ],

      option1: {
        "core": {
          "themes": {
            "responsive": false
          }
        },
        "types": {
          "default": {
            "icon": "ri-folder-line"
          },
          "file": {
            "icon": "ri-article-line"
          }
        },
        "plugins": ["types"]
      },
      option2: {
        "core": {
          "themes": {
            "responsive": false
          }
        },
        "types": {
          "default": {
            "icon": "ri-folder-line text-warning"
          },
          "file": {
            "icon": "ri-article-line  text-warning"
          }
        },
        "plugins": ["types"]
      },
      option3: {
        "plugins": ["wholerow", "checkbox", "types"],
        "core": {
          "themes": {
            "responsive": false
          },
          "data": [{
            "text": "Same but with checkboxes",
            "children": [{
              "text": "initially selected",
              "state": {
                "selected": true
              }
            }, {
              "text": "custom icon",
              "icon": "ri-feedback-line text-danger"
            }, {
              "text": "initially open",
              "icon": "ri-folder-line text-default",
              "state": {
                "opened": true
              },
              "children": ["Another node"]
            }, {
              "text": "custom icon",
              "icon": "ri-article-line text-warning"
            }, {
              "text": "disabled node",
              "icon": "ri-close-circle-line text-success",
              "state": {
                "disabled": true
              }
            }]
          },
            "And wholerow selection"
          ]
        },
        "types": {
          "default": {
            "icon": "ri-folder-line text-warning"
          },
          "file": {
            "icon": "ri-article-line  text-warning"
          }
        },
      },
      option4: {
        "core": {
          "themes": {
            "responsive": false
          },
          // so that create works
          "check_callback": true,
          "data": [{
            "text": "Parent Node",
            "children": [{
              "text": "Initially selected",
              "state": {
                "selected": true
              }
            }, {
              "text": "Custom Icon",
              "icon": "ri-feedback-line text-danger"
            }, {
              "text": "Initially open",
              "icon": "ri-folder-line text-success",
              "state": {
                "opened": true
              },
              "children": [{
                "text": "Another node",
                "icon": "ri-article-line text-warning"
              }]
            }, {
              "text": "Another Custom Icon",
              "icon": "ri-article-line text-warning"
            }, {
              "text": "Disabled Node",
              "icon": "ri-close-circle-line text-success",
              "state": {
                "disabled": true
              }
            }, {
              "text": "Sub Nodes",
              "icon": "ri-folder-line text-danger",
              "children": [{
                "text": "Item 1",
                "icon": "ri-article-line text-warning"
              },
                {
                  "text": "Item 2",
                  "icon": "ri-article-line text-success"
                },
                {
                  "text": "Item 3",
                  "icon": "ri-article-line text-default"
                },
                {
                  "text": "Item 4",
                  "icon": "ri-article-line text-danger"
                },
                {
                  "text": "Item 5",
                  "icon": "ri-article-line text-info"
                }
              ]
            }]
          },
            "Another Node"
          ]
        },
        "types": {
          "default": {
            "icon": "ri-folder-line text-primary"
          },
          "file": {
            "icon": "ri-article-line  text-primary"
          }
        },
        "state": {
          "key": "demo2"
        },
        "plugins": ["contextmenu", "state", "types"]
      },
      option5: {
        "core": {
          "themes": {
            "responsive": false
          },
          // so that create works
          "check_callback": true,
          "data": [{
            "text": "Parent Node",
            "children": [{
              "text": "Initially selected",
              "state": {
                "selected": true
              }
            }, {
              "text": "Custom Icon",
              "icon": "ri-article-line text-danger"
            }, {
              "text": "Initially open",
              "icon": "ri-folder-line text-success",
              "state": {
                "opened": true
              },
              "children": [{
                "text": "Another node",
                "icon": "ri-article-line text-warning"
              }]
            }, {
              "text": "Another Custom Icon",
              "icon": "ri-line-chart-line text-warning"
            }, {
              "text": "Disabled Node",
              "icon": "ri-close-circle-line text-success",
              "state": {
                "disabled": true
              }
            }, {
              "text": "Sub Nodes",
              "icon": "ri-folder-line text-danger",
              "children": [{
                "text": "Item 1",
                "icon": "ri-article-line text-warning"
              },
                {
                  "text": "Item 2",
                  "icon": "ri-article-line text-success"
                },
                {
                  "text": "Item 3",
                  "icon": "ri-article-line text-default"
                },
                {
                  "text": "Item 4",
                  "icon": "ri-article-line text-danger"
                },
                {
                  "text": "Item 5",
                  "icon": "ri-article-line text-info"
                }
              ]
            }]
          },
            "Another Node"
          ]
        },
        "types": {
          "default": {
            "icon": "ri-folder-line text-success"
          },
          "file": {
            "icon": "ri-article-line  text-success"
          }
        },
        "state": {
          "key": "demo2"
        },
        "plugins": ["dnd", "state", "types"]
      },
      option6: {
        "core": {
          "themes": {
            "responsive": false
          },
          // so that create works
          "check_callback": true,
          'data': {
            'url': function (node) {
              return node.id === '#' ?
                  '/src/assets/data/ajax_demo_children.json' : '/src/assets/data/ajax_demo_children.json';
            },
            'data': function (node) {
              return {'id': node.id};
            }
          }
        },
        "types": {
          "default": {
            "icon": "ri-folder-line text-primary"
          },
          "file": {
            "icon": "ri-article-line  text-primary"
          }
        },
        "state": {
          "key": "demo3"
        },
        "plugins": ["dnd", "state", "types"]
      }
    }
  },
  mounted() {
    $('#jstree-1').on('select_node.jstree', function (e, data) {
      var link = $('#' + data.selected).find('a');
      if (link.attr("href") != "#" && link.attr("href") != "javascript:;" && link.attr("href") != "") {
        if (link.attr("target") == "_blank") {
          link.attr("href").target = "_blank";
        }
        document.location.href = link.attr("href");
        return false;
      }
    });

    $('#jstree-2').on('select_node.jstree', function (e, data) {
      var link = $('#' + data.selected).find('a');
      if (link.attr("href") != "#" && link.attr("href") != "javascript:;" && link.attr("href") != "") {
        if (link.attr("target") == "_blank") {
          link.attr("href").target = "_blank";
        }
        document.location.href = link.attr("href");
        return false;
      }
    });
  }

}
</script>
