/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        'carmine' : '#921919',
        'rose-taupe': '#8C5C5C',
        'tea-rose': '#EDBBBB',
        'nyanza': '#CEF2D6',
        'spring-green': '#59EF7A',
        'malachite': '#43DF65',
        'dark-spring-green': '#396B38',
        'pakistan-green': '#0F480E',
        'dark-green': '#0A2610'
      },
    },
  },
  darkMode: "class",
  plugins: [],
}

