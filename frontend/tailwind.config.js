/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        obsidian: {
          DEFAULT: '#0B1220',
          50: '#F0F3F9',
          100: '#DDE3F0',
          200: '#B8C5DE',
          300: '#8E9ECC',
          400: '#5F73A8',
          500: '#3D4F7F',
          600: '#28365B',
          700: '#1A243D',
          800: '#0B1220',
          900: '#060A13',
        },
        cloud: {
          DEFAULT: '#F7F8FA',
          50: '#FFFFFF',
          100: '#F7F8FA',
          200: '#EEF0F4',
          300: '#E1E4EB',
          400: '#CBD0DC',
        },
        electric: {
          DEFAULT: '#2563EB',
          50: '#EFF6FF',
          100: '#DBEAFE',
          500: '#3B82F6',
          600: '#2563EB',
          700: '#1D4ED8',
        },
        teal: {
          DEFAULT: '#14B8A6',
          50: '#F0FDFA',
          100: '#CCFBF1',
          500: '#14B8A6',
          600: '#0D9488',
          700: '#0F766E',
        },
        ai: {
          DEFAULT: '#7C3AED',
          50: '#F5F3FF',
          100: '#EDE9FE',
          500: '#8B5CF6',
          600: '#7C3AED',
          700: '#6D28D9',
        },
        status: {
          success: '#16A34A',
          warning: '#D97706',
          danger: '#DC2626',
        }
      },
      fontFamily: {
        heading: ['Manrope', 'sans-serif'],
        sans: ['Inter', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
      boxShadow: {
        subtle: '0 1px 3px 0 rgba(11, 18, 32, 0.05), 0 1px 2px 0 rgba(11, 18, 32, 0.03)',
        card: '0 4px 6px -1px rgba(11, 18, 32, 0.04), 0 2px 4px -1px rgba(11, 18, 32, 0.02)',
        modal: '0 20px 25px -5px rgba(11, 18, 32, 0.1), 0 10px 10px -5px rgba(11, 18, 32, 0.04)',
      },
      screens: {
        'xs': '320px',
        'sm': '375px',
        'md': '768px',
        'lg': '1024px',
        'xl': '1280px',
        '2xl': '1440px',
        '3xl': '1920px',
      }
    },
  },
  plugins: [],
}
