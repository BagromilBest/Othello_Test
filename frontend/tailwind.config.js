/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#1976d2',
          dark: '#115293',
          light: '#4791db',
        },
        surface: {
          DEFAULT: '#1e1e1e',
          light: '#2d2d2d',
          lighter: '#3d3d3d',
        },
      },
    },
  },
  plugins: [],
}