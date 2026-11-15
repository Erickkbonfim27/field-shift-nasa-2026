// Wordmark "E · Órbita no nome": a órbita passa por trás das letras e volta pela frente com o satélite.
export default function Logo() {
  return (
    <div className="wordmark" role="img" aria-label="Harvesty">
      <svg className="orb-tras" viewBox="0 0 980 230" aria-hidden="true"><ellipse cx="490" cy="118" rx="470" ry="86" transform="rotate(-7 490 118)" /></svg>
      <span className="wm-txt" aria-hidden="true">HARVESTY</span>
      <svg className="orb-frente" viewBox="0 0 980 230" aria-hidden="true">
        <path className="halo" d="M 600 191 A 470 86 -7 0 0 958 70" />
        <path className="arco" d="M 600 191 A 470 86 -7 0 0 958 70" />
        <circle className="sat" cx="955" cy="72" r="16" />
      </svg>
    </div>
  );
}
