import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { getCurrentUser, login as apiLogin, logout as apiLogout } from '../api/auth'
import router from '../router'

const TOKEN_KEY = 'access_token'
const REFRESH_KEY = 'refresh_token'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem(TOKEN_KEY) || '')
  const user = ref(null)
  const initialized = ref(false)

  const isLoggedIn = computed(() => !!token.value)

  function setToken(access, refresh = '') {
    token.value = access
    if (access) localStorage.setItem(TOKEN_KEY, access)
    else localStorage.removeItem(TOKEN_KEY)
    if (refresh) localStorage.setItem(REFRESH_KEY, refresh)
    else localStorage.removeItem(REFRESH_KEY)
    // 当设置新 token 时，标记为未初始化，需要重新获取用户信息
    if (access) initialized.value = false
  }

  async function fetchUser() {
    if (!token.value) {
      initialized.value = true
      return
    }
    try {
      const res = await getCurrentUser()
      user.value = res.data || null
      initialized.value = true
      return user.value
    } catch {
      setToken('')
      user.value = null
      initialized.value = true
    }
  }

  async function login(credentials) {
    const res = await apiLogin(credentials)
    const { access, refresh } = res.data || {}
    setToken(access, refresh)
    await fetchUser()
  }

  async function logout() {
    try {
      await apiLogout()
    } catch {}
    setToken('')
    user.value = null
    router.push('/login')
  }

  async function initFromStorage() {
    if (initialized.value) return
    if (token.value && !user.value) {
      await fetchUser()
    } else {
      initialized.value = true
    }
  }

  return {
    token,
    user,
    initialized,
    isLoggedIn,
    setToken,
    fetchUser,
    login,
    logout,
    initFromStorage,
  }
})
