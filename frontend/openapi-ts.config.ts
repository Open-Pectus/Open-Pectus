import { defaultPlugins, defineConfig } from '@hey-api/openapi-ts';

export default defineConfig({
  input: './openapi.json',
  output: './src/app/api',
  plugins: [
    ...defaultPlugins,
    {
      asClass: true,
      classNameBuilder: '{{name}}Service',
      name: '@hey-api/sdk',
    },
    'legacy/angular',
  ],
});
