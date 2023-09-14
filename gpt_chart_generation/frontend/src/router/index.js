import Vue from 'vue'
import VueRouter from 'vue-router'
import LoginPage from '@/views/LoginPage';
import DashboardPage from '@/views/Dashboard';

Vue.use(VueRouter)

const routes = [
    {
        path: '/',
        redirect: {
            name: "dashboard"
        }
    },
    {
        path: "/login",
        name: "login",
        component: LoginPage
    },
    {
        path: "/dashboard",
        name: "dashboard",
        component: DashboardPage
    }
]

const router = new VueRouter({
    mode: 'history',
    base: process.env.BASE_URL,
    routes
})

export default router
