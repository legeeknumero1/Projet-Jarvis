/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: ["class"],
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
    "./public/index.html"
  ],
  theme: {
    extend: {
      fontFamily: {
        'sans': ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
        'mono': ['JetBrains Mono', 'Fira Code', 'monospace'],
      },
      colors: {
        // Cyberpunk Jarvis Neon theme
        jarvis: {
          // Backgrounds
          'bg-deep': '#06080c',        // Fond principal noir profond
          'bg-surface': '#0b0f17',     // Surfaces bleu nuit
          
          // Primary neon colors
          'neon-cyan': '#00e5ff',      // Couleur primaire cyan néon
          'neon-pink': '#ff3bd4',      // Couleur secondaire rose néon
          'neon-purple': '#8a2be2',    // Couleur tertiaire violet électrique
          'neon-green': '#4cff7a',     // Succès vert néon
          'neon-orange': '#ffb300',    // Avertissement orange vif
          
          // Text colors
          'text-primary': '#ffffff',    // Texte principal blanc pur
          'text-secondary': '#e8eaed',  // Texte secondaire gris très clair
          'text-muted': '#9aa0a6',     // Texte discret
          'text-disabled': '#5f6368',   // Texte désactivé
          
          // Interactive states
          'glow-cyan': 'rgba(0, 229, 255, 0.4)',
          'glow-pink': 'rgba(255, 59, 212, 0.4)',
          'glow-purple': 'rgba(138, 43, 226, 0.4)',
          'glow-green': 'rgba(76, 255, 122, 0.4)',
          
          // Borders and overlays
          'border-subtle': 'rgba(0, 229, 255, 0.2)',
          'border-bright': 'rgba(0, 229, 255, 0.6)',
          'overlay': 'rgba(11, 15, 23, 0.8)',
        },
        
        // Keep existing shadcn colors for component compatibility
        background: 'hsl(var(--background))',
        foreground: 'hsl(var(--foreground))',
        card: {
          DEFAULT: 'hsl(var(--card))',
          foreground: 'hsl(var(--card-foreground))'
        },
        popover: {
          DEFAULT: 'hsl(var(--popover))',
          foreground: 'hsl(var(--popover-foreground))'
        },
        primary: {
          DEFAULT: 'hsl(var(--primary))',
          foreground: 'hsl(var(--primary-foreground))'
        },
        secondary: {
          DEFAULT: 'hsl(var(--secondary))',
          foreground: 'hsl(var(--secondary-foreground))'
        },
        muted: {
          DEFAULT: 'hsl(var(--muted))',
          foreground: 'hsl(var(--muted-foreground))'
        },
        accent: {
          DEFAULT: 'hsl(var(--accent))',
          foreground: 'hsl(var(--accent-foreground))'
        },
        destructive: {
          DEFAULT: 'hsl(var(--destructive))',
          foreground: 'hsl(var(--destructive-foreground))'
        },
        border: 'hsl(var(--border))',
        input: 'hsl(var(--input))',
        ring: 'hsl(var(--ring))',
        chart: {
          '1': 'hsl(var(--chart-1))',
          '2': 'hsl(var(--chart-2))',
          '3': 'hsl(var(--chart-3))',
          '4': 'hsl(var(--chart-4))',
          '5': 'hsl(var(--chart-5))'
        }
      },
      borderRadius: {
        lg: 'var(--radius)',
        md: 'calc(var(--radius) - 2px)',
        sm: 'calc(var(--radius) - 4px)'
      },
      backdropBlur: {
        xs: '2px',
      },
      boxShadow: {
        // Neon glow effects
        'neon-cyan': '0 0 20px rgba(0, 229, 255, 0.5), 0 0 40px rgba(0, 229, 255, 0.2)',
        'neon-pink': '0 0 20px rgba(255, 59, 212, 0.5), 0 0 40px rgba(255, 59, 212, 0.2)',
        'neon-purple': '0 0 20px rgba(138, 43, 226, 0.5), 0 0 40px rgba(138, 43, 226, 0.2)',
        'neon-green': '0 0 20px rgba(76, 255, 122, 0.5), 0 0 40px rgba(76, 255, 122, 0.2)',
        'neon-orange': '0 0 20px rgba(255, 179, 0, 0.5), 0 0 40px rgba(255, 179, 0, 0.2)',
        
        // Subtle glows
        'glow-subtle-cyan': '0 0 10px rgba(0, 229, 255, 0.3)',
        'glow-subtle-pink': '0 0 10px rgba(255, 59, 212, 0.3)',
        'glow-subtle-purple': '0 0 10px rgba(138, 43, 226, 0.3)',
        
        // Inner glows
        'inner-neon-cyan': 'inset 0 0 20px rgba(0, 229, 255, 0.1)',
        'inner-neon-pink': 'inset 0 0 20px rgba(255, 59, 212, 0.1)',
        'inner-neon-purple': 'inset 0 0 20px rgba(138, 43, 226, 0.1)',
        
        // Multi-layer glows for intense effects
        'ultra-neon-cyan': '0 0 5px #00e5ff, 0 0 20px #00e5ff, 0 0 40px #00e5ff, 0 0 80px #00e5ff',
        'ultra-neon-pink': '0 0 5px #ff3bd4, 0 0 20px #ff3bd4, 0 0 40px #ff3bd4, 0 0 80px #ff3bd4',
      },
      animation: {
        // Neon pulse animations
        'neon-pulse-cyan': 'neonPulseCyan 2s ease-in-out infinite alternate',
        'neon-pulse-pink': 'neonPulsePink 2s ease-in-out infinite alternate',
        'neon-pulse-purple': 'neonPulsePurple 2s ease-in-out infinite alternate',
        
        // Flicker animations
        'neon-flicker': 'neonFlicker 3s linear infinite',
        'cyber-scan': 'cyberScan 4s linear infinite',
        
        // Float and rotation
        'float-slow': 'floatSlow 6s ease-in-out infinite',
        'rotate-slow': 'rotateSlow 10s linear infinite',
        
        // Existing
        'glow': 'glow 2s ease-in-out infinite alternate',
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'float': 'float 6s ease-in-out infinite',
        'scan': 'scan 2s linear infinite',
        'accordion-down': 'accordion-down 0.2s ease-out',
        'accordion-up': 'accordion-up 0.2s ease-out'
      },
      keyframes: {
        // Neon pulse keyframes
        neonPulseCyan: {
          'from': { boxShadow: '0 0 10px rgba(0, 229, 255, 0.3), 0 0 20px rgba(0, 229, 255, 0.2)' },
          'to': { boxShadow: '0 0 30px rgba(0, 229, 255, 0.8), 0 0 60px rgba(0, 229, 255, 0.4)' }
        },
        neonPulsePink: {
          'from': { boxShadow: '0 0 10px rgba(255, 59, 212, 0.3), 0 0 20px rgba(255, 59, 212, 0.2)' },
          'to': { boxShadow: '0 0 30px rgba(255, 59, 212, 0.8), 0 0 60px rgba(255, 59, 212, 0.4)' }
        },
        neonPulsePurple: {
          'from': { boxShadow: '0 0 10px rgba(138, 43, 226, 0.3), 0 0 20px rgba(138, 43, 226, 0.2)' },
          'to': { boxShadow: '0 0 30px rgba(138, 43, 226, 0.8), 0 0 60px rgba(138, 43, 226, 0.4)' }
        },
        
        // Flicker effect
        neonFlicker: {
          '0%, 100%': { opacity: '1' },
          '2%, 8%': { opacity: '0.8' },
          '4%': { opacity: '0.9' },
          '12%': { opacity: '0.7' },
          '14%': { opacity: '1' },
          '16%': { opacity: '0.9' },
          '18%': { opacity: '1' },
          '20%': { opacity: '0.8' },
          '22%': { opacity: '1' }
        },
        
        // Cyber scan line
        cyberScan: {
          '0%': { transform: 'translateY(-100%)' },
          '100%': { transform: 'translateY(100vh)' }
        },
        
        // Floating animations
        floatSlow: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-15px)' }
        },
        rotateSlow: {
          'from': { transform: 'rotate(0deg)' },
          'to': { transform: 'rotate(360deg)' }
        },
        
        // Existing keyframes
        glow: {
          'from': { boxShadow: '0 0 10px rgba(0, 229, 255, 0.2)' },
          'to': { boxShadow: '0 0 30px rgba(0, 229, 255, 0.6)' }
        },
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-10px)' }
        },
        scan: {
          '0%': { transform: 'translateX(-100%)' },
          '100%': { transform: 'translateX(100vw)' }
        },
        'accordion-down': {
          from: { height: '0' },
          to: { height: 'var(--radix-accordion-content-height)' }
        },
        'accordion-up': {
          from: { height: 'var(--radix-accordion-content-height)' },
          to: { height: '0' }
        }
      },
      backgroundImage: {
        'cyber-grid': `
          linear-gradient(rgba(0, 229, 255, 0.1) 1px, transparent 1px),
          linear-gradient(90deg, rgba(0, 229, 255, 0.1) 1px, transparent 1px)
        `,
        'neon-gradient-cyan': 'linear-gradient(135deg, #00e5ff 0%, #6df6ff 100%)',
        'neon-gradient-pink': 'linear-gradient(135deg, #ff3bd4 0%, #ff8a80 100%)',
        'neon-gradient-purple': 'linear-gradient(135deg, #8a2be2 0%, #b649d6 100%)',
      }
    }
  },
  plugins: [require("tailwindcss-animate")],
};