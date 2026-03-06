<template>
  <div class="page terminal-page">
    <div class="page-header"><h1>Terminal</h1><p>Web-based terminal access</p></div>
    <div class="card terminal-card fade-in">
      <iframe :src="terminalUrl" class="terminal-frame" title="Web Terminal"></iframe>
    </div>
  </div>
</template>
<script>
export default {
  name: 'TerminalView',
  computed: {
    terminalUrl() { return `${window.location.protocol}//${window.location.hostname}:8088` }
  }
}
</script>
<style scoped>
.terminal-page { display:flex; flex-direction:column; height:100%; }
.terminal-card { flex:1; padding:0; overflow:hidden; }
.terminal-frame { width:100%; height:100%; min-height:500px; border:none; background:#000; border-radius:var(--radius-md); }
</style>
