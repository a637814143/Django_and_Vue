<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, reactive, ref, watch } from "vue";
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
});

</script>

<template>
    <v-container fluid>
        <v-row>
            <v-col>
                 <v-alert v-if="error" type="error">{{ error }}</v-alert>
                <v-progress-circular v-if="loading" indeterminate></v-progress-circular>
                <v-card v-else>
                    <v-row>
                        <v-col cols="12" md="8">
                            <div class="hero-video-frame">
                                <video
                                  v-if="heroVideo"
                                  :key="heroVideo.id"
                                  :src="heroVideo.video_url"
                                  autoplay
                                  muted
                                  loop
                                  playsinline
                                  controls
                                  :poster="heroVideo.cover_url"
                                  class="hero-video"
                                ></video>
                                <div v-else class="d-flex align-center justify-center hero-video">
                                    <p>暂无视频，点击右上角「+」开启第一条灵感</p>
                                </div>
                            </div>
                             <div class="d-flex justify-center ga-2 mt-2">
                                <v-btn size="small" variant="tonal" prepend-icon="mdi-arrow-up" @click="goPrev" :disabled="!canNavigate">上一条</v-btn>
                                <v-btn size="small" variant="tonal" prepend-icon="mdi-arrow-down" @click="goNext" :disabled="!canNavigate">下一条</v-btn>
                                <v-btn size="small" variant="text" color="error" prepend-icon="mdi-delete" @click="deleteHero" :disabled="!heroVideo || !canDeleteHero || deletingHero">删除</v-btn>
                                <v-btn v-if="canUpload" size="small" variant="tonal" @click="toggleUploadPanel" :prepend-icon="showUploadPanel ? 'mdi-close' : 'mdi-plus'">
                                  {{ showUploadPanel ? '收起上传' : '上传视频' }}
                                </v-btn>
                            </div>
                            <v-dialog v-model="showUploadPanel" max-width="600">
                               <v-card>
                                   <v-card-title>上传视频</v-card-title>
                                   <v-card-text>
                                       <v-form @submit.prevent="submitUpload">
                                           <v-text-field v-model="uploadForm.title" label="标题" placeholder="青柠灵感套装"></v-text-field>
                                           <v-textarea v-model="uploadForm.description" label="描述" rows="2" placeholder="分享创作故事"></v-textarea>
                                           <v-file-input accept="video/*" label="上传视频" @change="handleFileChange"></v-file-input>
                                           <v-alert v-if="uploadError" type="error">{{ uploadError }}</v-alert>
                                       </v-form>
                                   </v-card-text>
                                   <v-card-actions>
                                       <v-spacer></v-spacer>
                                       <v-btn text @click="cancelUpload">取消</v-btn>
                                       <v-btn color="primary" @click="submitUpload" :loading="uploading">{{ uploading ? "上传中..." : "发布" }}</v-btn>
                                   </v-card-actions>
                               </v-card>
                            </v-dialog>
                        </v-col>
                        <v-col cols="12" md="4">
                            <v-card v-if="heroVideo">
                                <v-card-title>{{ heroVideo.title }}</v-card-title>
                                <v-card-subtitle>{{ heroVideo.creator }}</v-card-subtitle>
                                <v-card-text>
                                    <p>{{ heroVideo.description }}</p>
                                </v-card-text>
                                <v-card-actions>
                                    <v-btn
                                      size="small"
                                      variant="tonal"
                                      color="primary"
                                      @click="toggleLike(heroVideo)"
                                      prepend-icon="mdi-heart"
                                    >
                                        点赞 {{ heroVideo.like_count }}
                                    </v-btn>
                                    <v-btn
                                      size="small"
                                      variant="tonal"
                                      color="primary"
                                      @click="focusCommentInput"
                                      prepend-icon="mdi-comment"
                                    >
                                        评论 {{ heroVideo.comment_count }}
                                    </v-btn>
                                    <v-btn size="small" variant="text" prepend-icon="mdi-download" :href="heroVideo.video_url" download>下载</v-btn>
                                </v-card-actions>
                                <v-divider></v-divider>
                                <v-card-text>
                                    <h3>评论区</h3>
                                     <v-list>
                                        <v-list-item v-if="commentsPanel.loading">加载评论中...</v-list-item>
                                        <v-list-item v-for="comment in commentsPanel.items" :key="comment.id">
                                            <v-list-item-content>
                                                <v-list-item-title>{{ comment.author }}</v-list-item-title>
                                                <v-list-item-subtitle>{{ comment.content }}</v-list-item-subtitle>
                                            </v-list-item-content>
                                        </v-list-item>
                                        <v-list-item v-if="!commentsPanel.items.length && !commentsPanel.loading">暂无评论</v-list-item>
                                    </v-list>
                                </v-card-text>
                                <v-card-actions>
                                    <v-text-field ref="commentInputRef" v-model="commentsPanel.newComment" placeholder="写下你的想法" @keyup.enter="submitComment"></v-text-field>
                                    <v-btn color="primary" @click="submitComment">发布</v-btn>
                                </v-card-actions>
                            </v-card>
                             <p v-else>暂无视频，赶紧发布第一条灵感吧</p>
                        </v-col>
                    </v-row>
                     <v-alert v-if="heroActionError" type="error" class="mt-4">{{ heroActionError }}</v-alert>
                </v-card>
            </v-col>
        </v-row>
    </v-container>
</template>

<style scoped>
.hero-video-frame {
  width: 100%;
  max-width: 100%;
  aspect-ratio: 16 / 9;
  border-radius: 12px;
  overflow: hidden;
  background: #000;
}
.hero-video {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
</style>
