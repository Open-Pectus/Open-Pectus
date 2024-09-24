import { defineConfig } from '@hey-api/openapi-ts';

export default defineConfig({
  input: './openapi.json',
  output: './src/app/api',
  client: 'angular',
  services: {
    asClass: true,
  },
  types: {
    enums: 'typescript'
  },
  schemas: false,
});
