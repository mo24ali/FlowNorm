/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "#08090a",
        foreground: "#f9fafb",
        primary: "#3b82f6",
        secondary: "#1f2937",
        muted: "#64748b",
        border: "#2d3748",
        accent: "#d946ef"
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      }
    },
  },
  plugins: [],
}
