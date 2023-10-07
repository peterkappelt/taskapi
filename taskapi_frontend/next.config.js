/** @type {import('next').NextConfig} */
const nextConfig = {
  trailingSlash: true,
  async rewrites() {
    return [
      {
        source: "/accounts/:path*/",
        destination: `${process.env.NEXT_PUBLIC_BACKEND_URL}/accounts/:path*/`,
      },
    ];
  },
};

module.exports = nextConfig;
