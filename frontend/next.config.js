/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  async rewrites() {
    const backend = process.env.BACKEND_URL || 'http://dclaw-monitor-backend:8030'
    return [
      { source: '/health/:path*', destination: `${backend}/health/:path*` },
      { source: '/api/:path*',    destination: `${backend}/api/:path*` },
      { source: '/metrics',       destination: `${backend}/metrics` },
    ]
  },
}

module.exports = nextConfig
