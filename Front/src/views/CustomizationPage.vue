<script setup>
import { onMounted, reactive, ref } from "vue";
import { useAuthStore } from "../store/auth";
import GlassCard from "../components/ui/GlassCard.vue";
import { customizationApi } from "../api";

const wishes = ref([]);
const message = ref("");
const form = reactive({
  title: "",
  description: "",
  budget: 0,
  due_date: "",
});

const auth = useAuthStore();

const loadWishes = async () => {
  const res = await customizationApi.list();
  wishes.value = res.results ?? res;
};

const submitWish = async () => {
  message.value = "";
  try {
    await customizationApi.create(form);
    await loadWishes();
    Object.assign(form, { title: "", description: "", budget: 0, due_date: "" });
    message.value = "已提交定制请求";
  } catch (err) {
    message.value = err?.response?.data?.detail || "提交失败";
  }
};

const addNote = async (wish) => {
  const text = prompt("输入互动信息");
  if (!text) return;
  await customizationApi.addTimeline(wish.id, { message: text });
  await loadWishes();
};

const claimWish = async (wish) => {
  if (!["MERCHANT", "ADMIN"].includes(auth.role)) return;
  await customizationApi.assign(wish.id);
  await loadWishes();
};

onMounted(loadWishes);
</script>

<template>
  <div class="grid">
    <GlassCard title="定制请求">
      <article v-for="wish in wishes" :key="wish.id" class="wish-card">
        <header>
          <div>
            <p class="eyebrow">{{ wish.consumer }}</p>
            <h3>{{ wish.title }}</h3>
          </div>
          <span class="status">{{ wish.status }}</span>
        </header>
        <p>{{ wish.description }}</p>
        <p class="budget">预算：¥{{ wish.budget || "待确认" }}</p>
        <div class="timeline">
          <p v-for="entry in wish.timeline" :key="entry.id">
            <strong>{{ entry.author }}</strong>：{{ entry.message }}
          </p>
        </div>
        <div class="actions">
          <button class="btn-outline" @click="addNote(wish)">互动</button>
          <button
            v-if="['MERCHANT', 'ADMIN'].includes(auth.role)"
            class="btn-primary"
            @click="claimWish(wish)"
          >
            认领
          </button>
        </div>
      </article>
      <p v-if="!wishes.length" class="empty">快来发布第一条定制心愿吧</p>
    </GlassCard>

    <GlassCard title="创建新心愿">
      <form class="form" @submit.prevent="submitWish">
        <label>主题 <input v-model="form.title" required /></label>
        <label>描述 <textarea v-model="form.description" rows="4" required /></label>
        <label>预算 <input v-model.number="form.budget" type="number" min="0" /></label>
        <label>期望完成日期 <input v-model="form.due_date" type="date" /></label>
        <button class="btn-primary">提交</button>
        <p v-if="message">{{ message }}</p>
      </form>
    </GlassCard>
  </div>
</template>

<style scoped>
.grid {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 24px;
}

@media (max-width: 1024px) {
  .grid {
    grid-template-columns: 1fr;
  }
}

.wish-card {
  padding: 18px;
  border-radius: 20px;
  border: 1px solid rgba(15, 45, 31, 0.08);
  background: rgba(255, 255, 255, 0.85);
  margin-bottom: 16px;
}

.status {
  font-weight: 600;
}

.budget {
  color: #4d6359;
}

.timeline {
  margin: 12px 0;
  padding: 12px;
  border-radius: 12px;
  background: rgba(111, 207, 151, 0.12);
}

.actions {
  display: flex;
  gap: 12px;
}

.form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.empty {
  color: #6c7f74;
}
</style>
