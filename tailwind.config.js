/** @type {import('tailwindcss').Config} */
module.exports = {
 content: [
    "./app/templates/*.html",
    "./app/static/**/*.js",
    "./app/templates/**/*.html", // Your Flask template files
    "./main.py",  // Any other files that might contain Tailwind classes
  ],  theme: {
    extend: {},
  },
  plugins: [],
}

// app/templates/vms/list_running_vms.html