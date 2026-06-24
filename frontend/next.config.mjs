/** @type {import('next').NextConfig} */

function normalizeBackendUrl(raw) {
  let base = (raw ?? "http://localhost:8000").trim();
  if (!/^https?:\/\//i.test(base)) {
    base = `http://${base}`;
  }
  return base.replace(/\/$/, "");
}

const backendUrl = normalizeBackendUrl(process.env.BACKEND_URL);

const nextConfig = {
  reactStrictMode: true,
  poweredByHeader: false,
  // Standalone is for Docker/self-hosting; Vercel uses its own Next.js packaging.
  ...(process.env.VERCEL ? {} : { output: "standalone" }),
  experimental: {
    typedRoutes: true,
    optimizePackageImports: ["lucide-react"],
  },
  // Proxy /api/* vers l'EC2 (BACKEND_URL sur Vercel, lu au build).
  // Preferable a vercel.json : supporte les variables d'environnement.
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: `${backendUrl}/api/:path*`,
      },
    ];
  },
};

export default nextConfig;
