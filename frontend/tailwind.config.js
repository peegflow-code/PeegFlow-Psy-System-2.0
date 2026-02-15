/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {
      colors: {
        lilac: {
          50: "#faf7ff",
          100: "#f3ecff",
          200: "#e6d9ff",
          300: "#d1b8ff",
          400: "#b58cff",
          500: "#9d5cff",
          600: "#8b3dff",
          700: "#7429e6",
          800: "#5e22b8",
          900: "#4b1c91",
        },
      },
      boxShadow: {
        soft: "0 10px 30px rgba(0,0,0,.08)",
      },
    },
  },
  plugins: [],
};