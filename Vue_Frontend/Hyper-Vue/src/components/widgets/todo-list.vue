<template>
  <div class="card">
    <div class="card-header d-flex justify-content-between align-items-center">
      <h4 class="header-title">{{ title }}</h4>
      <b-dropdown
        variant="white"
        class="float-end"
        toggle-class="arrow-none card-drop p-0"
        right
      >
        <template v-slot:button-content>
          <i class="mdi mdi-dots-vertical"></i>
        </template>
        <b-dropdown-item href="javascript:void(0);">Settings</b-dropdown-item>
        <b-dropdown-item href="javascript:void(0);">Action</b-dropdown-item>
      </b-dropdown>
    </div>

    <div class="todoapp mt-1">
      <div class="card-body pt-0">
        <b-row class="align-items-between">
          <b-col sm="6">
            <h5 id="todo-message">
              <span id="todo-remaining">{{ completedTodo.length }}</span> of
              <span id="todo-total">{{ todoItems.length }}</span> remaining
            </h5>
          </b-col>
          <b-col sm="6">
            <a
              href="javascript: void(0);"
              class="float-end btn btn-light btn-sm"
              @click="archiveTodo"
              >Archive</a
            >
          </b-col>
        </b-row>
        <simplebar :style="`max-height:${todoWindowHeight}`">
          <div>
            <ul id="todo-list" class="list-group list-group-flush todo-list">
              <li
                v-for="(todo, index) of todoItems"
                :key="index"
                class="list-group-item border-0 ps-0"
              >
                <div class="form-check mb-0">
                  <b-form-checkbox class="todo-done" v-model="todo.isCompleted">
                    <s v-if="todo.isCompleted">{{ todo.task }}</s>
                    <span v-else>{{ todo.task }}</span>
                  </b-form-checkbox>
                </div>
              </li>
            </ul>
          </div>
        </simplebar>
        <form @submit.prevent="saveTodo">
          <b-row class="mt-1">
            <b-col lg="10">
              <input
                v-model="newTodoItem.task"
                type="text"
                class="form-control"
                placeholder="Add new todo"
                name="todo"
              />
            </b-col>
            <b-col lg="2">
              <b-button variant="primary" type="submit" class="width-sm"
                >Add
              </b-button>
            </b-col>
          </b-row>
        </form>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import simplebar from "simplebar-vue";

/**
 * Todo component
 * 1. User specifies the title of window using the 'title' input property.
 * 2. Window height set using the 'todoWindowHeight' input property. Height would count in pixel.
 * 3. Todolist array specify the id, todo, done task.
 *    id - specify the unique id of todo
 *    todo - specify the name
 *    done - Specify the todo done or not using checkbox checked value. Checkbox checked specify the done todo.
 */
export default {
  components: { simplebar },
  props: {
    title: {
      type: String,
      default: "Todo",
    },
    todoWindowHeight: {
      type: String,
      default: "404",
    },
    items: {
      type: Array,
      default: function () {
        return [];
      },
    },
  },
  data() {
    return {
      todoItems: [...this.items],
      newTodoItem: {
        task: "",
      },
      isSubmitted: false,
    };
  },
  // validations: {
  //   newTodoItem: {
  //     task: {required},
  //   },
  // },
  computed: {
    /**
     * return completed todo
     */
    completedTodo() {
      return this.todoItems.filter((t) => t.isCompleted === false);
    },
  },
  methods: {
    /**
     * Todo form submit
     */
    saveTodo() {
      this.isSubmitted = true;
      if (this.newTodoItem.task.length == 0) {
        return;
      } else {
        let id = this.todoItems.length;
        const task = this.newTodoItem.task;
        // Value Push in Todo
        this.todoItems.push({
          id: id + 1,
          task,
          isCompleted: false,
        });
      }
      this.isSubmitted = false;
      this.newTodoItem = {};
    },

    /**
     * Check box value change
     */
    togleStatus(index) {
      this.todoItems[index].isCompleted = !this.todoItems[index].isCompleted;
    },

    /**
     * Hide Selected todo
     */
    archiveTodo() {
      // eslint-disable-next-line no-return-assign
      return (this.todoItems = this.todoItems.filter(
        (x) => x.isCompleted === false
      ));
    },
  },
};
</script>
