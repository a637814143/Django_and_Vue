<script setup>
import { computed, onMounted, reactive, ref } from "vue";
import GlassCard from "../components/ui/GlassCard.vue";
import { communityApi } from "../api";

const posts = ref([]);
const loading = ref(false);
const loadError = ref("");

const composerOpen = ref(false);
const publishing = ref(false);
const composerError = ref("");
const composerForm = reactive({
  title: "",
  content: "",
  visibility: "PUBLIC",
});
const mediaFiles = ref([]);
const mediaPreviews = ref([]);

const detailOpen = ref(false);
const currentPostId = ref(null);
const activePost = computed(() => posts.value.find((post) => post.id === currentPostId.value) || null);
const activeMedia = computed(() => mediaFromPost(activePost.value));

const guessMediaType = (input) => {
  if (input?.type?.includes("video")) return "video";
  const url = typeof input === "string" ? input : input?.url || input?.path || input?.file || "";
  const cleanUrl = url.split("?")[0];
  const ext = cleanUrl.split(".").pop()?.toLowerCase();
  const videoExts = ["mp4", "mov", "webm", "mkv", "ogg"];
  return videoExts.includes(ext) ? "video" : "image";
};

const mediaFromPost = (post) => {
  if (!post) return [];
  const raw =
    post.media_files ||
    post.attachments ||
    post.media ||
    post.assets ||
    post.files ||
    post.gallery ||
    [];
  const list = Array.isArray(raw) ? raw : typeof raw === "string" ? [raw] : [];

  return list
    .map((item, index) => {
      if (!item) return null;
      if (typeof item === "string") {
        return {
          url: item,
          type: guessMediaType(item),
          name: item.split("/").pop() || `附件${index + 1}`,
        };
      }
      const url = item.url || item.path || item.file || item.src;
      if (!url) return null;
      return {
        url,
        type: guessMediaType(item),
        name: item.name || item.filename || item.title || `附件${index + 1}`,
      };
    })
    .filter(Boolean);
};

const clearMediaPreviews = () => {
  mediaPreviews.value.forEach((item) => {
    if (item.url?.startsWith("blob:")) {
      URL.revokeObjectURL(item.url);
    }
  });
  mediaPreviews.value = [];
  mediaFiles.value = [];
};

const loadPosts = async () => {
  loading.value = true;
  loadError.value = "";
  try {
    const res = await communityApi.posts();
    posts.value = res.results ?? res ?? [];
  } catch (err) {
    loadError.value = err?.response?.data?.detail || "加载帖子失败，请稍后重试";
  } finally {
    loading.value = false;
  }
};

const reloadKeepingDetail = async () => {
  await loadPosts();
  if (detailOpen.value && currentPostId.value) {
    const found = posts.value.find((item) => item.id === currentPostId.value);
    if (!found) {
      closeDetail();
    }
  }
};

const openComposer = () => {
  composerError.value = "";
  composerOpen.value = true;
};

const closeComposer = () => {
  composerOpen.value = false;
  composerError.value = "";
  Object.assign(composerForm, { title: "", content: "", visibility: "PUBLIC" });
  clearMediaPreviews();
};

const onFilesSelected = (event) => {
  const files = Array.from(event?.target?.files || []);
  clearMediaPreviews();
  mediaFiles.value = files;
  mediaPreviews.value = files.map((file) => ({
    name: file.name,
    type: file.type?.includes("video") ? "video" : "image",
    url: URL.createObjectURL(file),
  }));
};

const publish = async () => {
  if (!composerForm.title.trim() || !composerForm.content.trim()) {
    composerError.value = "请填写标题和内容";
    return;
  }
  publishing.value = true;
  composerError.value = "";
  try {
    await communityApi.createPost({
      title: composerForm.title.trim(),
      content: composerForm.content.trim(),
      visibility: composerForm.visibility,
      media_files: mediaFiles.value,
    });
    await loadPosts();
    closeComposer();
  } catch (err) {
    composerError.value = err?.response?.data?.detail || "发布失败，请稍后再试";
  } finally {
    publishing.value = false;
  }
};

const openDetail = (post) => {
  currentPostId.value = post.id;
  detailOpen.value = true;
};

const closeDetail = () => {
  detailOpen.value = false;
  currentPostId.value = null;
};

const comment = async (post) => {
  const text = prompt("说点什么？");
  if (!text) return;
  await communityApi.comment(post.id, { message: text });
  await reloadKeepingDetail();
};

const react = async (post, reaction_type) => {
  await communityApi.react(post.id, { reaction_type });
  await reloadKeepingDetail();
};

onMounted(loadPosts);
</script>

<template>
  <div class="grid">
    <GlassCard title="灵感发布" subtitle="集中入口">
      <template #actions>
        <button class="btn-primary" type="button" @click="openComposer">+ 发布灵感</button>
      </template>
      <p class="muted">整理好想法再发布，支持上传图片/视频附件。</p>
    </GlassCard>

    <GlassCard title="互动社区">
      <p v-if="loadError" class="error">{{ loadError }}</p>
      <p v-else-if="!posts.length && !loading" class="empty">暂时没有帖子</p>
      <p v-else-if="loading" class="muted">加载中...</p>
      <div v-else>
        <article class="post" v-for="post in posts" :key="post.id" @click="openDetail(post)">
          <header>
            <div>
              <p class="eyebrow">{{ post.visibility }}</p>
              <h3>{{ post.title }}</h3>
            </div>
            <span class="author">{{ post.author || "匿名" }}</span>
          </header>
          <p class="post-content">{{ post.content }}</p>
          <div v-if="mediaFromPost(post).length" class="media-strip">
            <span class="pill" v-for="media in mediaFromPost(post)" :key="media.url + media.name">
              {{ media.type === "video" ? "视频" : "图片" }} · {{ media.name || "附件" }}
            </span>
          </div>
          <div class="reactions">
            <button class="btn-outline" @click.stop="react(post, 'LIKE')">
              ❤️ {{ post.reactions?.length ?? 0 }}
            </button>
            <button class="btn-outline" @click.stop="comment(post)">
              评论 {{ post.comments?.length ?? 0 }}
            </button>
          </div>
          <div class="comment-list" v-if="post.comments?.length">
            <p v-for="comment in post.comments.slice(0, 2)" :key="comment.id">
              <strong>{{ comment.author }}</strong>：{{ comment.message }}
            </p>
            <p v-if="post.comments.length > 2" class="more">还有 {{ post.comments.length - 2 }} 条评论...</p>
          </div>
        </article>
      </div>
    </GlassCard>
  </div>

  <div v-if="composerOpen" class="modal-backdrop" @click.self="closeComposer">
    <div class="modal">
      <header class="modal-header">
        <div>
          <p class="eyebrow">发布灵感</p>
          <h3>和社区分享你的想法</h3>
        </div>
        <button class="btn-outline" type="button" @click="closeComposer">关闭</button>
      </header>
      <form class="form" @submit.prevent="publish">
        <label>标题 <input v-model="composerForm.title" required placeholder="一句话概括灵感" /></label>
        <label
          >内容
          <textarea
            v-model="composerForm.content"
            rows="4"
            required
            placeholder="详细描述想法、需求或进展"
          ></textarea>
        </label>
        <label>
          可见范围
          <select v-model="composerForm.visibility">
            <option value="PUBLIC">公开</option>
            <option value="MERCHANT">商家圈</option>
            <option value="INTERNAL">仅管理员</option>
          </select>
        </label>
        <label class="file-picker">
          图片 / 视频
          <input type="file" multiple accept="image/*,video/*" @change="onFilesSelected" />
        </label>
        <div v-if="mediaPreviews.length" class="preview-grid">
          <div class="media-preview" v-for="media in mediaPreviews" :key="media.url">
            <video v-if="media.type === 'video'" :src="media.url" controls />
            <img v-else :src="media.url" alt="" />
            <p>{{ media.name }}</p>
          </div>
        </div>
        <p v-if="composerError" class="error">{{ composerError }}</p>
        <div class="modal-actions">
          <button type="button" class="btn-outline" @click="closeComposer">取消</button>
          <button class="btn-primary" :disabled="publishing">
            {{ publishing ? "发布中..." : "发布" }}
          </button>
        </div>
      </form>
    </div>
  </div>

  <div v-if="detailOpen && activePost" class="modal-backdrop" @click.self="closeDetail">
    <div class="modal">
      <header class="detail-header">
        <div>
          <p class="eyebrow">{{ activePost.visibility }}</p>
          <h3>{{ activePost.title }}</h3>
          <span class="author">by {{ activePost.author || "匿名" }}</span>
        </div>
        <button class="btn-outline" type="button" @click="closeDetail">关闭</button>
      </header>
      <p class="full-content">{{ activePost.content }}</p>
      <div v-if="activeMedia.length" class="preview-grid">
        <div class="media-preview" v-for="media in activeMedia" :key="media.url">
          <video v-if="media.type === 'video'" :src="media.url" controls />
          <img v-else :src="media.url" alt="" />
          <p>{{ media.name }}</p>
        </div>
      </div>
      <div class="reactions detail-actions">
        <button class="btn-outline" @click="react(activePost, 'LIKE')">
          ❤️ {{ activePost.reactions?.length ?? 0 }}
        </button>
        <button class="btn-outline" @click="comment(activePost)">
          评论 {{ activePost.comments?.length ?? 0 }}
        </button>
      </div>
      <div class="comment-list">
        <p v-if="!activePost.comments?.length" class="muted">还没有评论</p>
        <p v-for="comment in activePost.comments || []" :key="comment.id">
          <strong>{{ comment.author }}</strong>：{{ comment.message }}
        </p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.grid {
  display: grid;
  gap: 24px;
}

.muted {
  color: #60756a;
  margin: 0;
}

.eyebrow {
  text-transform: uppercase;
  letter-spacing: 0.2em;
  font-size: 0.75rem;
  color: #5c6f63;
  margin: 0 0 6px;
}

.error {
  color: #c0392b;
  margin-top: 8px;
}

.form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.post {
  border: 1px solid rgba(15, 45, 31, 0.08);
  border-radius: 20px;
  padding: 18px;
  background: rgba(255, 255, 255, 0.9);
  margin-bottom: 18px;
  cursor: pointer;
  transition: transform 0.15s ease, box-shadow 0.15s ease;
}

.post:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 28px rgba(16, 68, 50, 0.08);
}

.author {
  color: #4c675b;
  font-size: 0.9rem;
}

.post-content {
  margin: 10px 0 6px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  color: #0f2d1f;
}

.full-content {
  margin: 12px 0;
  white-space: pre-line;
  color: #0f2d1f;
}

.media-strip {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin: 6px 0 10px;
}

.pill {
  padding: 6px 12px;
  border-radius: 999px;
  background: rgba(15, 45, 31, 0.06);
  color: #0f2d1f;
  font-size: 0.9rem;
}

.reactions {
  display: flex;
  gap: 12px;
  margin-top: 12px;
}

.detail-actions {
  margin-bottom: 12px;
}

.comment-list {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid rgba(15, 45, 31, 0.08);
  color: #4d6359;
}

.comment-list .more {
  color: #60756a;
  margin-top: 8px;
}

.empty {
  color: #60756a;
}

.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(4, 28, 16, 0.45);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 18px;
  z-index: 30;
}

.modal {
  background: #ffffff;
  border-radius: 20px;
  padding: 22px;
  max-width: 720px;
  width: 100%;
  box-shadow: 0 18px 42px rgba(16, 68, 50, 0.15);
}

.modal-header,
.detail-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 12px;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 6px;
}

.file-picker input {
  margin-top: 8px;
}

.preview-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 12px;
}

.media-preview {
  border: 1px solid rgba(15, 45, 31, 0.08);
  border-radius: 14px;
  padding: 10px;
  background: rgba(249, 252, 250, 0.85);
}

.media-preview img,
.media-preview video {
  width: 100%;
  border-radius: 10px;
  max-height: 180px;
  object-fit: cover;
  display: block;
}

.media-preview p {
  margin: 8px 0 0;
  color: #4c675b;
  font-size: 0.9rem;
}
</style>
