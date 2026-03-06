<template>
  <div class="app-layout">
    <!-- Sidebar -->
    <aside class="sidebar" :class="{ collapsed: sidebarCollapsed }">
      <div class="sidebar-header">
        <div class="logo" @click="sidebarCollapsed = !sidebarCollapsed">
          <div class="logo-icon">
            <svg viewBox="0 0 40 40" width="32" height="32">
              <circle cx="20" cy="20" r="18" fill="none" stroke="var(--coratia-primary)" stroke-width="2.5"/>
              <path d="M12 20 C12 14, 20 8, 28 14 L20 26 L12 20Z" fill="var(--coratia-accent)" opacity="0.9"/>
              <circle cx="20" cy="18" r="3" fill="var(--coratia-primary)"/>
            </svg>
          </div>
          <transition name="fade">
            <div v-if="!sidebarCollapsed" class="logo-text">
              <span class="logo-name">CoratiaOS</span>
              <span class="logo-version">v1.0.0</span>
            </div>
          </transition>
        </div>
      </div>

      <nav class="sidebar-nav">
        <router-link
          v-for="route in navRoutes"
          :key="route.path"
          :to="route.path"
          class="nav-item"
          :class="{ active: $route.path === route.path }"
        >
          <i :class="route.meta.icon" class="nav-icon"></i>
          <transition name="fade">
            <span v-if="!sidebarCollapsed" class="nav-label">{{ route.meta.label }}</span>
          </transition>
          <transition name="fade">
            <span v-if="!sidebarCollapsed && route.path === '/'" class="nav-badge badge-success">●</span>
          </transition>
        </router-link>
      </nav>

      <div class="sidebar-footer">
        <div class="system-status" v-if="!sidebarCollapsed">
          <div class="status-row">
            <i class="mdi mdi-thermometer" style="color: var(--status-warning)"></i>
            <span>{{ systemStats.temperature }}°C</span>
          </div>
          <div class="status-row">
            <i class="mdi mdi-memory" style="color: var(--coratia-primary)"></i>
            <span>{{ systemStats.memoryPercent }}%</span>
          </div>
          <div class="status-row">
            <i class="mdi mdi-speedometer" style="color: var(--coratia-accent)"></i>
            <span>{{ systemStats.cpuPercent }}%</span>
          </div>
        </div>
        <div class="power-controls">
          <button class="btn-icon" title="Reboot" @click="reboot">
            <i class="mdi mdi-restart"></i>
          </button>
          <button class="btn-icon" title="Shutdown" @click="shutdown" v-if="!sidebarCollapsed">
            <i class="mdi mdi-power"></i>
          </button>
        </div>
      </div>
    </aside>

    <!-- Main Content -->
    <main class="main-content">
      <header class="top-bar">
        <div class="top-bar-left">
          <h2 class="current-page-title">{{ $route.meta.label || $route.name }}</h2>
        </div>
        <div class="top-bar-right">
          <div class="vehicle-status">
            <span class="badge" :class="vehicleConnected ? 'badge-success' : 'badge-danger'">
              <i class="mdi" :class="vehicleConnected ? 'mdi-link' : 'mdi-link-off'"></i>
              {{ vehicleConnected ? 'Connected' : 'Disconnected' }}
            </span>
            <span class="badge" :class="vehicleArmed ? 'badge-warning' : 'badge-info'">
              {{ vehicleArmed ? 'ARMED' : 'DISARMED' }}
            </span>
            <span class="badge badge-info">{{ flightMode }}</span>
          </div>
          <div class="coratia-brand">
            <span class="brand-text">Coratia</span>
          </div>
        </div>
      </header>

      <div class="content-area">
        <router-view v-slot="{ Component }">
          <transition name="page-fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </div>
    </main>
  </div>
</template>

<script>
import { routes } from './router'

export default {
  name: 'App',
  data() {
    return {
      sidebarCollapsed: false,
      vehicleConnected: false,
      vehicleArmed: false,
      flightMode: 'MANUAL',
      systemStats: { cpuPercent: 0, memoryPercent: 0, temperature: 0 },
      wsConnection: null,
    }
  },
  computed: {
    navRoutes() {
      return routes.filter(r => r.meta && r.meta.label)
    }
  },
  mounted() {
    this.connectSystemWS()
    this.fetchVehicleStatus()
  },
  beforeUnmount() {
    if (this.wsConnection) this.wsConnection.close()
  },
  methods: {
    connectSystemWS() {
      try {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
        this.wsConnection = new WebSocket(`${protocol}//${window.location.host}/helper/v1.0/ws/system`)
        this.wsConnection.onmessage = (event) => {
          const data = JSON.parse(event.data)
          this.systemStats = {
            cpuPercent: Math.round(data.cpu_percent || 0),
            memoryPercent: Math.round(data.memory_percent || 0),
            temperature: Math.round(data.temperature || 0),
          }
        }
        this.wsConnection.onclose = () => {
          setTimeout(() => this.connectSystemWS(), 5000)
        }
      } catch (e) {
        console.warn('System WebSocket failed:', e)
      }
    },
    async fetchVehicleStatus() {
      try {
        const resp = await fetch('/ardupilot-manager/v1.0/vehicle/status')
        const data = await resp.json()
        this.vehicleConnected = data.connected
        this.vehicleArmed = data.armed
        this.flightMode = data.flight_mode || 'MANUAL'
      } catch (e) {
        // Services not running in dev mode
      }
      setTimeout(() => this.fetchVehicleStatus(), 3000)
    },
    async reboot() {
      if (confirm('Reboot system?')) {
        await fetch('/helper/v1.0/system/reboot', { method: 'POST' })
      }
    },
    async shutdown() {
      if (confirm('Shutdown system?')) {
        await fetch('/helper/v1.0/system/shutdown', { method: 'POST' })
      }
    }
  }
}
</script>

<style scoped>
.app-layout {
  display: flex;
  width: 100%;
  height: 100vh;
  overflow: hidden;
}

/* ── Sidebar ── */
.sidebar {
  width: var(--sidebar-width);
  min-width: var(--sidebar-width);
  background: var(--bg-surface);
  border-right: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
  transition: all var(--transition-slow);
  z-index: 100;
}
.sidebar.collapsed {
  width: var(--sidebar-collapsed);
  min-width: var(--sidebar-collapsed);
}

.sidebar-header {
  padding: 16px;
  border-bottom: 1px solid var(--border-color);
}
.logo {
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
  padding: 4px;
  border-radius: var(--radius-sm);
  transition: background var(--transition-fast);
}
.logo:hover {
  background: var(--bg-card);
}
.logo-icon {
  flex-shrink: 0;
  width: 32px;
  height: 32px;
}
.logo-name {
  font-size: 1.1rem;
  font-weight: 700;
  background: linear-gradient(135deg, var(--coratia-primary), var(--coratia-accent));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  white-space: nowrap;
}
.logo-version {
  display: block;
  font-size: 0.65rem;
  color: var(--text-muted);
  white-space: nowrap;
}

.sidebar-nav {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}
.nav-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 12px;
  margin: 2px 0;
  border-radius: var(--radius-sm);
  color: var(--text-secondary);
  transition: all var(--transition-fast);
  text-decoration: none;
  position: relative;
  white-space: nowrap;
}
.nav-item:hover {
  background: var(--bg-card);
  color: var(--text-primary);
}
.nav-item.active {
  background: var(--coratia-accent-dim);
  color: var(--coratia-primary);
}
.nav-item.active::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 3px;
  height: 60%;
  background: var(--coratia-primary);
  border-radius: 0 3px 3px 0;
}
.nav-icon {
  font-size: 1.2rem;
  flex-shrink: 0;
  width: 24px;
  text-align: center;
}
.nav-label {
  font-size: 0.875rem;
  font-weight: 500;
}
.nav-badge {
  margin-left: auto;
  font-size: 0.5rem;
}

.sidebar-footer {
  padding: 12px;
  border-top: 1px solid var(--border-color);
}
.system-status {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-bottom: 8px;
  padding: 8px;
  background: var(--bg-card);
  border-radius: var(--radius-sm);
}
.status-row {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.8rem;
  color: var(--text-secondary);
}
.power-controls {
  display: flex;
  gap: 8px;
  justify-content: center;
}
.btn-icon {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid var(--border-color);
  border-radius: var(--radius-sm);
  background: transparent;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all var(--transition-fast);
}
.btn-icon:hover {
  background: var(--bg-card);
  color: var(--text-primary);
  border-color: var(--border-active);
}

/* ── Main Content ── */
.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.top-bar {
  height: var(--header-height);
  min-height: var(--header-height);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  background: var(--bg-surface);
  border-bottom: 1px solid var(--border-color);
}
.current-page-title {
  font-size: 1.1rem;
  font-weight: 600;
}
.top-bar-right {
  display: flex;
  align-items: center;
  gap: 16px;
}
.vehicle-status {
  display: flex;
  gap: 8px;
}
.brand-text {
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.1em;
}

.content-area {
  flex: 1;
  overflow-y: auto;
  background: var(--bg-base);
}

/* ── Transitions ── */
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.2s ease;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}

.page-fade-enter-active {
  transition: opacity 0.25s ease, transform 0.25s ease;
}
.page-fade-leave-active {
  transition: opacity 0.15s ease;
}
.page-fade-enter-from {
  opacity: 0;
  transform: translateY(6px);
}
.page-fade-leave-to {
  opacity: 0;
}
</style>
