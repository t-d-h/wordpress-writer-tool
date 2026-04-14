import { Routes, Route, Navigate } from 'react-router-dom'
import Layout from './components/Layout'
import AIProviders from './components/Settings/AIProviders'
import WPSites from './components/Settings/WPSites'
import DefaultModels from './components/Settings/DefaultModels'
import ProjectList from './components/Projects/ProjectList'
import ProjectDetail from './components/Projects/ProjectDetail'
import PostView from './components/Posts/PostView'
import AllPosts from './components/AllPosts'

function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<Navigate to="/projects" replace />} />
        <Route path="/settings/ai-providers" element={<AIProviders />} />
        <Route path="/settings/wp-sites" element={<WPSites />} />
        <Route path="/settings/default-models" element={<DefaultModels />} />
        <Route path="/projects" element={<ProjectList />} />
        <Route path="/projects/:id" element={<ProjectDetail />} />
        <Route path="/posts/:id" element={<PostView />} />
        <Route path="/all-posts" element={<AllPosts />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  )
}

export default App
