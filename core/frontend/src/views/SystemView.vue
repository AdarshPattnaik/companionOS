<template>
  <div class="page">
    <div class="page-header"><h1>System Information</h1><p>Hardware monitoring and system diagnostics</p></div>
    <div class="grid grid-3 fade-in" style="margin-bottom:16px;">
      <div class="card"><div class="card-title">CPU</div><div class="big-stat">{{ cpu.usage_percent }}%</div><div class="info-row"><span>Frequency</span><span>{{ cpu.frequency_mhz.toFixed(0) }} MHz</span></div><div class="info-row"><span>Cores</span><span>{{ cpu.core_count }}</span></div><div class="info-row"><span>Temperature</span><span :style="{color: cpu.temperature > 70 ? 'var(--status-danger)' : 'var(--text-primary)'}">{{ cpu.temperature }}°C</span></div></div>
      <div class="card"><div class="card-title">Memory</div><div class="big-stat">{{ mem.usage_percent }}%</div><div class="info-row"><span>Total</span><span>{{ (mem.total_mb/1024).toFixed(1) }} GB</span></div><div class="info-row"><span>Used</span><span>{{ (mem.used_mb/1024).toFixed(1) }} GB</span></div><div class="info-row"><span>Available</span><span>{{ (mem.available_mb/1024).toFixed(1) }} GB</span></div></div>
      <div class="card"><div class="card-title">Disk</div><div class="big-stat">{{ disk.usage_percent }}%</div><div class="info-row"><span>Total</span><span>{{ disk.total_gb.toFixed(1) }} GB</span></div><div class="info-row"><span>Used</span><span>{{ disk.used_gb.toFixed(1) }} GB</span></div><div class="info-row"><span>Free</span><span>{{ disk.free_gb.toFixed(1) }} GB</span></div></div>
    </div>
    <div class="grid grid-2 fade-in">
      <div class="card">
        <div class="card-title">System</div>
        <div class="info-row"><span>Hostname</span><span>{{ sysInfo.hostname }}</span></div>
        <div class="info-row"><span>Platform</span><span>{{ sysInfo.platform }} {{ sysInfo.architecture }}</span></div>
        <div class="info-row"><span>Kernel</span><span>{{ sysInfo.kernel }}</span></div>
        <div class="info-row"><span>Uptime</span><span>{{ formatUptime(sysInfo.uptime) }}</span></div>
        <div class="info-row"><span>CoratiaOS</span><span>{{ sysInfo.coratiaos_version }}</span></div>
      </div>
      <div class="card">
        <div class="card-title">Top Processes</div>
        <table class="table" style="font-size:0.8rem;">
          <thead><tr><th>Process</th><th>CPU%</th><th>Mem (MB)</th></tr></thead>
          <tbody><tr v-for="p in processes.slice(0,8)" :key="p.pid"><td>{{ p.name }}</td><td>{{ p.cpu_percent.toFixed(1) }}</td><td>{{ p.memory_mb.toFixed(1) }}</td></tr></tbody>
        </table>
      </div>
    </div>
  </div>
</template>
<script>
export default {
  name: 'SystemView',
  data() { return { cpu: {usage_percent:0,frequency_mhz:0,core_count:0,temperature:0}, mem: {total_mb:0,used_mb:0,available_mb:0,usage_percent:0}, disk: {total_gb:0,used_gb:0,free_gb:0,usage_percent:0}, sysInfo: {hostname:'',platform:'',architecture:'',kernel:'',uptime:0,coratiaos_version:''}, processes: [] }},
  async mounted() { await this.fetchAll(); this.interval = setInterval(() => this.fetchAll(), 5000) },
  beforeUnmount() { clearInterval(this.interval) },
  methods: {
    async fetchAll() { try { const [c,m,d,s,p] = await Promise.all([fetch('/helper/v1.0/system/cpu').then(r=>r.json()),fetch('/helper/v1.0/system/memory').then(r=>r.json()),fetch('/helper/v1.0/system/disk').then(r=>r.json()),fetch('/helper/v1.0/system/info').then(r=>r.json()),fetch('/helper/v1.0/system/processes').then(r=>r.json())]); this.cpu=c;this.mem=m;this.disk=d;this.sysInfo=s;this.processes=p } catch {} },
    formatUptime(s) { const h=Math.floor(s/3600); const m=Math.floor((s%3600)/60); return `${h}h ${m}m` }
  }
}
</script>
<style scoped>
.big-stat { font-size:2.5rem; font-weight:700; color:var(--coratia-primary); margin:8px 0; }
.info-row {display:flex;justify-content:space-between;padding:6px 0;border-bottom:1px solid var(--border-color);font-size:0.85rem;}
.info-row span:first-child {color:var(--text-secondary);}
</style>
