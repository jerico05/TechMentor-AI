/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  poweredByHeader: false,
  output: "standalone",
  experimental: {
    typedRoutes: true,
  },
  // Proxy `/api/*` to the FastAPI backend in dev so the browser hits same-origin.
  async rewrites() {
    const backendUrl = process.env.BACKEND_URL ?? "http://localhost:8001";
    return [
      {
        source: "/api/:path*",
        destination: `${backendUrl}/api/:path*`,
      },
    ];
  },
};

export default nextConfig;
