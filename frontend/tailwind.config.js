/** @type {import('tailwindcss').Config} */
// AiKhbar design system — dark luxury editorial aesthetic.
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        ink: {
          950: '#070910',
          900: '#0c0f1a',
          800: '#141826',
          700: '#1d2235',
        },
        gold: {
          300: '#f3d899',
          400: '#e7c573',
          500: '#d4ac4d',
          600: '#b8902f',
        },
        accent: '#5b8def',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        urdu: ['Noto Nastaliq Urdu', 'serif'],
        display: ['Fraunces', 'Georgia', 'serif'],
      },
      backgroundImage: {
        'glass-gradient':
          'linear-gradient(135deg, rgba(255,255,255,0.08), rgba(255,255,255,0.02))',
        'gold-radial':
          'radial-gradient(circle at 30% 20%, rgba(212,172,77,0.18), transparent 60%)',
      },
      boxShadow: {
        glass: '0 8px 32px rgba(0,0,0,0.45)',
        glow: '0 0 40px rgba(212,172,77,0.25)',
      },
      backdropBlur: { xs: '2px' },
      keyframes: {
        float: {
          '0%,100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-12px)' },
        },
        shimmer: {
          '0%': { backgroundPosition: '-200% 0' },
          '100%': { backgroundPosition: '200% 0' },
        },
      },
      animation: {
        float: 'float 7s ease-in-out infinite',
        shimmer: 'shimmer 2.5s linear infinite',
      },
    },
  },
  plugins: [],
};
