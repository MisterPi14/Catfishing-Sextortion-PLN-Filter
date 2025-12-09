<template>
  <div class="app">
    <LoginView v-if="!isAuthenticated" />
    <ChatView v-else />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import authService from './services/authService'
import LoginView from './views/LoginView.vue'
import ChatView from './views/ChatView.vue'

const isAuthenticated = computed(() => authService.isAuthenticated())
</script>

<style>
html, body, #app {
  height: 100%;
  width: 100%;
}

.app {
  height: 100vh;
  width: 100%;
}
</style>
