<script setup>
import { onMounted, ref } from "vue";
import { focusApi } from "../api";

const videos = ref([]);
const loading = ref(true);
const error = ref("");

const headers = [
  { text: 'ID', value: 'id' },
  { text: '预览', value: 'video_url' },
  { text: '标题', value: 'title' },
  { text: '发布者', value: 'creator' },
  { text: '点赞', value: 'like_count' },
  { text: '评论', value: 'comment_count' },
  { text: '状态', value: 'status' },
  { text: '操作', value: 'actions', sortable: false },
];

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
  <v-container fluid>
    <v-card>
      <v-card-title>好物聚焦管理</v-card-title>
      <v-card-subtitle>管理员可预览/下载/下架</v-card-subtitle>
      <v-card-text>
        <v-alert v-if="error" type="error">{{ error }}</v-alert>
        <v-data-table
          :headers="headers"
          :items="videos"
          :loading="loading"
          class="elevation-1"
        >
          <template v-slot:item.video_url="{ item }">
            <video :src="item.video_url" controls preload="metadata" width="160"></video>
          </template>
          <template v-slot:item.status="{ item }">
            <v-chip :color="item.status === 'ACTIVE' ? 'success' : 'error'">
              {{ item.status === "ACTIVE" ? "在架" : "已下架" }}
            </v-chip>
          </template>
          <template v-slot:item.actions="{ item }">
            <v-btn :href="item.video_url" download small class="mr-2">下载</v-btn>
            <v-btn
              v-if="item.status === 'ACTIVE'"
              color="error"
              small
              @click="takeDown(item)"
            >
              下架
            </v-btn>
            <v-btn
              v-else
              color="primary"
              small
              @click="restoreVideo(item)"
            >
              恢复
            </v-btn>
          </template>
        </v-data-table>
      </v-card-text>
    </v-card>
  </v-container>
</template>
