/** @type {import('tailwindcss').Config} */

import plugin from 'tailwindcss/plugin';

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
      textShadow: {
        sm: '0 1px 2px var(--tw-shadow-color)',
        DEFAULT: '0 2px 4px var(--tw-shadow-color)',
        lg: '0 8px 16px var(--tw-shadow-color)',
      },
    },
  },
  darkMode: "class",
  plugins: [
    plugin(function ({ matchUtilities, theme }) {
      matchUtilities(
        {
          'text-shadow': (value) => ({
            textShadow: value,
          }),
        },
        { values: theme('textShadow') }
      )
    }),
  ],
}

