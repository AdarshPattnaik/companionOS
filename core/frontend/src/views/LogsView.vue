<template>
  <div class="page">
    <div class="page-header"><h1>Logs</h1><p>System and MAVLink log viewer</p></div>
    <div class="grid grid-3 fade-in" style="margin-bottom:16px;">
      <div class="card log-card" v-for="log in logs" :key="log.name" @click="viewLog(log)">
        <div style="display:flex;align-items:center;gap:10px;">
          <i class="mdi mdi-file-document-outline" style="font-size:1.5rem;color:var(--coratia-primary)"></i>
          <div><strong>{{ log.name }}</strong><br><span style="font-size:0.75rem;color:var(--text-muted);">{{ formatSize(log.size_bytes) }}</span></div>
        </div>
        <div style="display:flex;gap:6px;margin-top:8px;">
          <button class="btn btn-sm btn-secondary" @click.stop="downloadLog(log)"><i class="mdi mdi-download"></i></button>
          <button class="btn btn-sm btn-danger" @click.stop="deleteLog(log)"><i class="mdi mdi-delete"></i></button>
        </div>
      </div>
    </div>
    <div v-if="viewingLog" class="card fade-in">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;">
        <div class="card-title" style="margin-bottom:0">{{ viewingLog }}</div>
        <button class="btn btn-sm btn-secondary" @click="viewingLog=null;logContent=[]">Close</button>
      </div>
      <div class="log-viewer"><pre>{{ logContent.join('') }}</pre></div>
    </div>
    <div v-if="!logs.length && !viewingLog" class="card fade-in" style="text-align:center;padding:40px;">
      <i class="mdi mdi-text-box-outline" style="font-size:3rem;color:var(--text-muted)"></i>
      <p style="color:var(--text-secondary);margin-top:12px;">No log files found.</p>
    </div>
  </div>
</template>
<script>
export default {
  name: 'LogsView',
  data() { return { logs: [], viewingLog: null, logContent: [] } },
  async mounted() { await this.fetchLogs() },
  methods: {
    async fetchLogs() { try { this.logs = await (await fetch('/log-manager/v1.0/logs')).json() } catch {} },
    async viewLog(log) { try { const d = await (await fetch(`/log-manager/v1.0/logs/${log.name}?lines=200`)).json(); this.logContent = d.lines || []; this.viewingLog = log.name } catch {} },
    downloadLog(log) { window.open(`/log-manager/v1.0/logs/${log.name}/download`) },
    async deleteLog(log) { if(confirm(`Delete ${log.name}?`)) { await fetch(`/log-manager/v1.0/logs/${log.name}`,{method:'DELETE'}); await this.fetchLogs() }},
    formatSize(b) { if(b<1024)return b+'B'; if(b<1048576)return (b/1024).toFixed(1)+'KB'; return (b/1048576).toFixed(1)+'MB' }
  }
}
</script>
<style scoped>
.log-card { cursor:pointer; transition:all var(--transition-fast); }
.log-card:hover { border-color:var(--coratia-primary); }
.log-viewer { background:var(--bg-base); border-radius:var(--radius-sm); padding:16px; max-height:400px; overflow-y:auto; }
.log-viewer pre { font-family:'JetBrains Mono','Fira Code',monospace; font-size:0.8rem; color:var(--text-secondary); white-space:pre-wrap; word-break:break-all; }
</style>
