import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import { useAuthStore } from '../stores/auth'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: () => import('../views/LoginView.vue'),
      meta: { hideLayout: true, guest: true },
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
      path: '/authorization/users',
      name: 'authorization-users',
      component: () => import('../views/authorization/UsersView.vue'),
    },
    {
      path: '/authorization/roles',
      name: 'authorization-roles',
      component: () => import('../views/authorization/RolesView.vue'),
    },
    {
      path: '/authorization/permissions',
      name: 'authorization-permissions',
      component: () => import('../views/authorization/PermissionsView.vue'),
    },
    {
      path: '/about',
      name: 'about',
      component: () => import('../views/AboutView.vue'),
    },
  ],
})

router.beforeEach(async (to, from, next) => {
  const auth = useAuthStore()
  await auth.initFromStorage()
  if (to.meta.guest) {
    if (auth.isLoggedIn && to.name === 'login') return next('/')
    return next()
  }
  if (!auth.isLoggedIn && to.name !== 'login') {
    return next({ name: 'login', query: { redirect: to.fullPath } })
  }
  next()
})

export default router
