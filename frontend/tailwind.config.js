/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        // RiskLens AI dark "SOC console" palette
        base: '#0b1220',
        panel: '#111a2e',
        panel2: '#16233c',
        line: '#1f2d48',
        accent: '#38bdf8',
        ok: '#22c55e',
        warn: '#f59e0b',
        danger: '#ef4444',
        ink: '#e2e8f0',
        muted: '#64748b',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'ui-monospace', 'monospace'],
      },
    },
  },
  plugins: [],
}
