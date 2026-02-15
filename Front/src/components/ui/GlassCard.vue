<script setup>
defineProps({
  title: String,
  subtitle: String,
});
</script>

<template>
  <section class="glass">
    <header class="card-header" v-if="title">
      <div>
        <p class="eyebrow" v-if="subtitle">{{ subtitle }}</p>
        <h3>{{ title }}</h3>
      </div>
      <slot name="actions" />
    </header>
    <slot />
  </section>
</template>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 18px;
}

.eyebrow {
  text-transform: uppercase;
  letter-spacing: 0.2em;
  font-size: 0.75rem;
  color: #5c6f63;
  margin: 0 0 6px;
}

h3 {
  margin: 0;
}
</style>
