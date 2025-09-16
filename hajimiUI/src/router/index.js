import { createRouter, createWebHistory } from 'vue-router'
import DashboardView from '../views/DashboardView.vue'
import LoginView from '../views/LoginView.vue'

// 检查用户是否已认证
function isAuthenticated() {
  // 每次刷新都需要重新登录，所以始终返回false
  return false
}

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: LoginView,
    },
    {
      path: '/',
      name: 'dashboard',
      component: DashboardView,
      meta: { requiresAuth: true },
    },
    // 重定向所有其他路径到仪表盘
    {
      path: '/:pathMatch(.*)*',
      redirect: '/'
    }
  ],
})

// 全局路由守卫
router.beforeEach((to, from, next) => {
  // 如果路由需要认证（仪表盘）
  if (to.meta.requiresAuth) {
    // 每次刷新都需要重新登录，始终跳转到登录页
    next('/login')
  } else {
    next() // 访问登录页或其他不需要认证的页面
  }
})

export default router
