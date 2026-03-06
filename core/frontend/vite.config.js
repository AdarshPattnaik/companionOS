import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// Backend service targets
const services = {
  '/ardupilot-manager': 'http://127.0.0.1:8000',
  '/commander':         'http://127.0.0.1:6010',
  '/video':             'http://127.0.0.1:6020',
  '/nmea-injector':     'http://127.0.0.1:6030',
  '/helper':            'http://127.0.0.1:6040',
  '/wifi-manager':      'http://127.0.0.1:6050',
  '/log-manager':       'http://127.0.0.1:6065',
  '/file-browser':      'http://127.0.0.1:7070',
  '/version-chooser':   'http://127.0.0.1:8081',
  '/cable-guy':         'http://127.0.0.1:9090',
  '/kraken':            'http://127.0.0.1:9134',
}

/**
 * Custom plugin that intercepts API requests and returns mock 503
 * responses when backend services aren't running. This prevents
 * Vite from spamming ECONNREFUSED errors during frontend-only dev.
 */
function mockBackendPlugin() {
  return {
    name: 'coratiaos-mock-backend',
    configureServer(server) {
      server.middlewares.use((req, res, next) => {
        const matchedPrefix = Object.keys(services).find(prefix => req.url?.startsWith(prefix))
        if (!matchedPrefix) return next()

        const target = services[matchedPrefix]
        const url = new URL(req.url, target)

        // Try proxying; on failure return a silent 503
        const http = require('http')
        const proxyReq = http.request(url.href, { method: req.method, headers: req.headers, timeout: 2000 }, (proxyRes) => {
          res.writeHead(proxyRes.statusCode, proxyRes.headers)
          proxyRes.pipe(res)
        })
        proxyReq.on('error', () => {
          if (!res.headersSent) {
            res.writeHead(503, { 'Content-Type': 'application/json' })
            res.end(JSON.stringify({ error: 'Service unavailable' }))
          }
        })
        proxyReq.on('timeout', () => {
          proxyReq.destroy()
          if (!res.headersSent) {
            res.writeHead(503, { 'Content-Type': 'application/json' })
            res.end(JSON.stringify({ error: 'Service timeout' }))
          }
        })
        if (req.method !== 'GET' && req.method !== 'HEAD') {
          req.pipe(proxyReq)
        } else {
          proxyReq.end()
        }
      })
    }
  }
}

export default defineConfig({
  plugins: [vue(), mockBackendPlugin()],
  server: {
    port: 2511,
  },
  build: {
    outDir: 'dist',
    sourcemap: false,
  }
})
