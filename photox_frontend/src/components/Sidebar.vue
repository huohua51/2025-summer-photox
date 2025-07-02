<template>
  <div class="sidebar">
    <div 
      v-for="category in categories" 
      :key="category"
      :class="{ 'active': selectedCategory === category }"
      @click="$emit('select-category', category)"
    >
      {{ category }}
    </div>
  </div>
</template>

<script setup>
defineProps({
  categories: Array,
  selectedCategory: String
})
defineEmits(['select-category'])
</script>

<style scoped>
.sidebar {
  width: 100%;
  padding: 0;
}

.sidebar div {
  padding: 10px 20px;
  margin: 5px 0;
  cursor: pointer;
  border-radius: 6px;
  color: var(--text-color);
  transition: all 0.3s ease;
}

.sidebar div:hover {
  background: var(--primary-color);
  color: white;
}

.sidebar div.active {
  background: var(--primary-color);
  color: white;
  font-weight: 500;
}
</style>