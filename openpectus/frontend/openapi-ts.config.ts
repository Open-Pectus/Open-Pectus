import { defineConfig } from '@hey-api/openapi-ts';

export default defineConfig({
  input: './openapi.json',
  output: './src/app/api',
  client: 'legacy/angular',
  services: {
    asClass: true,
  },
  schemas: false,
});
