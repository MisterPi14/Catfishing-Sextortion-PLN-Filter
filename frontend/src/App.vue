<template>
  <div class="app">
    <router-view />
  </div>
</template>

<script setup>
// No local state needed here, router handles it
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
