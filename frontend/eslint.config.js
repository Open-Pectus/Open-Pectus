// @ts-check
// const eslint = import("@eslint/js");
import js from '@eslint/js';
import * as tseslint from 'typescript-eslint'
import * as angular from 'angular-eslint'
// const tseslint = import("typescript-eslint");
// const angular = import("angular-eslint");

export default tseslint.config(
    {
      files: ["**/*.ts"],
      ignores: [
        "src/app/api/**",
      ],
      extends: [
        js.configs.recommended,
        ...tseslint.configs.recommended,
        ...tseslint.configs.stylistic,
        ...angular.configs.tsRecommended,
      ],
      processor: angular.processInlineTemplates,
      rules: {
        "@angular-eslint/directive-selector": [
          "error",
          {
            type: "attribute",
            prefix: "app",
            style: "camelCase",
          },
        ],
        "@angular-eslint/component-selector": [
          "error",
          {
            type: "element",
            prefix: "app",
            style: "kebab-case",
          },
        ],
        "@typescript-eslint/no-unused-vars": [
          "error",
          {
            "argsIgnorePattern": "^_",
            "destructuredArrayIgnorePattern": "^_",
          },
        ],
      },
    },
    {
      files: ["**/*.html"],
      extends: [
        ...angular.configs.templateRecommended,
        ...angular.configs.templateAccessibility,
      ],
      rules: {
        "@angular-eslint/template/click-events-have-key-events": "off",
        "@angular-eslint/template/interactive-supports-focus": "off",
        "@angular-eslint/template/elements-content": "off",
      },
    },
);
