<template>
  <div class="page">
    <div class="page-header">
      <h1>Vehicle Setup</h1>
      <p>Flight controller information and vehicle configuration</p>
    </div>
    <div class="grid grid-2 fade-in">
      <div class="card">
        <div class="card-title">Flight Controller</div>
        <div class="info-grid">
          <div class="info-item"><span class="info-label">Status</span><span class="badge badge-success">Connected</span></div>
          <div class="info-item"><span class="info-label">Firmware</span><span>ArduSub v4.1.1</span></div>
          <div class="info-item"><span class="info-label">Board</span><span>Pixhawk 1</span></div>
          <div class="info-item"><span class="info-label">MAVLink</span><span>2.0</span></div>
          <div class="info-item"><span class="info-label">System ID</span><span>1</span></div>
          <div class="info-item"><span class="info-label">Serial Port</span><span>/dev/ttyACM0</span></div>
        </div>
        <button class="btn btn-primary" style="margin-top: 16px;" @click="detect">
          <i class="mdi mdi-magnify-scan"></i> Auto Detect
        </button>
      </div>
      <div class="card">
        <div class="card-title">Vehicle Configuration</div>
        <div class="info-grid">
          <div class="info-item"><span class="info-label">Vehicle Type</span><span>Submarine</span></div>
          <div class="info-item"><span class="info-label">Frame</span><span>BlueROV2 Heavy</span></div>
          <div class="info-item"><span class="info-label">Thrusters</span><span>8</span></div>
          <div class="info-item"><span class="info-label">Lights</span><span>2 channels</span></div>
        </div>
      </div>
    </div>
    <div class="card fade-in" style="margin-top: 16px;">
      <div class="card-title">Firmware Management</div>
      <p style="color: var(--text-secondary); margin-bottom: 12px;">Update or change the autopilot firmware.</p>
      <div style="display: flex; gap: 10px;">
        <button class="btn btn-secondary"><i class="mdi mdi-download"></i> Update Firmware</button>
        <button class="btn btn-secondary"><i class="mdi mdi-upload"></i> Upload Custom</button>
      </div>
    </div>
  </div>
</template>
<script>
export default {
  name: 'VehicleView',
  methods: {
    async detect() { 
      try {
        const r = await fetch('/ardupilot-manager/v1.0/vehicle/detect')
        const d = await r.json()
        alert(d.detected ? `Detected: ${d.board.name}` : 'No FC found')
      } catch { alert('Service unavailable') }
    }
  }
}
</script>
<style scoped>
.info-grid { display: flex; flex-direction: column; gap: 12px; }
.info-item { display: flex; justify-content: space-between; align-items: center; padding: 8px 0; border-bottom: 1px solid var(--border-color); }
.info-label { color: var(--text-secondary); font-size: 0.85rem; }
</style>
