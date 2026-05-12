import { fileURLToPath, URL } from 'node:url';
import { defineConfig, loadEnv } from 'vite';
import tailwindcss from '@tailwindcss/vite';
import vue from '@vitejs/plugin-vue';

export default defineConfig(async ({ mode }) => {
  const env = loadEnv(mode, process.cwd());

  const plugins = [tailwindcss(), vue()];

  if (mode === 'development') {
    const vueDevTools = await import('vite-plugin-vue-devtools').then(m => m.default);
    plugins.push(vueDevTools());
  }

  return {
    plugins: plugins,
    resolve: {
      alias: {
        '@': fileURLToPath(new URL('./src', import.meta.url)),
      },
    },
    server: {
      allowedHosts: [
        "test.ability.new",
      ],
      proxy: {
        '/api': {
          target: env.VITE_API_PROXY,
          changeOrigin: true,
          secure: false,
        },
      },
    },
  };
});
