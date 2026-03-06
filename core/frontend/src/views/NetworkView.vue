<template>
  <div class="page">
    <div class="page-header"><h1>Network</h1><p>WiFi and Ethernet configuration</p></div>
    <div class="grid grid-2 fade-in">
      <div class="card">
        <div class="card-title">WiFi</div>
        <div style="margin-bottom:12px;">
          <span class="badge" :class="wifi.connected?'badge-success':'badge-danger'">{{ wifi.connected ? `Connected: ${wifi.ssid}` : 'Disconnected' }}</span>
        </div>
        <button class="btn btn-primary btn-sm" @click="scanWifi" style="margin-bottom:12px;"><i class="mdi mdi-wifi-find"></i> Scan Networks</button>
        <div v-if="networks.length" class="network-list">
          <div class="network-item" v-for="n in networks" :key="n.ssid" @click="selectedNetwork = n">
            <i class="mdi mdi-wifi" :style="{ color: n.connected ? 'var(--status-success)' : 'var(--text-secondary)' }"></i>
            <span>{{ n.ssid }}</span>
            <span style="margin-left:auto;font-size:0.8rem;color:var(--text-muted);">{{ n.signal_strength }} dBm</span>
          </div>
        </div>
        <div v-if="selectedNetwork" style="margin-top:12px;padding:12px;background:var(--bg-base);border-radius:var(--radius-sm);">
          <strong>{{ selectedNetwork.ssid }}</strong>
          <input class="input" v-model="wifiPassword" placeholder="Password" type="password" style="margin:8px 0;">
          <button class="btn btn-primary btn-sm" @click="connectWifi">Connect</button>
        </div>
        <div style="margin-top:16px;padding-top:16px;border-top:1px solid var(--border-color);">
          <div class="card-title">Hotspot</div>
          <button class="btn btn-sm" :class="wifi.hotspot_active ? 'btn-danger' : 'btn-secondary'" @click="toggleHotspot">
            {{ wifi.hotspot_active ? 'Stop Hotspot' : 'Create Hotspot' }}
          </button>
        </div>
      </div>
      <div class="card">
        <div class="card-title">Ethernet</div>
        <div class="network-list">
          <div class="network-item" v-for="iface in ethernet" :key="iface.name">
            <i class="mdi mdi-ethernet" :style="{ color: iface.is_up ? 'var(--status-success)' : 'var(--text-muted)' }"></i>
            <div><strong>{{ iface.name }}</strong><br><span style="font-size:0.8rem;color:var(--text-secondary);">{{ iface.ip_address || 'No IP' }} · {{ iface.speed_mbps }} Mbps</span></div>
            <span class="badge" :class="iface.is_up ? 'badge-success' : 'badge-danger'" style="margin-left:auto;">{{ iface.is_up ? 'Up' : 'Down' }}</span>
          </div>
        </div>
        <div v-if="!ethernet.length" style="color:var(--text-secondary);margin-top:12px;">No ethernet interfaces detected.</div>
      </div>
    </div>
  </div>
</template>
<script>
export default {
  name: 'NetworkView',
  data() { return { wifi: { connected: false, ssid: '', hotspot_active: false }, networks: [], ethernet: [], selectedNetwork: null, wifiPassword: '' } },
  async mounted() {
    try { this.wifi = await (await fetch('/wifi-manager/v1.0/status')).json() } catch {}
    try { this.ethernet = await (await fetch('/cable-guy/v1.0/ethernet')).json() } catch {}
  },
  methods: {
    async scanWifi() { try { this.networks = await (await fetch('/wifi-manager/v1.0/scan')).json() } catch {} },
    async connectWifi() { if (!this.selectedNetwork) return; await fetch('/wifi-manager/v1.0/connect', { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({ssid:this.selectedNetwork.ssid,password:this.wifiPassword}) }); this.selectedNetwork=null; this.wifiPassword='' },
    async toggleHotspot() { if (this.wifi.hotspot_active) { await fetch('/wifi-manager/v1.0/hotspot',{method:'DELETE'}) } else { await fetch('/wifi-manager/v1.0/hotspot',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({ssid:'CoratiaOS-Hotspot',password:'coratiaos'})}) }; this.wifi.hotspot_active = !this.wifi.hotspot_active }
  }
}
</script>
<style scoped>
.network-list { display:flex; flex-direction:column; gap:4px; }
.network-item { display:flex; align-items:center; gap:12px; padding:10px 12px; background:var(--bg-base); border-radius:var(--radius-sm); cursor:pointer; transition:background var(--transition-fast); }
.network-item:hover { background:var(--bg-elevated); }
</style>
