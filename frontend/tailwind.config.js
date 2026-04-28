/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{vue,js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#eef7f5',
          100: '#d7ebe6',
          200: '#afd8cd',
          300: '#83c1b0',
          400: '#4c9f89',
          500: '#247d75',
          600: '#1f6f68',
          700: '#1d5954',
          800: '#1c4844',
          900: '#193d3a',
        },
        sand: {
          50: '#faf8f5',
          100: '#f4efe8',
          200: '#e8dfd2',
          300: '#d9c9b3',
          400: '#c3a886',
          500: '#b48f68',
          600: '#a27a58',
          700: '#87634b',
          800: '#6f523f',
          900: '#5c4435',
        },
      },
      boxShadow: {
        panel: '0 18px 42px rgba(120, 111, 103, 0.14)',
        soft: '0 18px 40px rgba(43, 45, 42, 0.06)',
      },
      borderRadius: {
        panel: '1.5rem',
      },
      fontFamily: {
        sans: ['Noto Sans SC', 'Microsoft YaHei', 'sans-serif'],
        display: ['Outfit', 'Noto Sans SC', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
