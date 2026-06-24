/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  poweredByHeader: false,
  // Standalone is for Docker/self-hosting; Vercel uses its own Next.js packaging.
  ...(process.env.VERCEL ? {} : { output: "standalone" }),
  experimental: {
    typedRoutes: true,
    optimizePackageImports: ["lucide-react"],
  },
};

export default nextConfig;
