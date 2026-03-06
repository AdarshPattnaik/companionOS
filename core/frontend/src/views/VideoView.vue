<template>
  <div class="page">
    <div class="page-header"><h1>Video Manager</h1><p>Camera feeds and video stream configuration</p></div>
    <div class="grid grid-2 fade-in" style="margin-bottom: 16px;">
      <div class="card" v-for="stream in streams" :key="stream.name">
        <div class="video-preview"><i class="mdi mdi-video-off" style="font-size: 3rem; color: var(--text-muted);"></i><span style="color: var(--text-secondary);">Stream: {{ stream.name }}</span></div>
        <div style="margin-top: 12px;">
          <div class="info-row"><span>Source</span><span style="font-family: monospace;">{{ stream.source }}</span></div>
          <div class="info-row"><span>Resolution</span><span>{{ stream.width }}×{{ stream.height }}</span></div>
          <div class="info-row"><span>Codec</span><span class="badge badge-info">{{ stream.codec }}</span></div>
          <div class="info-row"><span>Bitrate</span><span>{{ stream.bitrate }} kbps</span></div>
          <div class="info-row"><span>FPS</span><span>{{ stream.framerate }}</span></div>
        </div>
        <div style="display: flex; gap: 8px; margin-top: 12px;"><button class="btn btn-sm btn-secondary">Configure</button><button class="btn btn-sm btn-danger" @click="deleteStream(stream.name)">Remove</button></div>
      </div>
    </div>
    <div class="card fade-in">
      <div class="card-title">Cameras Detected</div>
      <button class="btn btn-primary btn-sm" @click="detectCameras" style="margin-bottom: 12px;"><i class="mdi mdi-magnify"></i> Scan</button>
      <div v-if="cameras.length" class="camera-list">
        <div class="camera-item" v-for="cam in cameras" :key="cam.device">
          <i class="mdi mdi-camera" style="color: var(--coratia-primary);"></i>
          <div><strong>{{ cam.name }}</strong><br><span style="color: var(--text-secondary); font-size: 0.8rem;">{{ cam.device }} ({{ cam.source_type }})</span></div>
          <button class="btn btn-sm btn-primary" @click="addStream(cam)">+ Stream</button>
        </div>
      </div>
      <p v-else style="color: var(--text-secondary);">No cameras detected. Click scan to search.</p>
    </div>
  </div>
</template>
<script>
export default {
  name: 'VideoView',
  data() { return { streams: [], cameras: [] } },
  async mounted() { try { this.streams = await (await fetch('/video/v1.0/streams')).json() } catch {} },
  methods: {
    async detectCameras() { try { this.cameras = await (await fetch('/video/v1.0/cameras')).json() } catch {} },
    async addStream(cam) { await fetch('/video/v1.0/streams', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ name: cam.name, source: cam.device, width: 1280, height: 720, bitrate: 5000, framerate: 30, codec: 'h264', endpoint: 'rtsp://0.0.0.0:8554/video0', enabled: true }) }); this.streams = await (await fetch('/video/v1.0/streams')).json() },
    async deleteStream(name) { await fetch(`/video/v1.0/streams/${name}`, { method: 'DELETE' }); this.streams = await (await fetch('/video/v1.0/streams')).json() }
  }
}
</script>
<style scoped>
.video-preview { height: 180px; background: var(--bg-base); border-radius: var(--radius-sm); display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 8px; }
.info-row { display: flex; justify-content: space-between; padding: 6px 0; border-bottom: 1px solid var(--border-color); font-size: 0.85rem; }
.camera-list { display: flex; flex-direction: column; gap: 8px; }
.camera-item { display: flex; align-items: center; gap: 12px; padding: 12px; background: var(--bg-base); border-radius: var(--radius-sm); }
.camera-item button { margin-left: auto; }
</style>
