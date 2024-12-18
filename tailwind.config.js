/** @type {import('tailwindcss').Config} */
module.exports = {
 content: [
    "./app/templates/*.html",
    "./app/static/**/*.js",
    "./app/templates/**/*.html", // Your Flask template files
    "./main.py",  // Any other files that might contain Tailwind classes
  ],  theme: {
    extend: {
        colors: {
            'primary-green': {
                DEFAULT: '#B8D900',
                'light': '#C4E533',
                'dark':'#A5C200'
            }
        }
    },
  },
  plugins: [],
}

// app/templates/vms/list_running_vms.html