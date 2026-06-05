const SHOWCASE = "https://matx104.github.io/AETHERIX";

export interface ResourceLink {
  type: string;
  title: string;
  url: string;
  badge?: string;
}

export function ResourcesCard({ title, links }: { title: string; links: ResourceLink[] }) {
  return (
    <div className="card">
      <div className="card-header">
        <h3>{title}</h3>
        <a
          href={`${SHOWCASE}/#study`}
          target="_blank"
          rel="noopener noreferrer"
          className="btn btn-secondary btn-sm"
        >
          All Resources &rarr;
        </a>
      </div>
      <div className="resources-grid">
        {links.map((r, i) => (
          <a
            key={i}
            href={r.url}
            target="_blank"
            rel="noopener noreferrer"
            className="resource-item"
          >
            <span className="resource-type">{r.type}</span>
            <span className="resource-title">{r.title}</span>
            {r.badge && <span className="resource-badge">{r.badge}</span>}
          </a>
        ))}
      </div>
    </div>
  );
}

export function ShowcaseLink({ route, children }: { route: string; children: React.ReactNode }) {
  return (
    <a
      href={`${SHOWCASE}/#${route}`}
      target="_blank"
      rel="noopener noreferrer"
      className="btn btn-secondary btn-sm"
    >
      {children}
    </a>
  );
}

export const SHOWCASE_URL = SHOWCASE;
