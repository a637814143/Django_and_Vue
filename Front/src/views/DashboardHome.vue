<script setup>
import { computed, onBeforeUnmount, onMounted, reactive, ref, watch } from "vue";
import { RouterLink } from "vue-router";
import GlassCard from "../components/ui/GlassCard.vue";
import MetricCard from "../components/ui/MetricCard.vue";
import { analyticsApi, orderApi, customizationApi, communityApi, catalogApi } from "../api";
import { useAuthStore } from "../store/auth";

const auth = useAuthStore();
const isConsumer = computed(() => auth.role === "CONSUMER");

const overview = ref({
  sales_last_7_days: 0,
  orders_last_7_days: 0,
  custom_requests_last_7_days: 0,
  active_products: 0,
});
const recentOrders = ref([]);
const wishes = ref([]);
const posts = ref([]);
const loading = ref(true);
const error = ref("");
const showPostModal = ref(false);
const posting = ref(false);
const postError = ref("");
const newPost = reactive({
  title: "",
  content: "",
});

const adminSlides = ref([]);
const currentAdminSlide = ref(0);
let adminTimer = null;

const consumerStories = ref([
  {
    title: "遇见灵感摊位",
    description: "在校园操场市集挑选限定手工好物，收藏每一次心动。",
    image:
      "https://images.unsplash.com/photo-1500534314209-a25ddb2bd429?auto=format&fit=crop&w=1000&q=60",
  },
  {
    title: "定制你的故事",
    description: "刻字、烫金、手写祝福，每一份礼物都代表独一份心意。",
    image:
      "https://images.unsplash.com/photo-1470246973918-29a93221c455?auto=format&fit=crop&w=1000&q=60",
  },
  {
    title: "一起玩转好物聚焦",
    description: "每周甄选 5 款人气单品，聆听背后的设计灵感。",
    image:
      "https://images.unsplash.com/photo-1498050108023-c5249f4df085?auto=format&fit=crop&w=1000&q=60",
  },
]);
const currentStory = ref(0);
let storyTimer = null;

const consumerLoading = ref(true);
const consumerError = ref("");
const featuredProducts = ref([]);
const curatedTiles = [
  { title: "好物聚焦", desc: "故事墙轮播精选灵感", to: "focus" },
  { title: "店铺广场", desc: "打卡摊位 & 合作社", to: "store" },
  { title: "定制灵感", desc: "DIY 刻字一键预约", to: "consumer-products" },
];

const startAdminCarousel = () => {
  if (adminTimer || adminSlides.value.length <= 1) return;
  adminTimer = setInterval(() => {
    currentAdminSlide.value = (currentAdminSlide.value + 1) % adminSlides.value.length;
  }, 5000);
};

const stopAdminCarousel = () => {
  if (adminTimer) {
    clearInterval(adminTimer);
    adminTimer = null;
  }
};

const startStoryRotation = () => {
  if (storyTimer || consumerStories.value.length <= 1) return;
  storyTimer = setInterval(() => {
    currentStory.value = (currentStory.value + 1) % consumerStories.value.length;
  }, 4500);
};

const stopStoryRotation = () => {
  if (storyTimer) {
    clearInterval(storyTimer);
    storyTimer = null;
  }
};

const loadDashboard = async () => {
  loading.value = true;
  error.value = "";
  try {
    const [metrics, orders, wishList, community] = await Promise.all([
      analyticsApi.overview(),
      orderApi.list({ page_size: 5 }),
      customizationApi.list(),
      communityApi.posts(),
    ]);
    overview.value = metrics;
    recentOrders.value = orders.results ?? orders;
    wishes.value = wishList.results ?? wishList;
    posts.value = community.results ?? community;
  } catch (err) {
    error.value = err?.response?.data?.detail || "加载仪表盘失败";
  } finally {
    loading.value = false;
  }
};

const loadConsumerShowcase = async () => {
  consumerLoading.value = true;
  consumerError.value = "";
  try {
    const [productRes, community] = await Promise.all([
      catalogApi.products({ ordering: "-updated_at", page_size: 8 }),
      communityApi.posts(),
    ]);
    featuredProducts.value = (productRes.results ?? productRes).slice(0, 6);
    posts.value = community.results ?? community;
  } catch (err) {
    consumerError.value = err?.response?.data?.detail || "加载推荐内容失败";
  } finally {
    consumerLoading.value = false;
  }
};

const openPostModal = () => {
  showPostModal.value = true;
  postError.value = "";
};

const closePostModal = () => {
  showPostModal.value = false;
  newPost.title = "";
  newPost.content = "";
  postError.value = "";
};

const submitPost = async () => {
  if (!newPost.title.trim() || !newPost.content.trim()) {
    postError.value = "请填写标题和内容";
    return;
  }
  posting.value = true;
  postError.value = "";
  try {
    const created = await communityApi.createPost({
      title: newPost.title.trim(),
      content: newPost.content.trim(),
    });
    posts.value = [created, ...(posts.value || [])];
    closePostModal();
  } catch (err) {
    postError.value = err?.response?.data?.detail || "发布失败，请稍后重试";
  } finally {
    posting.value = false;
  }
};

const bootstrapForRole = (role) => {
  stopAdminCarousel();
  stopStoryRotation();
  if (role === "CONSUMER") {
    loadConsumerShowcase();
    startStoryRotation();
  } else {
    loadDashboard();
    startAdminCarousel();
  }
};

onMounted(() => {
  bootstrapForRole(isConsumer.value ? "CONSUMER" : "BUSINESS");
});

watch(isConsumer, (value, oldValue) => {
  if (value === oldValue) return;
  bootstrapForRole(value ? "CONSUMER" : "BUSINESS");
});

onBeforeUnmount(() => {
  stopAdminCarousel();
  stopStoryRotation();
});
</script>

<template>
  <div v-if="isConsumer" class="consumer-home">
    <section
      class="consumer-hero glass"
      :style="{ backgroundImage: `url(${consumerStories[currentStory].image})` }"
    >
      <div class="hero-overlay">
        <p class="eyebrow">灵感旅程</p>
        <h1>{{ consumerStories[currentStory].title }}</h1>
        <p>{{ consumerStories[currentStory].description }}</p>
        <div class="cta-row">
          <RouterLink class="btn-primary" :to="{ name: 'store' }">去逛店</RouterLink>
          <RouterLink class="btn-outline" :to="{ name: 'focus' }">看看好物</RouterLink>
        </div>
        <div class="hero-dots">
          <button
            v-for="(story, index) in consumerStories"
            :key="story.title"
            :class="['dot', { active: index === currentStory }]"
            @click="currentStory = index"
            :aria-label="`切换到 ${story.title}`"
          ></button>
        </div>
      </div>
    </section>

    <div class="consumer-tiles">
      <RouterLink
        v-for="tile in curatedTiles"
        :key="tile.title"
        class="tile glass"
        :to="{ name: tile.to }"
      >
        <h3>{{ tile.title }}</h3>
        <p>{{ tile.desc }}</p>
        <span class="tile-cta">前往</span>
      </RouterLink>
    </div>

    <GlassCard title="灵感好物" subtitle="每次刷新都有惊喜">
      <p v-if="consumerError" class="error">{{ consumerError }}</p>
      <div v-if="consumerLoading" class="loading">精选加载中...</div>
      <div v-else-if="featuredProducts.length" class="product-grid">
        <article v-for="product in featuredProducts" :key="product.id" class="product-card">
          <p class="tag">{{ product.category?.name || "未分类" }}</p>
          <h4>{{ product.title }}</h4>
          <p class="desc">{{ product.description || "灵感待补充" }}</p>
          <div class="product-meta">
            <span>库存 {{ product.inventory }}</span>
            <strong>¥{{ Number(product.price).toFixed(2) }}</strong>
          </div>
        </article>
      </div>
      <p v-else class="empty">还没有上架的商品，稍后再来逛逛。</p>
    </GlassCard>

    <GlassCard title="灵感社区" subtitle="最新帖子">
      <div class="post-head">
        <div>
          <p class="eyebrow">社区</p>
          <h3>最新帖子</h3>
        </div>
        <button class="btn-primary" type="button" @click="openPostModal">发布灵感</button>
      </div>
      <div class="post-feed">
        <article v-for="post in posts.slice(0, 3)" :key="post.id" class="post-card">
          <h4>{{ post.title }}</h4>
          <p>{{ post.content.slice(0, 120) }}</p>
          <div class="meta">
            <span>{{ post.author }}</span>
            <span>{{ new Date(post.created_at).toLocaleString() }}</span>
          </div>
        </article>
        <p v-if="!posts.length" class="empty">暂无帖子，来发第一条吧。</p>
      </div>
    </GlassCard>
  </div>

  <template v-else>
    <section class="hero glass">
      <div>
        <p class="eyebrow">校园文创驾驶舱</p>
        <h1>清新自然的 Apple 级体验</h1>
        <p class="subtitle">商品、销售、定制、数据、社区五位一体，尽在此处</p>
      </div>
      <button class="btn-primary" @click="loadDashboard">刷新数据</button>
    </section>

    <div v-if="adminSlides.length" class="carousel glass">
      <div
        class="carousel__media"
        :style="{ backgroundImage: `url(${adminSlides[currentAdminSlide].image})` }"
      >
        <div class="carousel__overlay">
          <p class="eyebrow">策略速递</p>
          <h2>{{ adminSlides[currentAdminSlide].title }}</h2>
          <p>{{ adminSlides[currentAdminSlide].description }}</p>
        </div>
      </div>
      <div class="carousel__nav">
        <button
          v-for="(slide, index) in adminSlides"
          :key="slide.title"
          :class="['dot', { active: index === currentAdminSlide }]"
          @click="currentAdminSlide = index"
          :aria-label="`切换到 ${slide.title}`"
        ></button>
      </div>
    </div>

    <div v-if="error" class="error glass">{{ error }}</div>

    <section class="grid-3">
      <MetricCard
        title="七日销售额"
        :value="`¥${Number(overview.sales_last_7_days).toFixed(2)}`"
        trend="环比 +12%"
      />
      <MetricCard title="七日订单" :value="overview.orders_last_7_days" trend="成交率 68%" />
      <MetricCard title="活跃商品" :value="overview.active_products" trend="库存健康" />
    </section>

    <div class="grid-2">
      <GlassCard title="最近订单" subtitle="在线销售">
        <ul class="list">
          <li v-for="order in recentOrders" :key="order.id">
            <div>
              <strong>#{{ order.order_number }}</strong>
              <p>{{ order.consumer }} · {{ order.merchant }}</p>
            </div>
            <div class="status">{{ order.status }}</div>
          </li>
          <li v-if="!recentOrders.length" class="empty">暂时没有订单</li>
        </ul>
      </GlassCard>

      <GlassCard title="定制心愿" subtitle="消费者 · 商家">
        <ul class="list">
          <li v-for="wish in wishes.slice(0, 4)" :key="wish.id">
            <div>
              <strong>{{ wish.title }}</strong>
              <p>{{ wish.status }}</p>
            </div>
            <div class="pill">{{ wish.budget ? `¥${wish.budget}` : "待报价" }}</div>
          </li>
          <li v-if="!wishes.length" class="empty">还没有许愿请求</li>
        </ul>
      </GlassCard>
    </div>

    <GlassCard title="互动社区" subtitle="设计灵感">
      <div class="post-head">
        <div>
          <p class="eyebrow">社区</p>
          <h3>最新帖子</h3>
        </div>
        <button class="btn-primary" type="button" @click="openPostModal">发布灵感</button>
      </div>
      <div class="post-feed">
        <article v-for="post in posts.slice(0, 3)" :key="post.id" class="post-card">
          <h4>{{ post.title }}</h4>
          <p>{{ post.content.slice(0, 120) }}</p>
          <div class="meta">
            <span>{{ post.author }}</span>
            <span>{{ new Date(post.created_at).toLocaleString() }}</span>
          </div>
        </article>
        <p v-if="!posts.length" class="empty">暂无帖子，来发第一条吧。</p>
      </div>
    </GlassCard>
  </template>

  <div v-if="showPostModal" class="modal-backdrop" @click.self="closePostModal">
    <div class="modal">
      <h3>发布灵感</h3>
      <label class="label">标题</label>
      <input v-model.trim="newPost.title" class="input" placeholder="输入标题" />
      <label class="label">内容</label>
      <textarea v-model.trim="newPost.content" class="textarea" rows="5" placeholder="分享你的灵感"></textarea>
      <p v-if="postError" class="error">{{ postError }}</p>
      <div class="modal-actions">
        <button class="btn-secondary" type="button" @click="closePostModal" :disabled="posting">取消</button>
        <button class="btn-primary" type="button" @click="submitPost" :disabled="posting">
          {{ posting ? "发布中..." : "发布" }}
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.consumer-home {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.consumer-hero {
  min-height: 280px;
  border-radius: 26px;
  background-size: cover;
  background-position: center;
  position: relative;
  padding: 0;
  overflow: hidden;
}

.hero-overlay {
  background: linear-gradient(180deg, rgba(3, 25, 18, 0.05), rgba(3, 25, 18, 0.75));
  color: #fff;
  height: 100%;
  padding: 32px;
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
  gap: 12px;
}

.cta-row {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.hero-dots {
  display: flex;
  gap: 8px;
  margin-top: 12px;
}

.consumer-tiles {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 16px;
}

.tile {
  border-radius: 22px;
  text-decoration: none;
  color: inherit;
}

.tile h3 {
  margin: 0 0 6px;
}

.tile-cta {
  font-size: 0.85rem;
  color: #0f2d1f;
  opacity: 0.7;
}

.product-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.product-card {
  border-radius: 20px;
  padding: 18px;
  border: 1px solid rgba(15, 45, 31, 0.08);
  background: rgba(255, 255, 255, 0.92);
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.product-card .desc {
  color: #4d6359;
  flex: 1;
}

.product-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.tag {
  font-size: 0.75rem;
  color: #4d6359;
}

.loading,
.empty {
  text-align: center;
  color: #6b7f73;
  padding: 16px 0;
}

.hero {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 24px;
}

.subtitle {
  color: #4d6359;
}

.carousel {
  margin: 24px 0;
  padding: 0;
  overflow: hidden;
}

.carousel__media {
  min-height: 260px;
  border-radius: 24px;
  background-size: cover;
  background-position: center;
  display: flex;
  align-items: flex-end;
}

.carousel__overlay {
  background: linear-gradient(180deg, rgba(3, 25, 18, 0.05), rgba(3, 25, 18, 0.65));
  color: #fff;
  width: 100%;
  border-radius: 24px;
  padding: 32px;
}

.carousel__nav {
  display: flex;
  gap: 8px;
  justify-content: center;
  padding: 16px 0 8px;
}

.dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  border: none;
  background: rgba(15, 45, 31, 0.2);
  cursor: pointer;
  transition: transform 0.2s ease, background 0.2s ease;
}

.dot.active {
  background: rgba(111, 207, 151, 0.8);
  transform: scale(1.1);
}

.grid-3 {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 20px;
}

.grid-2 {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
  margin: 24px 0;
}

.list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.list li {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px;
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.7);
}

.list .empty {
  justify-content: center;
  color: #73877b;
}

.status {
  font-weight: 600;
  color: #4a5c53;
}

.post-feed {
  display: grid;
  gap: 16px;
}

.post-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.post-card {
  padding: 18px;
  border-radius: 18px;
  border: 1px solid rgba(15, 45, 31, 0.08);
  background: rgba(255, 255, 255, 0.8);
}

.post-card h4 {
  margin: 0 0 6px;
}

.post-card p {
  margin: 0;
  color: #4d6359;
}

.meta {
  display: flex;
  justify-content: space-between;
  margin-top: 12px;
  font-size: 0.85rem;
  color: #6c7f74;
}

.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.35);
  display: grid;
  place-items: center;
  z-index: 1000;
}

.modal {
  width: min(520px, 90vw);
  background: #fff;
  border-radius: 16px;
  padding: 20px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.label {
  font-weight: 600;
  color: #1f2937;
}

.input,
.textarea {
  width: 100%;
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  padding: 10px 12px;
  font-size: 1rem;
}

.textarea {
  resize: vertical;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 8px;
}

.btn-secondary {
  border: 1px solid #e5e7eb;
  background: #f8fafc;
  color: #1f2937;
  padding: 8px 14px;
  border-radius: 10px;
  cursor: pointer;
}

.error {
  color: #b42318;
  font-weight: 600;
}
</style>
