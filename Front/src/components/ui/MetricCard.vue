<script setup>
defineProps({
  title: String,
  value: [String, Number],
  trend: String,
  accent: {
    type: String,
    default: "#6fcf97",
  },
});
</script>

<template>
  <div class="metric-card glass" :style="{ borderColor: accent }">
    <p class="label">{{ title }}</p>
    <h3>{{ value }}</h3>
    <p class="trend">{{ trend }}</p>
  </div>
</template>

<style scoped>
.metric-card {
  border-radius: 24px;
  padding: 20px;
}

.label {
  margin: 0;
  font-size: 0.9rem;
  color: #4a5c53;
}

h3 {
  margin: 6px 0;
  font-size: 2rem;
  color: #0f2d1f;
}

.trend {
  margin: 0;
  color: #4a5c53;
  font-size: 0.9rem;
}
</style>
