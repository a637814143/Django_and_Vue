import { defineStore } from "pinia";

const STORAGE_KEY = "cartItems";

const loadInitial = () => {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch (e) {
    return [];
  }
};

const persist = (items) => {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(items));
};

export const useCartStore = defineStore("cart", {
  state: () => ({
    items: loadInitial(),
  }),
  getters: {
    total: (state) =>
      state.items.reduce((sum, item) => sum + Number(item.price || 0) * Number(item.qty || 1), 0),
    count: (state) => state.items.reduce((sum, item) => sum + Number(item.qty || 1), 0),
  },
  actions: {
    add(item) {
      const existing = this.items.find((i) => i.id === item.id);
      if (existing) {
        existing.qty += 1;
      } else {
        this.items.push({
          id: item.id,
          title: item.title,
          price: Number(item.price || 0),
          hero_image: item.hero_image || "",
          store_name: item.store?.name || "",
          qty: 1,
        });
      }
      persist(this.items);
    },
    remove(id) {
      this.items = this.items.filter((i) => i.id !== id);
      persist(this.items);
    },
    setQty(id, qty) {
      const target = this.items.find((i) => i.id === id);
      if (!target) return;
      target.qty = Math.max(1, qty);
      persist(this.items);
    },
    clear() {
      this.items = [];
      persist(this.items);
    },
  },
});
