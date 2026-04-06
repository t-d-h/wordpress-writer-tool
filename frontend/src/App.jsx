import { Routes, Route, Navigate } from 'react-router-dom'
import Layout from './components/Layout'
import Dashboard from './components/Dashboard'
import AIProviders from './components/Settings/AIProviders'
import WPSites from './components/Settings/WPSites'
import ProjectList from './components/Projects/ProjectList'
import ProjectDetail from './components/Projects/ProjectDetail'
import PostView from './components/Posts/PostView'

function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<Dashboard />} />
        <Route path="/settings/ai-providers" element={<AIProviders />} />
        <Route path="/settings/wp-sites" element={<WPSites />} />
        <Route path="/projects" element={<ProjectList />} />
        <Route path="/projects/:id" element={<ProjectDetail />} />
        <Route path="/posts/:id" element={<PostView />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  )
}

export default App
