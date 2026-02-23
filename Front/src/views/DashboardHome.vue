<script setup>
import { computed, onBeforeUnmount, onMounted, reactive, ref, watch } from "vue";
import { RouterLink } from "vue-router";
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
    image: "https://images.unsplash.com/photo-1500534314209-a25ddb2bd429?auto=format&fit=crop&w=1000&q=60",
  },
  {
    title: "定制你的故事",
    description: "刻字、烫金、手写祝福，每一份礼物都代表独一份心意。",
    image: "https://images.unsplash.com/photo-1470246973918-29a93221c455?auto=format&fit=crop&w=1000&q=60",
  },
  {
    title: "一起玩转好物聚焦",
    description: "每周甄选 5 款人气单品，聆听背后的设计灵感。",
    image: "https://images.unsplash.com/photo-1498050108023-c5249f4df085?auto=format&fit=crop&w=1000&q=60",
  },
]);
const currentStory = ref(0);
let storyTimer = null;

const consumerLoading = ref(true);
const consumerError = ref("");
const featuredProducts = ref([]);
const curatedTiles = [
  { title: "店铺广场", desc: "打卡摊位 & 合作推荐", to: "store" },
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
  <v-container fluid>
    <div v-if="isConsumer" class="consumer-home">
      <v-carousel v-model="currentStory" :show-arrows="false" hide-delimiters cycle>
        <v-carousel-item v-for="(story, i) in consumerStories" :key="i" :src="story.image" cover>
          <v-row class="fill-height ma-0" align="end" justify="center">
            <v-col class="white--text text-center" cols="12">
              <div class="text-h4 font-weight-bold">{{ story.title }}</div>
              <div class="text-subtitle-1">{{ story.description }}</div>
            </v-col>
          </v-row>
        </v-carousel-item>
      </v-carousel>

      <v-row>
        <v-col v-for="tile in curatedTiles" :key="tile.title" cols="12" md="4">
          <v-card :to="{ name: tile.to }">
            <v-card-title>{{ tile.title }}</v-card-title>
            <v-card-subtitle>{{ tile.desc }}</v-card-subtitle>
            <v-card-actions>
              <v-btn text color="primary">前往</v-btn>
            </v-card-actions>
          </v-card>
        </v-col>
      </v-row>

    </div>

    <div v-else>
      <v-row>
        <v-col cols="12">
          <v-card>
            <v-card-title class="headline">校园文创驾驶舱</v-card-title>
            <v-card-subtitle>商品、销售、定制、数据、社区五位一体，尽在此处</v-card-subtitle>
            <v-card-actions>
              <v-btn color="primary" @click="loadDashboard">刷新数据</v-btn>
            </v-card-actions>
          </v-card>
        </v-col>
      </v-row>

      <v-row>
        <v-col cols="12" md="4">
          <v-card>
            <v-card-title>七日销售额</v-card-title>
            <v-card-text>
              <p class="text-h4">¥{{ Number(overview.sales_last_7_days).toFixed(2) }}</p>
              <p>环比 +12%</p>
            </v-card-text>
          </v-card>
        </v-col>
        <v-col cols="12" md="4">
          <v-card>
            <v-card-title>七日订单</v-card-title>
            <v-card-text>
              <p class="text-h4">{{ overview.orders_last_7_days }}</p>
              <p>成交率 68%</p>
            </v-card-text>
          </v-card>
        </v-col>
        <v-col cols="12" md="4">
          <v-card>
            <v-card-title>活跃商品</v-card-title>
            <v-card-text>
              <p class="text-h4">{{ overview.active_products }}</p>
              <p>库存健康</p>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>

      <v-row>
        <v-col cols="12" md="6">
          <v-card>
            <v-card-title>最近订单</v-card-title>
            <v-list>
              <v-list-item v-for="order in recentOrders" :key="order.id">
                <v-list-item-content>
                  <v-list-item-title>#{{ order.order_number }}</v-list-item-title>
                  <v-list-item-subtitle>{{ order.consumer }} · {{ order.merchant }}</v-list-item-subtitle>
                </v-list-item-content>
                <v-list-item-action>
                  <v-chip>{{ order.status }}</v-chip>
                </v-list-item-action>
              </v-list-item>
              <v-list-item v-if="!recentOrders.length">
                <v-list-item-content>
                  <v-list-item-title class="text-center">暂时没有订单</v-list-item-title>
                </v-list-item-content>
              </v-list-item>
            </v-list>
          </v-card>
        </v-col>
        <v-col cols="12" md="6">
          <v-card>
            <v-card-title>定制心愿</v-card-title>
            <v-list>
              <v-list-item v-for="wish in wishes.slice(0, 4)" :key="wish.id">
                <v-list-item-content>
                  <v-list-item-title>{{ wish.title }}</v-list-item-title>
                  <v-list-item-subtitle>{{ wish.status }}</v-list-item-subtitle>
                </v-list-item-content>
                <v-list-item-action>
                  <v-chip>{{ wish.budget ? ('¥' + wish.budget) : "待报价" }}</v-chip>
                </v-list-item-action>
              </v-list-item>
              <v-list-item v-if="!wishes.length">
                <v-list-item-content>
                  <v-list-item-title class="text-center">还没有许愿清单</v-list-item-title>
                </v-list-item-content>
              </v-list-item>
            </v-list>
          </v-card>
        </v-col>
      </v-row>

      <v-row>
        <v-col cols="12">
          <v-card>
            <v-card-title>
              互动社区
              <v-btn color="primary" class="ml-4" @click="openPostModal">发布灵感</v-btn>
            </v-card-title>
            <v-list>
              <v-list-item v-for="post in posts.slice(0, 3)" :key="post.id">
                <v-list-item-content>
                  <v-list-item-title>{{ post.title }}</v-list-item-title>
                  <v-list-item-subtitle>{{ post.content.slice(0, 120) }}</v-list-item-subtitle>
                </v-list-item-content>
                <v-list-item-action>
                  <span>{{ post.author }}</span>
                  <span>{{ new Date(post.created_at).toLocaleString() }}</span>
                </v-list-item-action>
              </v-list-item>
              <v-list-item v-if="!posts.length">
                <v-list-item-content>
                  <v-list-item-title class="text-center">暂无帖子，来发第一条吧～</v-list-item-title>
                </v-list-item-content>
              </v-list-item>
            </v-list>
          </v-card>
        </v-col>
      </v-row>

      <v-dialog v-model="showPostModal" max-width="600px">
        <v-card>
          <v-card-title>发布灵感</v-card-title>
          <v-card-text>
            <v-text-field v-model.trim="newPost.title" label="标题" placeholder="输入标题"></v-text-field>
            <v-textarea v-model.trim="newPost.content" label="内容" rows="5" placeholder="分享你的灵感"></v-textarea>
            <v-alert v-if="postError" type="error">{{ postError }}</v-alert>
          </v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn text @click="closePostModal" :disabled="posting">取消</v-btn>
            <v-btn color="primary" @click="submitPost" :loading="posting">
              {{ posting ? "发布中.." : "发布" }}
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>
    </div>
  </v-container>
</template>













