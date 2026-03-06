<template>
  <div class="page">
    <div class="page-header"><h1>Version Manager</h1><p>Update CoratiaOS and manage versions</p></div>
    <div class="card fade-in" style="margin-bottom:16px;">
      <div class="card-title">Current Version</div>
      <div style="display:flex;align-items:center;gap:16px;">
        <div class="version-badge"><i class="mdi mdi-check-circle" style="color:var(--status-success);font-size:2rem;"></i></div>
        <div>
          <div style="font-size:1.25rem;font-weight:700;">CoratiaOS {{ current.version }}</div>
          <div style="color:var(--text-secondary);font-size:0.85rem;">Tag: {{ current.tag }} · SHA: {{ current.sha }}</div>
          <div style="color:var(--text-muted);font-size:0.8rem;">Built: {{ current.build_date }}</div>
        </div>
        <div style="margin-left:auto;display:flex;gap:8px;">
          <button class="btn btn-secondary" @click="restart"><i class="mdi mdi-restart"></i> Restart</button>
          <button class="btn btn-primary" @click="checkUpdates"><i class="mdi mdi-update"></i> Check Updates</button>
        </div>
      </div>
    </div>
    <div class="grid grid-2 fade-in">
      <div class="card">
        <div class="card-title">Available Versions</div>
        <div class="version-list">
          <div class="version-item" v-for="v in remote" :key="v.tag">
            <div><strong>{{ v.repository }}</strong><br><span style="color:var(--text-secondary);font-size:0.8rem;">{{ v.tag }}</span></div>
            <button class="btn btn-sm btn-primary" @click="update(v.tag)"><i class="mdi mdi-download"></i> Update</button>
          </div>
        </div>
      </div>
      <div class="card">
        <div class="card-title">Local Versions</div>
        <div class="version-list">
          <div class="version-item" v-for="v in local" :key="v.tag">
            <div><strong>{{ v.repository }}</strong><br><span style="color:var(--text-secondary);font-size:0.8rem;">{{ v.tag }}</span></div>
            <span v-if="v.is_current" class="badge badge-success">Current</span>
            <button v-else class="btn btn-sm btn-secondary" @click="update(v.tag)">Switch</button>
          </div>
        </div>
        <button class="btn btn-secondary" style="margin-top:12px;" @click="rollback"><i class="mdi mdi-undo"></i> Rollback</button>
      </div>
    </div>
  </div>
</template>
<script>
export default {
  name: 'VersionView',
  data() { return { current: { version:'', tag:'', sha:'', build_date:'' }, local: [], remote: [] } },
  async mounted() {
    try { this.current = await (await fetch('/version-chooser/v1.0/version/current')).json() } catch {}
    try { this.local = await (await fetch('/version-chooser/v1.0/version/local')).json() } catch {}
    try { this.remote = await (await fetch('/version-chooser/v1.0/version/remote')).json() } catch {}
  },
  methods: {
    async update(tag) { if(confirm(`Update to ${tag}?`)) { await fetch(`/version-chooser/v1.0/version/update/${tag}`,{method:'POST'}); alert('Update initiated. System will restart.') }},
    async rollback() { if(confirm('Rollback to previous version?')) { await fetch('/version-chooser/v1.0/version/rollback',{method:'POST'}); alert('Rollback initiated.') }},
    async restart() { if(confirm('Restart CoratiaOS?')) { await fetch('/version-chooser/v1.0/version/restart',{method:'POST'}) }},
    async checkUpdates() { try { this.remote = await (await fetch('/version-chooser/v1.0/version/remote')).json(); alert(`Found ${this.remote.length} available versions.`) } catch { alert('Failed to check for updates.') }}
  }
}
</script>
<style scoped>
.version-badge { width:48px;height:48px;background:var(--bg-base);border-radius:var(--radius-md);display:flex;align-items:center;justify-content:center; }
.version-list { display:flex;flex-direction:column;gap:4px; }
.version-item { display:flex;align-items:center;justify-content:space-between;padding:10px 12px;background:var(--bg-base);border-radius:var(--radius-sm);transition:background var(--transition-fast); }
.version-item:hover { background:var(--bg-elevated); }
</style>
