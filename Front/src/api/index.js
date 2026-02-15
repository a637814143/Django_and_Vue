import http, { API_BASE_URL } from "./http";

const unwrap = (promise) => promise.then((res) => res.data);

export const accountApi = {
  register: (payload) => unwrap(http.post("accounts/register/", payload)),
  login: (payload) => unwrap(http.post("accounts/login/", payload)),
  profile: () => unwrap(http.get("accounts/profile/")),
  updateProfile: (payload) => unwrap(http.put("accounts/profile/", payload)),
  logout: () => unwrap(http.post("accounts/logout/")),
  users: (params = {}) => unwrap(http.get("accounts/users/", { params })),
};

export const catalogApi = {
  categories: () => unwrap(http.get("catalog/categories/")),
  products: (params = {}) => unwrap(http.get("catalog/products/", { params })),
  createProduct: (payload) => unwrap(http.post("catalog/products/", payload)),
  createCategory: (payload) => unwrap(http.post("catalog/categories/", payload)),
  updateProduct: (id, payload) => unwrap(http.put(`catalog/products/${id}/`, payload)),
};

export const inventoryApi = {
  logs: () => unwrap(http.get("catalog/inventory/")),
  adjust: (payload) => unwrap(http.post("catalog/inventory/", payload)),
};

export const orderApi = {
  list: (params = {}) => unwrap(http.get("commerce/orders/", { params })),
  create: (payload) => unwrap(http.post("commerce/orders/", payload)),
  updateStatus: (id, payload) => unwrap(http.post(`commerce/orders/${id}/update_status/`, payload)),
};

export const walletApi = {
  overview: () => unwrap(http.get("wallet/")),
  pay: (payload) => unwrap(http.post("wallet/pay/", payload)),
  refund: (payload) => unwrap(http.post("wallet/refund/", payload)),
  config: () => unwrap(http.get("wallet/config/")),
  updateConfig: (payload) => unwrap(http.put("wallet/config/", payload)),
  recharge: (payload) => unwrap(http.post("wallet/recharge/", payload)),
  generateVouchers: (payload) => unwrap(http.post("wallet/vouchers/generate/", payload)),
  redeemVoucher: (payload) => unwrap(http.post("wallet/vouchers/redeem/", payload)),
  vouchers: () => unwrap(http.get("wallet/vouchers/")),
};

export const addressApi = {
  list: () => unwrap(http.get("accounts/addresses/")),
  create: (payload) => unwrap(http.post("accounts/addresses/", payload)),
  update: (id, payload) => unwrap(http.put(`accounts/addresses/${id}/`, payload)),
  remove: (id) => unwrap(http.delete(`accounts/addresses/${id}/`)),
};

export const storefrontApi = {
  stores: (params = {}) => unwrap(http.get("storefront/stores/", { params })),
  storeDetail: (id) => unwrap(http.get(`storefront/stores/${id}/`)),
  storeProducts: (id, params = {}) => unwrap(http.get(`storefront/stores/${id}/products/`, { params })),
  categories: (params = {}) => unwrap(http.get("storefront/categories/", { params })),
  products: (params = {}) => unwrap(http.get("storefront/products/", { params })),
};

export const customizationApi = {
  list: () => unwrap(http.get("customization/wishes/")),
  create: (payload) => unwrap(http.post("customization/wishes/", payload)),
  addTimeline: (id, payload) => unwrap(http.post(`customization/wishes/${id}/timeline/`, payload)),
  assign: (id) => unwrap(http.post(`customization/wishes/${id}/assign/`)),
};

export const analyticsApi = {
  overview: () => unwrap(http.get("analytics/overview/")),
  metrics: () => unwrap(http.get("analytics/metrics/")),
};

export const communityApi = {
  posts: () => unwrap(http.get("community/posts/")),
  createPost: (payload) => {
    const sendFormData = (formData) =>
      unwrap(
        http.post("community/posts/", formData, {
          headers: { "Content-Type": "multipart/form-data" },
        }),
      );

    if (payload instanceof FormData) {
      return sendFormData(payload);
    }

    const mediaFiles = payload?.media_files || payload?.attachments || [];
    const hasFiles = Array.isArray(mediaFiles) && mediaFiles.length > 0;

    if (hasFiles) {
      const formData = new FormData();
      formData.append("title", payload.title || "");
      formData.append("content", payload.content || "");
      formData.append("visibility", payload.visibility || "PUBLIC");
      mediaFiles.forEach((file) => {
        if (file) {
          formData.append("media_files", file);
        }
      });
      return sendFormData(formData);
    }

    return unwrap(http.post("community/posts/", payload));
  },
  comment: (id, payload) => unwrap(http.post(`community/posts/${id}/comment/`, payload)),
  react: (id, payload) => unwrap(http.post(`community/posts/${id}/react/`, payload)),
};

export const focusApi = {
  videos: (params = {}) => unwrap(http.get("focus/videos/", { params })),
  upload: ({ title, description, video_file, cover_file }) => {
    const formData = new FormData();
    formData.append("title", title);
    if (description) {
      formData.append("description", description);
    }
    formData.append("video_file", video_file);
    if (cover_file) {
      formData.append("cover_file", cover_file);
    }
    return unwrap(
      http.post("focus/videos/", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      }),
    );
  },
  remove: (id) => unwrap(http.delete(`focus/videos/${id}/`)),
  like: (id) => unwrap(http.post(`focus/videos/${id}/like/`)),
  comments: (id) => unwrap(http.get(`focus/videos/${id}/comments/`)),
  addComment: (id, payload) => unwrap(http.post(`focus/videos/${id}/comments/`, payload)),
  deactivate: (id) => unwrap(http.post(`focus/videos/${id}/deactivate/`)),
  restore: (id) => unwrap(http.post(`focus/videos/${id}/restore/`)),
};

export const adminApi = {
  runCommand: (payload) => unwrap(http.post("admin/terminal/", payload)),
  history: () => unwrap(http.get("admin/terminal/")),
};

export { API_BASE_URL };
