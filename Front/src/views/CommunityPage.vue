<script setup>
import { computed, onMounted, reactive, ref } from "vue";
import { communityApi, API_BASE_URL } from "../api";

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
  const flag = (input?.media_type || "").toString().toUpperCase();
  if (flag === "VIDEO") return "video";
  if (flag === "IMAGE") return "image";
  if (input?.type?.includes("video")) return "video";
  const url = typeof input === "string" ? input : input?.url || input?.path || input?.file || "";
  const cleanUrl = url.split("?")[0];
  const ext = cleanUrl.split(".").pop()?.toLowerCase();
  const videoExts = ["mp4", "mov", "webm", "mkv", "ogg"];
  return videoExts.includes(ext) ? "video" : "image";
};

const buildUrl = (url) => {
  if (!url) return "";
  if (url.startsWith("http")) return url;
  if (url.startsWith("/")) {
    try {
      const base = API_BASE_URL.replace(/\/api\/?$/, "/");
      return new URL(url, base).toString();
    } catch (e) {
      return url;
    }
  }
  return url;
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
          url: buildUrl(item),
          type: guessMediaType(item),
          name: item.split("/").pop() || `附件${index + 1}`,
        };
      }
      const url = buildUrl(item.url || item.path || item.file || item.src);
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
  <v-container fluid>
    <v-row>
      <v-col cols="12">
        <v-card>
          <v-card-title>灵感发布</v-card-title>
          <v-card-subtitle>集中入口</v-card-subtitle>
          <v-card-text>整理好想法再发布，支持上传图片/视频附件。</v-card-text>
          <v-card-actions>
            <v-btn color="primary" @click="openComposer">+ 发布灵感</v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>
    <v-row>
      <v-col cols="12">
        <v-card>
          <v-card-title>互动社区</v-card-title>
          <v-card-text>
            <v-alert v-if="loadError" type="error">{{ loadError }}</v-alert>
            <p v-else-if="!posts.length && !loading">暂时没有帖子</p>
            <v-progress-circular v-else-if="loading" indeterminate></v-progress-circular>
            <v-row v-else>
              <v-col v-for="post in posts" :key="post.id" cols="12" md="6" lg="4">
                <v-card @click="openDetail(post)">
                  <v-card-title>{{ post.title }}</v-card-title>
                  <v-card-subtitle>{{ post.visibility }} by {{ post.author || "匿名" }}</v-card-subtitle>
                  <v-card-text>
                    <div class="line-clamp">{{ post.content }}</div>
                    <v-row v-if="mediaFromPost(post).length" class="mt-2" dense>
                      <v-col
                        v-for="media in mediaFromPost(post).slice(0, 2)"
                        :key="media.url"
                        cols="6"
                      >
                        <v-img
                          v-if="media.type === 'image'"
                          :src="media.url"
                          height="140"
                          cover
                          class="rounded"
                        />
                        <video
                          v-else
                          :src="media.url"
                          controls
                          height="140"
                          style="width: 100%; border-radius: 8px; object-fit: cover"
                        ></video>
                      </v-col>
                    </v-row>
                  </v-card-text>
                  <v-card-actions>
                    <v-btn color="primary" variant="tonal" size="small" @click.stop="react(post, 'LIKE')">
                      <span class="btn-icon">❤️</span>
                      <span class="btn-text">点赞 {{ post.reactions?.length ?? 0 }}</span>
                    </v-btn>
                    <v-btn color="secondary" variant="tonal" size="small" @click.stop="comment(post)">
                      <span class="btn-icon">💬</span>
                      <span class="btn-text">评论 {{ post.comments?.length ?? 0 }}</span>
                    </v-btn>
                  </v-card-actions>
                </v-card>
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
    <v-dialog v-model="composerOpen" max-width="720px">
      <v-card>
        <v-card-title>发布灵感</v-card-title>
        <v-card-subtitle>和社区分享你的想法</v-card-subtitle>
        <v-card-text>
          <v-form @submit.prevent="publish">
            <v-text-field v-model="composerForm.title" label="标题" required placeholder="一句话概括灵感"></v-text-field>
            <v-textarea v-model="composerForm.content" label="内容" rows="4" required placeholder="详细描述想法、需求或进展"></v-textarea>
            <v-select v-model="composerForm.visibility" :items="['PUBLIC', 'MERCHANT', 'INTERNAL']" label="可见范围"></v-select>
            <v-file-input multiple label="图片 / 视频" accept="image/*,video/*" @change="onFilesSelected"></v-file-input>
            <v-row v-if="mediaPreviews.length">
              <v-col v-for="media in mediaPreviews" :key="media.url" cols="6" sm="4">
                <v-img v-if="media.type.startsWith('image')" :src="media.url" height="150"></v-img>
                <video v-else :src="media.url" controls height="150"></video>
                <p>{{ media.name }}</p>
              </v-col>
            </v-row>
            <v-alert v-if="composerError" type="error">{{ composerError }}</v-alert>
          </v-form>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn text @click="closeComposer">取消</v-btn>
          <v-btn color="primary" @click="publish" :loading="publishing">{{ publishing ? "发布中..." : "发布" }}</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
    <v-dialog v-model="detailOpen" class="detail-dialog" max-width="1024px" width="90vw">
      <v-card v-if="activePost">
        <v-card-title>{{ activePost.title }}</v-card-title>
        <v-card-subtitle>{{ activePost.visibility }} by {{ activePost.author || "匿名" }}</v-card-subtitle>
        <v-card-text>
          <p>{{ activePost.content }}</p>
          <v-row v-if="activeMedia.length" class="mt-2" dense>
            <v-col v-for="media in activeMedia" :key="media.url" cols="12" sm="6" md="4">
              <v-img
                v-if="media.type === 'image'"
                :src="media.url"
                cover
                height="220"
                class="rounded mb-2"
              />
              <video
                v-else
                :src="media.url"
                controls
                class="w-100 rounded mb-2"
                style="max-height: 260px; object-fit: cover"
              ></video>
              <p class="text-caption mb-0">{{ media.name }}</p>
            </v-col>
          </v-row>
          <v-alert v-else type="info" dense>该帖子没有附件</v-alert>
        </v-card-text>
        <v-card-actions>
          <v-btn color="primary" variant="tonal" @click="react(activePost, 'LIKE')">
            <span class="btn-icon">❤️</span>
            <span class="btn-text">点赞 {{ activePost.reactions?.length ?? 0 }}</span>
          </v-btn>
          <v-btn color="secondary" variant="tonal" @click="comment(activePost)">
            <span class="btn-icon">💬</span>
            <span class="btn-text">评论 {{ activePost.comments?.length ?? 0 }}</span>
          </v-btn>
        </v-card-actions>
        <v-list>
          <v-list-item v-for="comment in activePost.comments || []" :key="comment.id">
            <v-list-item-content>
              <v-list-item-title>{{ comment.author }}</v-list-item-title>
              <v-list-item-subtitle>{{ comment.message }}</v-list-item-subtitle>
            </v-list-item-content>
          </v-list-item>
        </v-list>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<style scoped>
.line-clamp {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.detail-dialog :deep(.v-card) {
  max-width: 100%;
}

.btn-icon {
  display: inline-block;
  margin-right: 6px;
}

.btn-text {
  display: inline-block;
}
</style>
