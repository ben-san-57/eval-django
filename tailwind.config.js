/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./cocktails/**/*.{html,js,py}",
    "./templates/**/*.{html,js}",
    "./static/js/**/*.js",
  ],
  theme: {
    extend: {},
  },
  plugins: [
    require('daisyui'),
  ],
  daisyui: {
    themes: ["light", "dark"],
  },
}
