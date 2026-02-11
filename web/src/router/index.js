import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: () => import('../views/LoginView.vue'),
      meta: { hideLayout: true }
    },
    {
      path: '/',
      name: 'home',
      component: HomeView,
    },
    {
      path: '/dashboard',
      name: 'dashboard',
      component: () => import('../views/DashboardView.vue'),
    },
    {
      path: '/dashboard/analysis',
      name: 'dashboard-analysis',
      component: () => import('../views/DashboardView.vue'),
    },
    {
      path: '/dashboard/monitor',
      name: 'dashboard-monitor',
      component: () => import('../views/DashboardView.vue'),
    },
    {
      path: '/dashboard/workplace',
      name: 'dashboard-workplace',
      component: () => import('../views/DashboardView.vue'),
    },
    {
      path: '/users',
      name: 'users',
      component: () => import('../views/UsersView.vue'),
    },
    {
      path: '/users/list',
      name: 'users-list',
      component: () => import('../views/UsersView.vue'),
    },
    {
      path: '/users/roles',
      name: 'users-roles',
      component: () => import('../views/UsersView.vue'),
    },
    {
      path: '/users/permissions',
      name: 'users-permissions',
      component: () => import('../views/UsersView.vue'),
    },
    {
      path: '/about',
      name: 'about',
      component: () => import('../views/AboutView.vue'),
    },
  ],
})

export default router
