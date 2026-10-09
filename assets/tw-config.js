// Paleta "póster de viaje" compartida por todas las páginas.
// indigo/slate/emerald se redefinen para que las clases existentes (y el modal de Reservar) adopten el estilo.
tailwind.config = {
  theme: {
    extend: {
      fontFamily: {
        sans: ['"DM Sans"', 'system-ui', 'Segoe UI', 'sans-serif'],
        display: ['"Josefin Sans"', 'system-ui', 'sans-serif'],
        slab: ['"Josefin Slab"', 'Georgia', 'serif'],
      },
      letterSpacing: {
        tightest: '-0.02em',
        poster: '0.08em',
      },
      colors: {
        paper: '#FBF4E4',
        cream: '#F6E7CB',
        plum: { DEFAULT: '#42344A', soft: '#5B4B66', night: '#33283B' },
        sky: { DEFAULT: '#7FAEE0', light: '#B9D5EE' },
        peach: '#F2C3A7',
        mustard: '#EDB84E',
        meadow: '#A6CB72',
        indigo: {
          50: '#FDF1EA', 100: '#FADFD0', 200: '#F4BFA2', 300: '#EC9B73', 400: '#E27A4E',
          500: '#D4613A', 600: '#C24F2C', 700: '#A13F23', 800: '#80331E', 900: '#5F2717',
        },
        slate: {
          50: '#FBF6EC', 100: '#F3EADB', 200: '#E5D8C6', 300: '#CDBBAA', 400: '#A8958C',
          500: '#85727A', 600: '#6A5868', 700: '#54445A', 800: '#42344A', 900: '#33283B',
        },
        emerald: {
          50: '#EEF5E6', 100: '#DCEBCB', 200: '#BCD9A2', 300: '#9CC57C', 400: '#74A862',
          500: '#4F9460', 600: '#3E7F4F', 700: '#346B43', 800: '#2A5636', 900: '#20412A',
        },
      },
    },
  },
};
