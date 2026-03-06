import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/', name: 'Dashboard', component: () => import('../views/DashboardView.vue'), meta: { icon: 'mdi-view-dashboard', label: 'Dashboard' } },
  { path: '/vehicle', name: 'Vehicle', component: () => import('../views/VehicleView.vue'), meta: { icon: 'mdi-submarine', label: 'Vehicle Setup' } },
  { path: '/endpoints', name: 'Endpoints', component: () => import('../views/EndpointsView.vue'), meta: { icon: 'mdi-lan-connect', label: 'Endpoints' } },
  { path: '/video', name: 'Video', component: () => import('../views/VideoView.vue'), meta: { icon: 'mdi-video', label: 'Video' } },
  { path: '/parameters', name: 'Parameters', component: () => import('../views/ParametersView.vue'), meta: { icon: 'mdi-tune-vertical', label: 'Parameters' } },
  { path: '/extensions', name: 'Extensions', component: () => import('../views/ExtensionsView.vue'), meta: { icon: 'mdi-puzzle', label: 'Extensions' } },
  { path: '/network', name: 'Network', component: () => import('../views/NetworkView.vue'), meta: { icon: 'mdi-wifi', label: 'Network' } },
  { path: '/system', name: 'System', component: () => import('../views/SystemView.vue'), meta: { icon: 'mdi-chip', label: 'System' } },
  { path: '/logs', name: 'Logs', component: () => import('../views/LogsView.vue'), meta: { icon: 'mdi-text-box-outline', label: 'Logs' } },
  { path: '/files', name: 'Files', component: () => import('../views/FilesView.vue'), meta: { icon: 'mdi-folder-outline', label: 'Files' } },
  { path: '/terminal', name: 'Terminal', component: () => import('../views/TerminalView.vue'), meta: { icon: 'mdi-console', label: 'Terminal' } },
  { path: '/version', name: 'Version', component: () => import('../views/VersionView.vue'), meta: { icon: 'mdi-update', label: 'Version' } },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
export { routes }
