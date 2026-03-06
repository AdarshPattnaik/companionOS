<template>
  <div class="page">
    <div class="page-header">
      <h1>Dashboard</h1>
      <p>Real-time vehicle and system overview</p>
    </div>

    <!-- Status Cards Row -->
    <div class="grid grid-4 fade-in" style="margin-bottom: 20px;">
      <div class="card status-card">
        <div class="card-title">Vehicle</div>
        <div class="status-value">
          <i class="mdi mdi-submarine" style="color: var(--coratia-primary)"></i>
          <span :class="vehicle.connected ? 'text-success' : 'text-danger'">
            {{ vehicle.connected ? 'Connected' : 'Disconnected' }}
          </span>
        </div>
        <div class="status-sub">{{ vehicle.firmware_type }}</div>
      </div>

      <div class="card status-card">
        <div class="card-title">Armed Status</div>
        <div class="status-value">
          <i class="mdi" :class="vehicle.armed ? 'mdi-shield-alert text-warning' : 'mdi-shield-check text-success'"></i>
          <span>{{ vehicle.armed ? 'ARMED' : 'DISARMED' }}</span>
        </div>
        <div class="status-sub">Mode: {{ vehicle.flight_mode }}</div>
      </div>

      <div class="card status-card">
        <div class="card-title">Battery</div>
        <div class="status-value">
          <i class="mdi mdi-battery" style="color: var(--status-success)"></i>
          <span>{{ vehicle.battery_voltage.toFixed(1) }}V</span>
        </div>
        <div class="status-sub">{{ vehicle.battery_remaining }}% remaining</div>
      </div>

      <div class="card status-card">
        <div class="card-title">Depth</div>
        <div class="status-value">
          <i class="mdi mdi-waves" style="color: var(--coratia-accent)"></i>
          <span>{{ telemetry.depth.toFixed(1) }}m</span>
        </div>
        <div class="status-sub">Heading: {{ telemetry.heading }}°</div>
      </div>
    </div>

    <!-- Gauges Row -->
    <div class="grid grid-4 fade-in" style="animation-delay: 0.1s; margin-bottom: 20px;">
      <div class="card">
        <div class="card-title">CPU</div>
        <div class="gauge-container">
          <div class="gauge-ring">
            <svg viewBox="0 0 100 100" width="100" height="100">
              <circle class="gauge-bg" cx="50" cy="50" r="42"/>
              <circle class="gauge-fill" cx="50" cy="50" r="42"
                :stroke="gaugeColor(system.cpu_percent)"
                :stroke-dasharray="264"
                :stroke-dashoffset="264 - (264 * system.cpu_percent / 100)"/>
            </svg>
            <div class="gauge-value">{{ system.cpu_percent }}%</div>
          </div>
          <div class="gauge-label">Usage</div>
        </div>
      </div>

      <div class="card">
        <div class="card-title">Memory</div>
        <div class="gauge-container">
          <div class="gauge-ring">
            <svg viewBox="0 0 100 100" width="100" height="100">
              <circle class="gauge-bg" cx="50" cy="50" r="42"/>
              <circle class="gauge-fill" cx="50" cy="50" r="42"
                :stroke="gaugeColor(system.memory_percent)"
                :stroke-dasharray="264"
                :stroke-dashoffset="264 - (264 * system.memory_percent / 100)"/>
            </svg>
            <div class="gauge-value">{{ system.memory_percent }}%</div>
          </div>
          <div class="gauge-label">Used</div>
        </div>
      </div>

      <div class="card">
        <div class="card-title">Temperature</div>
        <div class="gauge-container">
          <div class="gauge-ring">
            <svg viewBox="0 0 100 100" width="100" height="100">
              <circle class="gauge-bg" cx="50" cy="50" r="42"/>
              <circle class="gauge-fill" cx="50" cy="50" r="42"
                :stroke="tempColor(system.temperature)"
                :stroke-dasharray="264"
                :stroke-dashoffset="264 - (264 * Math.min(system.temperature, 85) / 85)"/>
            </svg>
            <div class="gauge-value">{{ system.temperature }}°</div>
          </div>
          <div class="gauge-label">CPU Temp</div>
        </div>
      </div>

      <div class="card">
        <div class="card-title">Disk</div>
        <div class="gauge-container">
          <div class="gauge-ring">
            <svg viewBox="0 0 100 100" width="100" height="100">
              <circle class="gauge-bg" cx="50" cy="50" r="42"/>
              <circle class="gauge-fill" cx="50" cy="50" r="42"
                :stroke="gaugeColor(system.disk_percent)"
                :stroke-dasharray="264"
                :stroke-dashoffset="264 - (264 * system.disk_percent / 100)"/>
            </svg>
            <div class="gauge-value">{{ system.disk_percent }}%</div>
          </div>
          <div class="gauge-label">Storage</div>
        </div>
      </div>
    </div>

    <!-- Bottom Row -->
    <div class="grid grid-2 fade-in" style="animation-delay: 0.2s;">
      <!-- Attitude Display -->
      <div class="card">
        <div class="card-title">Vehicle Attitude</div>
        <div class="attitude-display">
          <div class="attitude-item">
            <span class="attitude-label">Roll</span>
            <span class="attitude-value">{{ telemetry.roll.toFixed(1) }}°</span>
          </div>
          <div class="attitude-item">
            <span class="attitude-label">Pitch</span>
            <span class="attitude-value">{{ telemetry.pitch.toFixed(1) }}°</span>
          </div>
          <div class="attitude-item">
            <span class="attitude-label">Yaw</span>
            <span class="attitude-value">{{ telemetry.yaw.toFixed(1) }}°</span>
          </div>
          <div class="attitude-item">
            <span class="attitude-label">Heading</span>
            <span class="attitude-value">{{ telemetry.heading }}°</span>
          </div>
        </div>
      </div>

      <!-- Quick Actions -->
      <div class="card">
        <div class="card-title">Quick Actions</div>
        <div class="quick-actions">
          <button class="btn btn-primary" @click="detectVehicle">
            <i class="mdi mdi-magnify-scan"></i> Detect Vehicle
          </button>
          <button class="btn btn-secondary" @click="$router.push('/endpoints')">
            <i class="mdi mdi-lan-connect"></i> Endpoints
          </button>
          <button class="btn btn-secondary" @click="$router.push('/video')">
            <i class="mdi mdi-video"></i> Video
          </button>
          <button class="btn btn-secondary" @click="$router.push('/extensions')">
            <i class="mdi mdi-puzzle"></i> Extensions
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'DashboardView',
  data() {
    return {
      vehicle: {
        connected: false, armed: false, flight_mode: 'MANUAL',
        firmware_type: 'ArduSub', battery_voltage: 0, battery_remaining: 0,
      },
      system: { cpu_percent: 0, memory_percent: 0, temperature: 0, disk_percent: 0 },
      telemetry: { depth: 0, heading: 0, roll: 0, pitch: 0, yaw: 0 },
      ws: null,
    }
  },
  mounted() {
    this.fetchVehicle()
    this.fetchSystem()
    this.connectTelemetryWS()
  },
  beforeUnmount() {
    if (this.ws) this.ws.close()
  },
  methods: {
    gaugeColor(pct) {
      if (pct > 80) return 'var(--status-danger)'
      if (pct > 60) return 'var(--status-warning)'
      return 'var(--coratia-primary)'
    },
    tempColor(t) {
      if (t > 70) return 'var(--status-danger)'
      if (t > 55) return 'var(--status-warning)'
      return 'var(--coratia-accent)'
    },
    async fetchVehicle() {
      try {
        const r = await fetch('/ardupilot-manager/v1.0/vehicle/status')
        this.vehicle = await r.json()
      } catch {}
    },
    async fetchSystem() {
      try {
        const [cpu, mem, disk] = await Promise.all([
          fetch('/helper/v1.0/system/cpu').then(r => r.json()),
          fetch('/helper/v1.0/system/memory').then(r => r.json()),
          fetch('/helper/v1.0/system/disk').then(r => r.json()),
        ])
        this.system = {
          cpu_percent: Math.round(cpu.usage_percent),
          memory_percent: Math.round(mem.usage_percent),
          temperature: Math.round(cpu.temperature),
          disk_percent: Math.round(disk.usage_percent),
        }
      } catch {}
      setTimeout(() => this.fetchSystem(), 3000)
    },
    connectTelemetryWS() {
      try {
        const proto = location.protocol === 'https:' ? 'wss:' : 'ws:'
        this.ws = new WebSocket(`${proto}//${location.host}/ardupilot-manager/v1.0/ws/telemetry`)
        this.ws.onmessage = (e) => { this.telemetry = JSON.parse(e.data) }
        this.ws.onclose = () => setTimeout(() => this.connectTelemetryWS(), 5000)
      } catch {}
    },
    async detectVehicle() {
      try {
        const r = await fetch('/ardupilot-manager/v1.0/vehicle/detect')
        const data = await r.json()
        alert(data.detected ? `Found: ${data.board.name}` : 'No flight controller detected')
      } catch { alert('Service unavailable') }
    }
  }
}
</script>

<style scoped>
.status-card { text-align: center; }
.status-value {
  font-size: 1.25rem;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin: 8px 0;
}
.status-sub { font-size: 0.8rem; color: var(--text-secondary); }
.text-success { color: var(--status-success); }
.text-warning { color: var(--status-warning); }
.text-danger { color: var(--status-danger); }

.attitude-display { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; padding: 12px 0; }
.attitude-item { text-align: center; padding: 12px; background: var(--bg-base); border-radius: var(--radius-sm); }
.attitude-label { display: block; font-size: 0.75rem; color: var(--text-secondary); text-transform: uppercase; }
.attitude-value { display: block; font-size: 1.5rem; font-weight: 700; color: var(--coratia-primary); margin-top: 4px; }

.quick-actions { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
.quick-actions .btn { justify-content: center; padding: 14px; }
</style>
