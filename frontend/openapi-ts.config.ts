import { defaultPlugins, defineConfig } from '@hey-api/openapi-ts';

export default defineConfig({
  input: './openapi.json',
  output: './src/app/api',
  client: 'legacy/angular',
  plugins: [
    ...defaultPlugins,
    {
      asClass: true,
      name: '@hey-api/sdk',
    },
  ],
});
