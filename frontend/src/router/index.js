import { createRouter, createWebHistory } from 'vue-router'
import authService from '../services/authService'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/LoginView.vue'),
    meta: { requiresGuest: true }
  },
  {
    path: '/signup',
    name: 'SignUp',
    component: () => import('../views/RegisterView.vue'),
    meta: { requiresGuest: true }
  },
  {
    path: '/',
    name: 'Home',
    component: () => import('../views/ChatView.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'GeneralChat',
        component: () => import('../views/GeneralChatView.vue')
      },
      {
        path: 'chat/:id',
        name: 'ChatRoom',
        component: () => import('../views/ChatRoomView.vue'),
        props: true
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const isAuthenticated = authService.isAuthenticated()

  if (to.meta.requiresAuth && !isAuthenticated) {
    next({ name: 'Login' })
  } else if (to.meta.requiresGuest && isAuthenticated) {
    next({ name: 'Home' })
  } else {
    next()
  }
})

export default router
