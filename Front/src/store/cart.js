import { defineStore } from 'pinia'

export const useCartStore = defineStore('cart', {
  state: () => ({
    items: [],
  }),
  getters: {
    total() {
      return this.items.reduce((acc, item) => acc + item.price * item.qty, 0)
    }
  },
  actions: {
    add(item) {
      const existing = this.items.find(i => i.id === item.id)
      if (existing) {
        existing.qty++
      } else {
        this.items.push({ ...item, qty: 1 })
      }
    },
    remove(id) {
      this.items = this.items.filter(i => i.id !== id)
    },
    setQty(id, qty) {
      const item = this.items.find(i => i.id === id)
      if (item) {
        if (qty <= 0) {
          this.remove(id)
        } else {
          item.qty = qty
        }
      }
    },
    clear() {
      this.items = []
    }
  },
})
