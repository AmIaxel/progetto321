/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./templates/**/*.html", // Include i file HTML di Flask
    "./static/**/*.css",
    "./**/*.html",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
};
