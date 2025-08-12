import {defineStore} from "pinia";
import axios from "axios";
import {useStorage} from "@vueuse/core";

export const useAuthStore = defineStore("auth", {

    state: () => ({
        authUser: useStorage('authUser', null)
    }),

    getters: {
        user: (state) => state.authUser
    },

    actions: {

        async fetchUser(id: number) {
            const res = await axios.get(`/api/users/${id}`);
            this.authUser = await res.data;
        },

        async register(name: string, email: string, password: string) {
            const res = await axios.post("/api/register", {name, email, password});
            this.authUser = await res.data
        },

        async logIn(email: string, password: string) {
            const res = await axios.post("/api/login", {email, password});
            this.authUser = await res.data;
        },

         logout() {
            this.authUser = null
        }
    }
})