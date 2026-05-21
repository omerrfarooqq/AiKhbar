/** @type {import('tailwindcss').Config} */
// AiKhbar design system — light editorial aesthetic:
// a warm cream canvas, ocean-blue accent and metallic-steel neutrals.
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        // Warm paper canvas + surfaces.
        cream: {
          50: '#FCFAF4',
          100: '#F8F3E7',
          200: '#F0E8D5',
          300: '#E5D9BE',
        },
        // Ocean blue — primary accent, drawn from the logo globe.
        ocean: {
          300: '#7FB2D0',
          400: '#4C8DB8',
          500: '#2A6E9C',
          600: '#1E5478',
          700: '#163E59',
          800: '#102C40',
        },
        // Metallic steel — neutrals, borders, secondary text.
        steel: {
          100: '#EEF1F4',
          200: '#DCE1E6',
          300: '#C2CAD2',
          400: '#97A2AD',
          500: '#6C7884',
          600: '#4C5660',
          700: '#343C45',
        },
        // Near-black ink — headings and primary text.
        ink: {
          700: '#39424E',
          800: '#262C36',
          900: '#171B22',
          950: '#0E1117',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        urdu: ['"Noto Naskh Arabic"', 'serif'],
        display: ['Fraunces', 'Georgia', 'serif'],
      },
      backgroundImage: {
        'glass-gradient':
          'linear-gradient(150deg, rgba(255,255,255,0.88), rgba(255,255,255,0.58))',
        'ocean-radial':
          'radial-gradient(circle at 30% 20%, rgba(42,110,156,0.14), transparent 62%)',
      },
      boxShadow: {
        soft: '0 2px 10px rgba(22,40,56,0.05), 0 12px 32px rgba(22,40,56,0.07)',
        lift: '0 20px 50px rgba(22,40,56,0.14)',
        glow: '0 0 38px rgba(42,110,156,0.22)',
      },
      backdropBlur: { xs: '2px' },
      keyframes: {
        float: {
          '0%,100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-14px)' },
        },
        shimmer: {
          '0%': { backgroundPosition: '-200% 0' },
          '100%': { backgroundPosition: '200% 0' },
        },
        'spin-slow': {
          '0%': { transform: 'rotate(0deg)' },
          '100%': { transform: 'rotate(360deg)' },
        },
      },
      animation: {
        float: 'float 8s ease-in-out infinite',
        shimmer: 'shimmer 2.5s linear infinite',
        'spin-slow': 'spin-slow 60s linear infinite',
      },
    },
  },
  plugins: [],
};
