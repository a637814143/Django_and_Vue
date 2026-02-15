<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, reactive, ref, watch } from "vue";
import GlassCard from "../components/ui/GlassCard.vue";
import { focusApi } from "../api";
import { useAuthStore } from "../store/auth";

const auth = useAuthStore();
const canUpload = ["CONSUMER", "MERCHANT"].includes(auth.role);
const videos = ref([]);
const loading = ref(true);
const error = ref("");
const uploading = ref(false);
const uploadError = ref("");
const showUploadPanel = ref(false);

const commentsPanel = reactive({
  loading: false,
  items: [],
  newComment: "",
});
const commentInputRef = ref(null);

const uploadForm = reactive({
  title: "",
  description: "",
  video_file: null,
});
const currentIndex = ref(0);
const heroActionError = ref("");
const deletingHero = ref(false);
const playerCanvasRef = ref(null);
const heroHeight = ref(0);
const stretchedHeight = computed(() => (heroHeight.value ? heroHeight.value * 1.25 : 0));
const detailsColumnStyle = computed(() => {
  if (!stretchedHeight.value) return {};
  const px = `${Math.round(stretchedHeight.value)}px`;
  return { height: px, maxHeight: px };
});
const playerCanvasStyle = computed(() => {
  if (!stretchedHeight.value) return {};
  return { height: `${Math.round(stretchedHeight.value)}px` };
});

const heroVideo = computed(() => {
  if (!videos.value.length) return null;
  return videos.value[currentIndex.value] ?? videos.value[0];
});
const canNavigate = computed(() => videos.value.length > 1);
const canDeleteHero = computed(() => Boolean(heroVideo.value?.can_delete));

watch(
  () => videos.value.length,
  (len) => {
    if (!len) {
      currentIndex.value = 0;
      return;
    }
    if (currentIndex.value > len - 1) {
      currentIndex.value = 0;
    }
  },
);

const syncHeroHeight = () => {
  const width = playerCanvasRef.value?.offsetWidth || 0;
  heroHeight.value = width ? (width * 9) / 16 : 0;
};

const loadComments = async (videoId) => {
  commentsPanel.loading = true;
  try {
    const res = await focusApi.comments(videoId);
    commentsPanel.items = res;
  } catch (err) {
    commentsPanel.items = [];
  } finally {
    commentsPanel.loading = false;
  }
};

const refreshComments = () => {
  const video = heroVideo.value;
  if (!video) return;
  loadComments(video.id);
};

const focusCommentInput = () => {
  commentInputRef.value?.focus();
};

watch(
  () => heroVideo.value?.id,
  async (id) => {
    commentsPanel.items = [];
    commentsPanel.newComment = "";
    await nextTick();
    syncHeroHeight();
    if (id) {
      loadComments(id);
    }
  },
  { immediate: true },
);

const toggleUploadPanel = () => {
  if (!canUpload) return;
  showUploadPanel.value = !showUploadPanel.value;
  if (!showUploadPanel.value) {
    uploadError.value = "";
  }
  heroActionError.value = "";
};

const cancelUpload = () => {
  showUploadPanel.value = false;
  uploadError.value = "";
  heroActionError.value = "";
};

const loadFeed = async () => {
  loading.value = true;
  error.value = "";
  const activeId = heroVideo.value?.id ?? null;
  try {
    const data = await focusApi.videos();
    const list = data.results ?? data;
    videos.value = list;
    if (list.length) {
      const nextIndex = activeId ? list.findIndex((item) => item.id === activeId) : -1;
      currentIndex.value = nextIndex >= 0 ? nextIndex : Math.min(currentIndex.value, list.length - 1);
    } else {
      currentIndex.value = 0;
    }
  } catch (err) {
    error.value = err?.response?.data?.detail || "加载视频失败";
  } finally {
    loading.value = false;
    heroActionError.value = "";
    nextTick(syncHeroHeight);
  }
};

const handleFileChange = (event) => {
  const file = event.target.files?.[0];
  uploadForm.video_file = file || null;
};

const goPrev = () => {
  heroActionError.value = "";
  if (!canNavigate.value) return;
  currentIndex.value = (currentIndex.value - 1 + videos.value.length) % videos.value.length;
};

const goNext = () => {
  heroActionError.value = "";
  if (!canNavigate.value) return;
  currentIndex.value = (currentIndex.value + 1) % videos.value.length;
};

const deleteHero = async () => {
  heroActionError.value = "";
  const current = heroVideo.value;
  if (!current || !canDeleteHero.value || deletingHero.value) return;
  try {
    deletingHero.value = true;
    await focusApi.remove(current.id);
    const index = videos.value.findIndex((video) => video.id === current.id);
    if (index !== -1) {
      videos.value.splice(index, 1);
    }
    if (!videos.value.length) {
      currentIndex.value = 0;
    } else if (currentIndex.value >= videos.value.length) {
      currentIndex.value = 0;
    }
  } catch (err) {
    heroActionError.value = err?.response?.data?.detail || "删除失败";
  } finally {
    deletingHero.value = false;
    nextTick(syncHeroHeight);
  }
};

const submitUpload = async () => {
  uploadError.value = "";
  if (!uploadForm.title.trim() || !uploadForm.video_file) {
    uploadError.value = "请填写标题并选择视频";
    return;
  }
  try {
    uploading.value = true;
    await focusApi.upload({
      title: uploadForm.title.trim(),
      description: uploadForm.description.trim(),
      video_file: uploadForm.video_file,
    });
    Object.assign(uploadForm, { title: "", description: "", video_file: null });
    cancelUpload();
    await loadFeed();
  } catch (err) {
    uploadError.value = err?.response?.data?.detail || "上传失败";
  } finally {
    uploading.value = false;
  }
};

const toggleLike = async (video) => {
  try {
    const res = await focusApi.like(video.id);
    video.is_liked = res.liked;
    video.like_count = res.like_count;
  } catch (err) {
    // ignore
  }
};

const submitComment = async () => {
  const current = heroVideo.value;
  if (!current || !commentsPanel.newComment.trim()) return;
  const content = commentsPanel.newComment.trim();
  commentsPanel.loading = true;
  try {
    const res = await focusApi.addComment(current.id, { content });
    commentsPanel.items.unshift(res);
    current.comment_count += 1;
    commentsPanel.newComment = "";
  } catch (err) {
    // ignore
  } finally {
    commentsPanel.loading = false;
  }
};

onMounted(() => {
  loadFeed();
  nextTick(syncHeroHeight);
  window.addEventListener("resize", syncHeroHeight);
});

onBeforeUnmount(() => {
  window.removeEventListener("resize", syncHeroHeight);
});
</script>

<template>
  <div class="focus-page">
    <div v-if="loading" class="loading">视频加载中...</div>
    <p v-else-if="error" class="error">{{ error }}</p>
    <div v-else class="focus-body">
      <GlassCard class="hero-shell">
        <div class="hero-layout">
          <div class="player-column">
            <div class="player-frame">
              <div
                class="player-canvas"
                :class="{ 'is-empty': !heroVideo }"
                ref="playerCanvasRef"
                :style="playerCanvasStyle"
              >
                <div v-if="heroVideo" class="video-frame">
                  <video
                    :key="heroVideo.id"
                    :src="heroVideo.video_url"
                    autoplay
                    muted
                    loop
                    playsinline
                    controls
                    :poster="heroVideo.cover_url"
                  ></video>
                </div>
                <div v-else class="empty-player">
                  <p>暂无视频，点击右上角「+」开启第一条灵感</p>
                </div>
                <div v-if="canUpload || heroVideo" class="hero-controls">
                  <button
                    v-if="canUpload"
                    class="hero-control upload-trigger"
                    type="button"
                    @click="toggleUploadPanel"
                    aria-label="上传视频"
                  >
                    {{ showUploadPanel ? "×" : "+" }}
                  </button>
                  <button
                    class="hero-control"
                    type="button"
                    @click="deleteHero"
                    :disabled="!heroVideo || !canDeleteHero || deletingHero"
                    aria-label="删除当前视频"
                  >
                    -
                  </button>
                  <button
                    class="hero-control"
                    type="button"
                    @click="goPrev"
                    :disabled="!heroVideo || !canNavigate"
                    aria-label="上一个视频"
                  >
                    up
                  </button>
                  <button
                    class="hero-control"
                    type="button"
                    @click="goNext"
                    :disabled="!heroVideo || !canNavigate"
                    aria-label="下一个视频"
                  >
                    down
                  </button>
                </div>
                <transition name="upload-fade">
                  <form v-if="showUploadPanel" class="upload-panel" @submit.prevent="submitUpload">
                    <label>
                      标题
                      <input v-model="uploadForm.title" placeholder="青柠灵感套装" />
                    </label>
                    <label>
                      描述
                      <textarea v-model="uploadForm.description" rows="2" placeholder="分享创作故事" />
                    </label>
                    <label>
                      上传视频
                      <input type="file" accept="video/*" @change="handleFileChange" />
                    </label>
                    <div class="panel-actions">
                      <button class="ghost" type="button" @click="cancelUpload">取消</button>
                      <button class="btn-primary" type="submit" :disabled="uploading">
                        {{ uploading ? "上传中..." : "发布" }}
                      </button>
                    </div>
                    <p v-if="uploadError" class="error">{{ uploadError }}</p>
                  </form>
                </transition>
              </div>
            </div>
          </div>
          <div class="details-column" :style="detailsColumnStyle">
            <template v-if="heroVideo">
              <div class="details-scroll">
                <div class="hero-meta">
                  <div class="hero-meta__header">
                    <div>
                      <p class="eyebrow">{{ heroVideo.creator }}</p>
                      <h2>{{ heroVideo.title }}</h2>
                    </div>
                    <div class="actions">
                      <button :class="['icon-btn', { liked: heroVideo.is_liked }]" @click="toggleLike(heroVideo)">
                        ❤️ {{ heroVideo.like_count }}
                      </button>
                      <button class="icon-btn" type="button" @click="focusCommentInput">
                        💬 {{ heroVideo.comment_count }}
                      </button>
                      <a class="icon-btn" :href="heroVideo.video_url" download>⬇︎ 下载</a>
                    </div>
                  </div>
                  <p>{{ heroVideo.description }}</p>
                </div>
                <section class="side-comments">
                  <header>
                    <h3>评论区</h3>
                    <button class="ghost" type="button" @click="refreshComments">刷新</button>
                  </header>
                  <div class="comments-scroll">
                    <p v-if="commentsPanel.loading">加载评论中...</p>
                    <ul v-else>
                      <li v-for="comment in commentsPanel.items" :key="comment.id">
                        <strong>{{ comment.author }}</strong>
                        <span>{{ comment.content }}</span>
                      </li>
                      <li v-if="!commentsPanel.items.length" class="empty">暂无评论</li>
                    </ul>
                  </div>
                  <div class="comments-input">
                    <input
                      ref="commentInputRef"
                      v-model="commentsPanel.newComment"
                      placeholder="写下你的想法"
                      @keyup.enter="submitComment"
                    />
                    <button class="btn-primary" type="button" @click="submitComment">发布</button>
                  </div>
                </section>
              </div>
            </template>
            <p v-else class="empty secondary">暂无视频，赶紧发布第一条灵感吧</p>
          </div>
        </div>
        <p v-if="heroActionError" class="error hero-error">{{ heroActionError }}</p>
      </GlassCard>
    </div>
  </div>
</template>

<style scoped>
.focus-page {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.focus-body {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.hero-shell {
  padding: 24px;
  border-radius: 28px;
}

.hero-layout {
  display: flex;
  gap: 3%;
  align-items: stretch;
}

.player-column {
  flex: 0 0 60%;
}

.details-column {
  flex: 0 0 37%;
  overflow: hidden;
  display: flex;
}

.details-scroll {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 18px;
  overflow-y: auto;
  padding-right: 8px;
}

.player-frame {
  width: 100%;
}

.player-canvas {
  position: relative;
  width: 100%;
  min-height: 360px;
  display: flex;
  align-items: stretch;
}

.video-frame {
  width: 100%;
  height: 100%;
  background: #0f2d1f;
  overflow: hidden;
  border-radius: 28px;
  box-shadow: 0 20px 50px rgba(15, 45, 31, 0.25);
}

.video-frame video {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.empty-player {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 32px;
  text-align: center;
  color: #6b7f73;
  background: rgba(15, 45, 31, 0.08);
  width: 100%;
  height: 100%;
  border-radius: 28px;
}

.hero-controls {
  position: absolute;
  top: 18px;
  right: 18px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  z-index: 3;
}

.hero-control {
  width: 46px;
  height: 46px;
  border-radius: 16px;
  border: none;
  background: rgba(255, 255, 255, 0.9);
  font-size: 1rem;
  font-weight: 600;
  color: #0f2d1f;
  cursor: pointer;
  transition: transform 0.18s ease, box-shadow 0.18s ease;
}

.hero-control:hover {
  transform: scale(1.05);
  box-shadow: 0 12px 24px rgba(15, 45, 31, 0.2);
}

.hero-control:disabled {
  opacity: 0.4;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.upload-trigger {
  font-size: 1.6rem;
}

.upload-panel {
  position: absolute;
  top: 18px;
  right: 72px;
  width: min(320px, 75vw);
  background: rgba(255, 255, 255, 0.98);
  box-shadow: 0 24px 70px rgba(15, 45, 31, 0.35);
  border-radius: 24px;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  z-index: 4;
}

.upload-panel label {
  display: flex;
  flex-direction: column;
  gap: 6px;
  font-size: 0.9rem;
  color: #3d4f43;
}

.upload-panel input,
.upload-panel textarea {
  border-radius: 14px;
  border: 1px solid rgba(15, 45, 31, 0.2);
  padding: 10px 14px;
  font: inherit;
}

.upload-panel textarea {
  resize: none;
}

.panel-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.hero-meta {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.hero-meta__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}

.side-comments {
  flex: 1 1 auto;
  min-height: 0;
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 18px;
  border-radius: 24px;
  background: rgba(15, 45, 31, 0.05);
  overflow: hidden;
}

.side-comments header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.comments-scroll {
  flex: 1 1 auto;
  min-height: 0;
  overflow-y: auto;
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.6);
  padding: 16px;
}

.comments-scroll ul {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.comments-scroll li strong {
  display: block;
  font-size: 0.85rem;
  color: #3d4f43;
}

.comments-scroll li span {
  display: block;
  font-size: 0.95rem;
  color: #10271b;
}

.actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.icon-btn {
  border: none;
  background: rgba(15, 45, 31, 0.08);
  padding: 8px 14px;
  border-radius: 12px;
  cursor: pointer;
}

.icon-btn.liked {
  background: rgba(250, 99, 132, 0.2);
}

.comments-input {
  display: flex;
  gap: 12px;
}

.comments-input input {
  flex: 1;
  border-radius: 16px;
  border: 1px solid rgba(15, 45, 31, 0.2);
  padding: 10px 14px;
}

.upload-fade-enter-active,
.upload-fade-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.upload-fade-enter-from,
.upload-fade-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}

.loading,
.empty {
  text-align: center;
  color: #6b7f73;
  padding: 16px 0;
}

.empty.secondary {
  font-style: italic;
}

.hero-error {
  margin: 24px 0 0;
}

@media (max-width: 960px) {
  .hero-layout {
    flex-direction: column;
    gap: 24px;
  }

  .player-column {
    flex: 1 1 auto;
  }

  .details-column {
    flex: 1 1 auto;
    height: auto;
    max-height: none;
    overflow: visible;
  }

  .details-scroll {
    overflow: visible;
    padding-right: 0;
  }

  .player-canvas {
    height: auto;
  }

  .hero-controls {
    right: 12px;
    top: 12px;
  }

  .comments-scroll {
    max-height: none;
  }
}
</style>

