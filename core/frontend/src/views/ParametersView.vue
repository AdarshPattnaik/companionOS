<template>
  <div class="page">
    <div class="page-header"><h1>Parameters</h1><p>Edit ArduPilot vehicle parameters</p></div>
    <div class="card fade-in">
      <div style="display:flex;gap:12px;margin-bottom:16px;"><input class="input" v-model="search" placeholder="Search parameters..." style="max-width:400px;"><button class="btn btn-secondary btn-sm" @click="fetchParams"><i class="mdi mdi-refresh"></i> Refresh</button></div>
      <table class="table">
        <thead><tr><th>Parameter</th><th>Value</th><th>Description</th><th>Action</th></tr></thead>
        <tbody>
          <tr v-for="(info, name) in filteredParams" :key="name">
            <td><strong style="font-family:monospace;color:var(--coratia-primary);">{{ name }}</strong></td>
            <td><input class="input" style="width:120px;" :value="info.value" @change="e => setParam(name, e.target.value)"></td>
            <td style="color:var(--text-secondary);font-size:0.85rem;">{{ info.description }}</td>
            <td><button class="btn btn-sm btn-primary" @click="setParam(name, info.value)">Save</button></td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
<script>
export default {
  name: 'ParametersView',
  data() { return { params: {}, search: '' } },
  computed: { filteredParams() { const s = this.search.toLowerCase(); return Object.fromEntries(Object.entries(this.params).filter(([k]) => k.toLowerCase().includes(s))) } },
  async mounted() { await this.fetchParams() },
  methods: {
    async fetchParams() { try { const d = await (await fetch('/ardupilot-manager/v1.0/parameters')).json(); this.params = d.parameters || {} } catch {} },
    setParam(name, val) { alert(`Set ${name} = ${val} (would send via MAVLink)`) }
  }
}
</script>
