import {defineStore} from "pinia";
import {useStorage} from "@vueuse/core";

const fakeData = {
    name: 'Hyper',
    email: 'test@test.com',
    pass: 'password'
}

export const useFakeAuthStore = defineStore("fakeAuth", {
    state: () => ({
        fakeUser: useStorage('fakeUser', {name: '', email: ''})
    }),
    getters: {
        user: (state) => state.fakeUser,
        isAuthenticated: (state) => {
            return state.fakeUser.email.length > 0 && state.fakeUser.name.length > 0;
        }
    },
    actions: {
        register(name: string, email: string, password: string) {
            if (password == '' || email == '' || name == '') {
                return false
            } else {
                this.fakeUser.name = name
                this.fakeUser.email = email
                return true
            }
        },
        logIn(email: string, password: string) {
            if (fakeData.email == email && fakeData.pass == password) {
                this.fakeUser.name = fakeData.name
                this.fakeUser.email = fakeData.email
                return true
            }
            return false
        },
        logout() {
            this.fakeUser = {name: '', email: ''}
        }
    }
})