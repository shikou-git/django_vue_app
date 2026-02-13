import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import HomeView from '../views/HomeView.vue'

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
      meta: { permission: 'auth.view_user' },
    },
    {
      path: '/authorization/roles',
      name: 'authorization-roles',
      component: () => import('../views/authorization/RolesView.vue'),
      meta: { permission: 'auth.view_group' },
    },
    {
      path: '/authorization/permissions',
      name: 'authorization-permissions',
      component: () => import('../views/authorization/PermissionsView.vue'),
      meta: { permission: 'auth.view_permission' },
    },
    {
      path: '/apilog',
      name: 'apilog',
      component: () => import('../views/apilog/ApiLogView.vue'),
      meta: { permission: 'apilog.view_apilog' },
    },
    {
      path: '/api_stats',
      name: 'api_stats',
      component: () => import('../views/apilog/ApiStatsView.vue'),
      meta: { permission: 'apilog.view_apilog' },
    },
    {
      path: '/403',
      name: 'forbidden',
      component: () => import('../components/result/ForbiddenView.vue'),
    },
    {
      path: '/404',
      name: 'notFound',
      component: () => import('../components/result/NotFoundView.vue'),
    },
    {
      path: '/:pathMatch(.*)*',
      name: 'notFoundCatch',
      component: () => import('../components/result/NotFoundView.vue'),
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
  // 需要权限的路由：校验当前用户是否具备 meta.permission
  const requiredPermission = to.meta.permission
  if (requiredPermission) {
    const user = auth.user
    const isSuper = user?.is_superuser === true
    const perms = user?.permissions || []
    if (!isSuper && !perms.includes(requiredPermission)) {
      return next({ name: 'forbidden' })
    }
  }
  next()
})

export default router
