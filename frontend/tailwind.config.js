
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Brand colors inspired by the Speak Insights logo
        'si-primary': '#1D5FD6',       // chat bubble blue
        'si-primary-soft': '#E0ECFF',
        'si-primary-strong': '#123769', // deep navy
        // Adaptive semantic tokens driven by CSS variables (see index.css)
        'si-bg': 'rgb(var(--si-bg) / <alpha-value>)',
        'si-surface': 'rgb(var(--si-surface) / <alpha-value>)',
        'si-border': 'rgb(var(--si-border) / <alpha-value>)',
        'si-text': 'rgb(var(--si-text) / <alpha-value>)',
        'si-muted': 'rgb(var(--si-muted) / <alpha-value>)',
        'si-elevated': 'rgb(var(--si-elevated) / <alpha-value>)',
      },
      boxShadow: {
        'si-soft': '0 18px 45px rgba(15, 23, 42, 0.18)',
      },
      borderRadius: {
        '2xl': '1.5rem',
      },
    },
  },
  plugins: [],
}
