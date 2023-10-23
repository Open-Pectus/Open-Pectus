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
        'vscode-green': '#1D9271',
      },
      keyframes: {
        'ping-pong-x': {
          '0%': {transform: 'translateX(0)', left: '0'},
          '100%': {transform: 'translateX(-100%)', left: '100%'},
        },
      },
      animation: {
        'ping-pong-x': 'ping-pong-x 1.4s linear alternate infinite',
      },
    },
  },
  plugins: [],
}

