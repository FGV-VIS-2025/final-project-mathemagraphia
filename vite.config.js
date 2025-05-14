import { defineConfig } from 'vite'
import { svelte } from '@sveltejs/vite-plugin-svelte'

// Substitua 'nome-do-repo' pelo NOME EXATO do seu repositório
export default defineConfig({
  base: '/final-project-mathemagraphia/',
  plugins: [svelte()],
  server: {
    hmr: false
  }
})