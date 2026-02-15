<script setup>
import { onMounted, ref } from "vue";
import GlassCard from "../components/ui/GlassCard.vue";
import { focusApi } from "../api";

const videos = ref([]);
const loading = ref(true);
const error = ref("");

const loadVideos = async () => {
  loading.value = true;
  try {
    const data = await focusApi.videos({ page_size: 50, with_comments: 0 });
    videos.value = data.results ?? data;
  } catch (err) {
    error.value = err?.response?.data?.detail || "加载灵感视频失败";
  } finally {
    loading.value = false;
  }
};

const takeDown = async (video) => {
  try {
    await focusApi.deactivate(video.id);
    video.status = "DISABLED";
  } catch (err) {
    // ignore
  }
};

const restoreVideo = async (video) => {
  try {
    await focusApi.restore(video.id);
    video.status = "ACTIVE";
  } catch (err) {
    // ignore
  }
};

onMounted(loadVideos);
</script>

<template>
  <GlassCard title="好物聚焦管理" subtitle="管理员可预览/下载/下架">
    <p v-if="error" class="error">{{ error }}</p>
    <div v-if="loading" class="loading">加载中...</div>
    <table v-else>
      <thead>
        <tr>
          <th>ID</th>
          <th>预览</th>
          <th>标题</th>
          <th>发布者</th>
          <th>点赞</th>
          <th>评论</th>
          <th>状态</th>
          <th>操作</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="video in videos" :key="video.id">
          <td>{{ video.id }}</td>
          <td>
            <video :src="video.video_url" controls preload="metadata"></video>
          </td>
          <td>{{ video.title }}</td>
          <td>{{ video.creator }}</td>
          <td>{{ video.like_count }}</td>
          <td>{{ video.comment_count }}</td>
          <td>
            <span :class="['status', video.status === 'ACTIVE' ? 'status--active' : 'status--down']">
              {{ video.status === "ACTIVE" ? "在架" : "已下架" }}
            </span>
          </td>
          <td class="actions">
            <a class="btn-outline" :href="video.video_url" download>下载</a>
            <button
              v-if="video.status === 'ACTIVE'"
              class="btn-danger"
              type="button"
              @click="takeDown(video)"
            >
              下架
            </button>
            <button
              v-else
              class="btn-primary"
              type="button"
              @click="restoreVideo(video)"
            >
              恢复
            </button>
          </td>
        </tr>
        <tr v-if="!videos.length">
          <td colspan="8" class="empty">暂无视频</td>
        </tr>
      </tbody>
    </table>
  </GlassCard>
</template>

<style scoped>
table {
  width: 100%;
  border-collapse: collapse;
}

th,
td {
  padding: 12px;
  border-bottom: 1px solid rgba(15, 45, 31, 0.12);
  text-align: left;
  vertical-align: top;
}

video {
  width: 160px;
  max-height: 120px;
  border-radius: 10px;
}

.actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.status {
  padding: 4px 10px;
  border-radius: 999px;
}

.status--active {
  background: rgba(111, 207, 151, 0.2);
  color: #0f3d2e;
}

.status--down {
  background: rgba(255, 99, 132, 0.2);
  color: #8c182b;
}

.btn-danger {
  border: 1px solid rgba(255, 99, 132, 0.8);
  background: rgba(255, 99, 132, 0.1);
  border-radius: 999px;
  padding: 8px 16px;
  cursor: pointer;
}

.btn-primary {
  border: 1px solid rgba(15, 45, 31, 0.3);
  background: rgba(15, 45, 31, 0.08);
  border-radius: 999px;
  padding: 8px 16px;
}

.btn-outline {
  border: 1px solid rgba(15, 45, 31, 0.3);
  border-radius: 999px;
  padding: 8px 16px;
  text-decoration: none;
  color: inherit;
}

.loading,
.empty {
  text-align: center;
  color: #6b7f73;
}

.error {
  color: #b42318;
}
</style>
