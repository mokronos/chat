/** @type {import('tailwindcss').Config} */
const defaultTheme = require('tailwindcss/defaultTheme')

module.exports = {
    content: [
        "./templates/**/*.html",
        // "./static/src/**/*.js",
    ],
    theme: {
        extend: {
            colors: {
                'c1': '#2A2B2A',
                'c2': '#374151',
                'c3': '#E04700',

            },
            fontFamily: {
                'sans': ['Inter var', ...defaultTheme.fontFamily.sans],
            },
            keyframes: {
                fadeOut: {
                    '0%': { opacity: '1' },
                    '99%': { opacity: '0', visibility: 'visible' },
                    '100%': { opacity: '0', visibility: 'hidden', pointerEvents: 'none' },
                },
                move: {
                    '0%': { backgroundPosition: '100% 0' },
                    '100%': { backgroundPosition: '-100% 0' },
                }
            },
            animation: {
                'fade-out': 'fadeOut 2s 2s forwards ease-out',
                'move': 'move 2s linear infinite',
            }
        },
    },
    plugins: [],
}
