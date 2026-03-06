<template>
  <div class="page">
    <div class="page-header">
      <h1>MAVLink Endpoints</h1>
      <p>Configure MAVLink communication endpoints</p>
    </div>
    <div class="card fade-in" style="margin-bottom: 16px;">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
        <div class="card-title" style="margin-bottom: 0">Active Endpoints</div>
        <button class="btn btn-primary btn-sm" @click="showCreate = true"><i class="mdi mdi-plus"></i> Add Endpoint</button>
      </div>
      <table class="table">
        <thead><tr><th>Name</th><th>Type</th><th>Address</th><th>Status</th><th>Actions</th></tr></thead>
        <tbody>
          <tr v-for="ep in endpoints" :key="ep.name">
            <td><strong>{{ ep.name }}</strong></td>
            <td><span class="badge badge-info">{{ ep.type }}</span></td>
            <td style="font-family: monospace;">{{ ep.place }}</td>
            <td><span class="badge" :class="ep.enabled ? 'badge-success' : 'badge-danger'">{{ ep.enabled ? 'Active' : 'Disabled' }}</span></td>
            <td>
              <button class="btn btn-sm btn-secondary" @click="toggleEndpoint(ep)" :disabled="ep.protected">
                {{ ep.enabled ? 'Disable' : 'Enable' }}
              </button>
              <button class="btn btn-sm btn-danger" @click="deleteEndpoint(ep.name)" :disabled="ep.protected" style="margin-left: 6px;">
                <i class="mdi mdi-delete"></i>
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <!-- Create Dialog -->
    <div v-if="showCreate" class="modal-overlay" @click.self="showCreate = false">
      <div class="modal">
        <h3>New Endpoint</h3>
        <div class="form-group"><label>Name</label><input class="input" v-model="newEp.name" placeholder="My GCS"></div>
        <div class="form-group"><label>Type</label>
          <select class="input" v-model="newEp.type">
            <option value="udpclient">UDP Client</option><option value="udpserver">UDP Server</option>
            <option value="tcpclient">TCP Client</option><option value="tcpserver">TCP Server</option>
            <option value="serial">Serial</option>
          </select>
        </div>
        <div class="form-group"><label>Address</label><input class="input" v-model="newEp.place" placeholder="192.168.2.1:14550"></div>
        <div style="display: flex; gap: 10px; justify-content: flex-end; margin-top: 16px;">
          <button class="btn btn-secondary" @click="showCreate = false">Cancel</button>
          <button class="btn btn-primary" @click="createEndpoint">Create</button>
        </div>
      </div>
    </div>
  </div>
</template>
<script>
export default {
  name: 'EndpointsView',
  data() { return { endpoints: [], showCreate: false, newEp: { name: '', type: 'udpclient', place: '' } } },
  async mounted() { await this.fetch() },
  methods: {
    async fetch() { try { this.endpoints = await (await fetch('/ardupilot-manager/v1.0/endpoints')).json() } catch {} },
    async createEndpoint() {
      await fetch('/ardupilot-manager/v1.0/endpoints', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ ...this.newEp, enabled: true, persistent: true, protected: false }) })
      this.showCreate = false; this.newEp = { name: '', type: 'udpclient', place: '' }; await this.fetch()
    },
    async deleteEndpoint(name) { await fetch(`/ardupilot-manager/v1.0/endpoints/${name}`, { method: 'DELETE' }); await this.fetch() },
    toggleEndpoint(ep) { ep.enabled = !ep.enabled }
  }
}
</script>
<style scoped>
.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.6); display: flex; align-items: center; justify-content: center; z-index: 1000; backdrop-filter: blur(4px); }
.modal { background: var(--bg-card); border: 1px solid var(--border-color); border-radius: var(--radius-lg); padding: 28px; width: 420px; max-width: 90vw; }
.modal h3 { margin-bottom: 20px; }
.form-group { margin-bottom: 14px; }
.form-group label { display: block; font-size: 0.8rem; color: var(--text-secondary); margin-bottom: 6px; }
</style>
