/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{html,ts}",
  ],
  theme: {
    extend: {
      colors: {
        'vscode-darkblue': '#04395E',
        'vscode-mediumblue': '#007ACC',
        'vscode-background-grey': '#F3F3F3',
        'vscode-background-grey-hover': '#DBDBDB',
        'vscode-background-dark': '#2C2C2C',
      },
    },
  },
  plugins: [],
}

