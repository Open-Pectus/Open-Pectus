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
        'vscode-backgroundgrey': '#F3F3F3',
        'vscode-backgroundgrey-hover': '#DBDBDB',
        'vscode-backgrounddark': '#2C2C2C',
      },
    },
  },
  plugins: [],
}
