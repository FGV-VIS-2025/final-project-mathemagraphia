import { vitePreprocess } from '@sveltejs/vite-plugin-svelte';

export default {
  compilerOptions: {
    // 👇 habilita API clássica (Svelte 4)
    compatibility: {
      componentApi: 4
    }
  },
  preprocess: vitePreprocess()
};