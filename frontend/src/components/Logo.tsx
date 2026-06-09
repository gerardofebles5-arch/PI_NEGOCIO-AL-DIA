export function Logo({ size = 40 }: { size?: number }) {
  return (
    <div className="flex items-center gap-3">
      <svg
        width={size}
        height={size}
        viewBox="0 0 64 64"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        aria-hidden
      >
        <defs>
          <linearGradient id="piGold" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0%" stopColor="#f4e0ab" />
            <stop offset="45%" stopColor="#d9b158" />
            <stop offset="100%" stopColor="#936a31" />
          </linearGradient>
        </defs>
        <rect x="2" y="2" width="60" height="60" rx="16" fill="#292B2A" />
        <rect
          x="2"
          y="2"
          width="60"
          height="60"
          rx="16"
          fill="none"
          stroke="url(#piGold)"
          strokeWidth="2"
        />
        <text
          x="32"
          y="44"
          textAnchor="middle"
          fontFamily="'League Gothic', sans-serif"
          fontSize="40"
          fill="url(#piGold)"
        >
          π
        </text>
      </svg>
      <div className="leading-none">
        <div
          className="font-display text-2xl text-pi-ink"
          style={{ letterSpacing: "0.04em" }}
        >
          (π)NAD
        </div>
        <div className="text-[10px] uppercase tracking-[0.25em] text-pi-gold-deep">
          Negocio al día
        </div>
      </div>
    </div>
  );
}
