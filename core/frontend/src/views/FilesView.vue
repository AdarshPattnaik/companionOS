<template>
  <div class="page">
    <div class="page-header"><h1>File Browser</h1><p>Browse and manage mission files, logs, and data</p></div>
    <div class="card fade-in">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;">
        <div style="display:flex;align-items:center;gap:8px;">
          <button class="btn btn-sm btn-secondary" @click="navigateUp" :disabled="currentPath==='/'"><i class="mdi mdi-arrow-up"></i></button>
          <span style="font-family:monospace;color:var(--text-secondary);font-size:0.9rem;">{{ currentPath }}</span>
        </div>
        <div style="display:flex;gap:8px;">
          <button class="btn btn-sm btn-secondary" @click="showMkdir=true"><i class="mdi mdi-folder-plus"></i> New Folder</button>
          <label class="btn btn-sm btn-primary" style="cursor:pointer;"><i class="mdi mdi-upload"></i> Upload<input type="file" @change="uploadFile" style="display:none;"></label>
        </div>
      </div>
      <div class="file-list">
        <div class="file-item" v-for="f in files" :key="f.path" @click="f.is_directory ? navigate(f.path) : null" :class="{ clickable: f.is_directory }">
          <i class="mdi" :class="f.is_directory ? 'mdi-folder' : 'mdi-file-outline'" :style="{ color: f.is_directory ? 'var(--status-warning)' : 'var(--text-secondary)' }"></i>
          <span class="file-name">{{ f.name }}</span>
          <span class="file-size">{{ f.is_directory ? '' : formatSize(f.size_bytes) }}</span>
          <div class="file-actions">
            <button v-if="!f.is_directory" class="btn btn-sm btn-secondary" @click.stop="download(f)"><i class="mdi mdi-download"></i></button>
            <button class="btn btn-sm btn-danger" @click.stop="deleteFile(f)"><i class="mdi mdi-delete"></i></button>
          </div>
        </div>
        <div v-if="!files.length" style="text-align:center;padding:40px;color:var(--text-secondary);">
          <i class="mdi mdi-folder-open-outline" style="font-size:3rem;color:var(--text-muted)"></i>
          <p style="margin-top:8px;">This directory is empty</p>
        </div>
      </div>
    </div>
    <div v-if="showMkdir" class="modal-overlay" @click.self="showMkdir=false">
      <div class="modal"><h3>Create Folder</h3><input class="input" v-model="newDirName" placeholder="Folder name"><div style="display:flex;gap:8px;justify-content:flex-end;margin-top:12px;"><button class="btn btn-secondary" @click="showMkdir=false">Cancel</button><button class="btn btn-primary" @click="mkdir">Create</button></div></div>
    </div>
  </div>
</template>
<script>
export default {
  name: 'FilesView',
  data() { return { files: [], currentPath: '/', showMkdir: false, newDirName: '' } },
  async mounted() { await this.fetchFiles() },
  methods: {
    async fetchFiles() { try { this.files = await (await fetch(`/file-browser/v1.0/files?path=${this.currentPath}`)).json() } catch {} },
    navigate(path) { this.currentPath = '/' + path; this.fetchFiles() },
    navigateUp() { const parts = this.currentPath.split('/').filter(Boolean); parts.pop(); this.currentPath = '/' + parts.join('/'); this.fetchFiles() },
    download(f) { window.open(`/file-browser/v1.0/files/download?path=${f.path}`) },
    async deleteFile(f) { if(confirm(`Delete ${f.name}?`)) { await fetch(`/file-browser/v1.0/files?path=${f.path}`,{method:'DELETE'}); await this.fetchFiles() }},
    async mkdir() { if(!this.newDirName) return; await fetch(`/file-browser/v1.0/files/mkdir?path=${this.currentPath}/${this.newDirName}`,{method:'POST'}); this.showMkdir=false; this.newDirName=''; await this.fetchFiles() },
    async uploadFile(e) { const file = e.target.files[0]; if(!file) return; const fd = new FormData(); fd.append('file', file); await fetch(`/file-browser/v1.0/files/upload?path=${this.currentPath}`,{method:'POST',body:fd}); await this.fetchFiles() },
    formatSize(b) { if(b<1024)return b+'B'; if(b<1048576)return (b/1024).toFixed(1)+'KB'; return (b/1048576).toFixed(1)+'MB' }
  }
}
</script>
<style scoped>
.file-list { display:flex; flex-direction:column; }
.file-item { display:flex; align-items:center; gap:12px; padding:10px 12px; border-bottom:1px solid var(--border-color); transition:background var(--transition-fast); }
.file-item:hover { background:var(--bg-card-hover); }
.file-item.clickable { cursor:pointer; }
.file-name { flex:1; font-weight:500; }
.file-size { color:var(--text-muted); font-size:0.8rem; width:80px; text-align:right; }
.file-actions { display:flex; gap:4px; }
.modal-overlay { position:fixed;inset:0;background:rgba(0,0,0,0.6);display:flex;align-items:center;justify-content:center;z-index:1000;backdrop-filter:blur(4px); }
.modal { background:var(--bg-card);border:1px solid var(--border-color);border-radius:var(--radius-lg);padding:28px;width:380px; }
.modal h3 { margin-bottom:16px; }
</style>
