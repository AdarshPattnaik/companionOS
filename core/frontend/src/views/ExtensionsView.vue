<template>
  <div class="page">
    <div class="page-header"><h1>Extensions</h1><p>Install and manage Docker-based extensions</p></div>
    <div class="tabs fade-in">
      <button :class="{ active: tab === 'installed' }" @click="tab='installed'">Installed</button>
      <button :class="{ active: tab === 'store' }" @click="tab='store'; fetchStore()">Store</button>
      <button :class="{ active: tab === 'containers' }" @click="tab='containers'; fetchContainers()">Containers</button>
    </div>
    <div v-if="tab === 'installed'" class="grid grid-3 fade-in" style="margin-top:16px;">
      <div class="card ext-card" v-for="ext in installed" :key="ext.identifier">
        <div class="ext-icon"><i class="mdi mdi-puzzle" style="font-size:2rem;color:var(--coratia-primary)"></i></div>
        <h3>{{ ext.name }}</h3>
        <p>{{ ext.description }}</p>
        <div style="display:flex;gap:8px;margin-top:auto;">
          <button class="btn btn-sm btn-secondary" @click="toggleExt(ext)">{{ ext.enabled ? 'Disable' : 'Enable' }}</button>
          <button class="btn btn-sm btn-danger" @click="uninstall(ext.identifier)">Remove</button>
        </div>
      </div>
      <div v-if="!installed.length" class="card" style="text-align:center;padding:40px;grid-column:1/-1;">
        <i class="mdi mdi-puzzle-outline" style="font-size:3rem;color:var(--text-muted)"></i>
        <p style="color:var(--text-secondary);margin-top:12px;">No extensions installed. Browse the Store to add some!</p>
      </div>
    </div>
    <div v-if="tab === 'store'" class="grid grid-3 fade-in" style="margin-top:16px;">
      <div class="card ext-card" v-for="ext in store" :key="ext.identifier">
        <div class="ext-icon"><i class="mdi mdi-puzzle-plus" style="font-size:2rem;color:var(--coratia-accent)"></i></div>
        <h3>{{ ext.name }}</h3>
        <p>{{ ext.description }}</p>
        <div class="ext-meta"><span>By {{ ext.author }}</span><span>v{{ ext.version }}</span></div>
        <button class="btn btn-primary btn-sm" style="margin-top:auto;" @click="install(ext)"><i class="mdi mdi-download"></i> Install</button>
      </div>
    </div>
    <div v-if="tab === 'containers'" class="card fade-in" style="margin-top:16px;">
      <div class="card-title">Docker Containers</div>
      <table class="table">
        <thead><tr><th>Name</th><th>Image</th><th>Status</th></tr></thead>
        <tbody><tr v-for="c in containers" :key="c.name"><td>{{ c.name }}</td><td style="font-family:monospace;">{{ c.image }}</td><td><span class="badge" :class="c.status==='running'?'badge-success':'badge-warning'">{{ c.status }}</span></td></tr></tbody>
      </table>
    </div>
  </div>
</template>
<script>
export default {
  name: 'ExtensionsView',
  data() { return { tab: 'installed', installed: [], store: [], containers: [] } },
  async mounted() { try { this.installed = await (await fetch('/kraken/v1.0/extensions/installed')).json() } catch {} },
  methods: {
    async fetchStore() { try { this.store = await (await fetch('/kraken/v1.0/extensions/store')).json() } catch {} },
    async fetchContainers() { try { this.containers = await (await fetch('/kraken/v1.0/containers')).json() } catch {} },
    async install(ext) { await fetch('/kraken/v1.0/extensions/install', { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(ext) }); this.installed = await (await fetch('/kraken/v1.0/extensions/installed')).json() },
    async uninstall(id) { await fetch(`/kraken/v1.0/extensions/${id}`, {method:'DELETE'}); this.installed = await (await fetch('/kraken/v1.0/extensions/installed')).json() },
    async toggleExt(ext) { await fetch(`/kraken/v1.0/extensions/${ext.identifier}/${ext.enabled?'stop':'start'}`, {method:'POST'}); ext.enabled = !ext.enabled }
  }
}
</script>
<style scoped>
.tabs { display:flex; gap:4px; background:var(--bg-card); border-radius:var(--radius-sm); padding:4px; width:fit-content; }
.tabs button { padding:8px 20px; border:none; background:transparent; color:var(--text-secondary); border-radius:var(--radius-sm); cursor:pointer; font-family:inherit; font-weight:500; transition:all var(--transition-fast); }
.tabs button.active { background:var(--coratia-primary); color:white; }
.ext-card { display:flex; flex-direction:column; gap:8px; }
.ext-icon { width:48px; height:48px; background:var(--bg-base); border-radius:var(--radius-sm); display:flex; align-items:center; justify-content:center; }
.ext-card h3 { font-size:1rem; }
.ext-card p { font-size:0.85rem; color:var(--text-secondary); flex:1; }
.ext-meta { display:flex; justify-content:space-between; font-size:0.75rem; color:var(--text-muted); }
</style>
