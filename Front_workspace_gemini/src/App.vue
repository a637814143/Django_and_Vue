<template>
  <v-app>
    <RouterView />
  </v-app>
</template>

<script setup>
import { useAuthStore } from "./store/auth";

const auth = useAuthStore();
if (auth.isAuthenticated) {
  auth.fetchProfile();
}
</script>

<style>
/* 保证按钮可见 */
.v-btn,
.v-list-item {
  color: rgba(0, 0, 0, 0.87) !important;
}
.v-btn .v-btn__content {
  width: 100%;
  justify-content: center;
  text-align: center;
  gap: 4px;
}
.v-btn {
  position: relative;
}
/* 让前后置图标悬浮，不影响文字居中 */
.v-btn--has-prepend .v-btn__content,
.v-btn--has-append .v-btn__content {
  justify-content: center;
}
.v-btn--has-prepend .v-btn__content {
  padding-left: 32px;
}
.v-btn--has-append .v-btn__content {
  padding-right: 32px;
}
.v-btn .v-btn__prepend,
.v-btn .v-btn__append {
  margin-inline: 0 !important;
  position: absolute;
  inset-block: 0;
  display: flex;
  align-items: center;
  width: 18px;
  pointer-events: none;
}
.v-btn .v-btn__prepend {
  left: 10px;
}
.v-btn .v-btn__append {
  right: 10px;
}
.v-btn .v-icon {
  color: rgba(0, 0, 0, 0.54) !important;
}
.v-app-bar .v-btn {
  background-color: rgba(0, 0, 0, 0.1) !important;
  color: white !important;
}
.v-app-bar .v-btn .v-icon {
  color: white !important;
}
</style>
