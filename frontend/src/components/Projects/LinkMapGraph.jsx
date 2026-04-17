import { useRef, useEffect, useState, useCallback } from 'react'
import PropTypes from 'prop-types'

/**
 * LinkMapGraph — Canvas-based force-directed graph visualization
 * Shows internal (post-to-post) and external (post-to-website) links
 */
export default function LinkMapGraph({ nodes, edges }) {
  const canvasRef = useRef(null)
  const containerRef = useRef(null)
  const animFrameRef = useRef(null)
  const simRef = useRef(null)
  const [tooltip, setTooltip] = useState(null)
  const [dimensions, setDimensions] = useState({ width: 900, height: 600 })
  const positionsRef = useRef({}) // Store { id: {x, y, vx, vy} }
  const viewStateRef = useRef({ zoom: 1, panX: 0, panY: 0 })
  const lastDownRef = useRef({ x: 0, y: 0, time: 0 })

  // Initialize simulation data
  const initSimulation = useCallback(() => {
    if (!nodes || nodes.length === 0) return null
    if (dimensions.width <= 0 || dimensions.height <= 0) return null

    const w = dimensions.width
    const h = dimensions.height

    const simNodes = nodes.map((node, i) => {
      const isPost = node.type === 'post'
      const prevPos = positionsRef.current[node.id]
      
      if (prevPos) {
        return {
          ...node,
          x: prevPos.x,
          y: prevPos.y,
          vx: prevPos.vx || 0,
          vy: prevPos.vy || 0,
          radius: isPost ? 28 : 16,
        }
      }

      // Initial placement if no previous pos
      const angle = (i / nodes.length) * Math.PI * 2
      const radius = isPost ? Math.min(w, h) * 0.2 : Math.min(w, h) * 0.35
      return {
        ...node,
        x: w / 2 + Math.cos(angle) * radius + (Math.random() - 0.5) * 40,
        y: h / 2 + Math.sin(angle) * radius + (Math.random() - 0.5) * 40,
        vx: 0,
        vy: 0,
        radius: isPost ? 28 : 16,
      }
    })

    const nodeMap = {}
    simNodes.forEach(n => { nodeMap[n.id] = n })

    const simEdges = edges
      .filter(e => nodeMap[e.source] && nodeMap[e.target])
      .map(e => ({
        source: nodeMap[e.source],
        target: nodeMap[e.target],
        type: e.type,
      }))

    return {
      nodes: simNodes,
      edges: simEdges,
      nodeMap,
      dragging: null,
      offsetX: 0,
      offsetY: 0,
      zoom: viewStateRef.current.zoom,
      panX: viewStateRef.current.panX,
      panY: viewStateRef.current.panY,
      isPanning: false,
      panStartX: 0,
      panStartY: 0,
      coolingFactor: 1.0,
    }
  }, [nodes, edges, dimensions])

  // Force simulation step
  const simulate = useCallback((sim) => {
    if (!sim || sim.coolingFactor < 0.01) return

    const alpha = 0.3 * sim.coolingFactor
    const repulsion = 4000
    const springLen = 140
    const springK = 0.006
    const centerK = 0.012
    const damping = 0.8
    const w = dimensions.width
    const h = dimensions.height

    // Repulsion between all nodes
    for (let i = 0; i < sim.nodes.length; i++) {
      for (let j = i + 1; j < sim.nodes.length; j++) {
        const a = sim.nodes[i]
        const b = sim.nodes[j]
        let dx = b.x - a.x
        let dy = b.y - a.y
        let dist = Math.sqrt(dx * dx + dy * dy) || 1
        const force = repulsion / (dist * dist)
        const fx = (dx / dist) * force * alpha
        const fy = (dy / dist) * force * alpha
        a.vx -= fx
        a.vy -= fy
        b.vx += fx
        b.vy += fy
      }
    }

    // Spring forces along edges
    for (const edge of sim.edges) {
      const a = edge.source
      const b = edge.target
      let dx = b.x - a.x
      let dy = b.y - a.y
      let dist = Math.sqrt(dx * dx + dy * dy) || 1
      const displacement = dist - springLen
      const force = springK * displacement * alpha
      const fx = (dx / dist) * force
      const fy = (dy / dist) * force
      a.vx += fx
      a.vy += fy
      b.vx -= fx
      b.vy -= fy
    }

    // Center gravity
    for (const node of sim.nodes) {
      node.vx += (w / 2 - node.x) * centerK * alpha
      node.vy += (h / 2 - node.y) * centerK * alpha
    }

    // Update positions
    for (const node of sim.nodes) {
      if (sim.dragging === node) continue
      node.vx *= damping
      node.vy *= damping
      node.x += node.vx
      node.y += node.vy
      // Bounds
      // Bounds with graceful margin
      const margin = 50
      node.x = Math.max(-margin, Math.min(w + margin, node.x))
      node.y = Math.max(-margin, Math.min(h + margin, node.y))
      
      // Save pos to ref
      positionsRef.current[node.id] = { x: node.x, y: node.y, vx: node.vx, vy: node.vy }
    }

    sim.coolingFactor *= 0.995
  }, [dimensions])

  // Draw function
  const draw = useCallback((ctx, sim) => {
    if (!sim) return
    const w = dimensions.width
    const h = dimensions.height

    ctx.clearRect(0, 0, w, h)
    ctx.save()
    ctx.translate(sim.panX, sim.panY)
    ctx.scale(sim.zoom, sim.zoom)

    // Draw edges
    for (const edge of sim.edges) {
      const { source: s, target: t, type } = edge
      ctx.beginPath()
      ctx.moveTo(s.x, s.y)
      ctx.lineTo(t.x, t.y)

      if (type === 'internal') {
        ctx.strokeStyle = 'rgba(108, 92, 231, 0.5)'
        ctx.lineWidth = 2
        ctx.setLineDash([])
      } else {
        ctx.strokeStyle = 'rgba(0, 206, 201, 0.35)'
        ctx.lineWidth = 1.5
        ctx.setLineDash([6, 4])
      }
      ctx.stroke()
      ctx.setLineDash([])

      // Draw arrow
      const angle = Math.atan2(t.y - s.y, t.x - s.x)
      const arrowDist = t.radius + 6
      const ax = t.x - Math.cos(angle) * arrowDist
      const ay = t.y - Math.sin(angle) * arrowDist
      const arrowSize = type === 'internal' ? 8 : 6

      ctx.beginPath()
      ctx.moveTo(ax, ay)
      ctx.lineTo(
        ax - arrowSize * Math.cos(angle - Math.PI / 6),
        ay - arrowSize * Math.sin(angle - Math.PI / 6)
      )
      ctx.lineTo(
        ax - arrowSize * Math.cos(angle + Math.PI / 6),
        ay - arrowSize * Math.sin(angle + Math.PI / 6)
      )
      ctx.closePath()
      ctx.fillStyle = type === 'internal' ? 'rgba(108, 92, 231, 0.7)' : 'rgba(0, 206, 201, 0.5)'
      ctx.fill()
    }

    // Draw nodes
    for (const node of sim.nodes) {
      if (node.type === 'post') {
        // Rounded rectangle for posts
        const rw = node.radius * 2.2
        const rh = node.radius * 1.4
        const rx = node.x - rw / 2
        const ry = node.y - rh / 2
        const r = 8

        ctx.beginPath()
        ctx.moveTo(rx + r, ry)
        ctx.lineTo(rx + rw - r, ry)
        ctx.quadraticCurveTo(rx + rw, ry, rx + rw, ry + r)
        ctx.lineTo(rx + rw, ry + rh - r)
        ctx.quadraticCurveTo(rx + rw, ry + rh, rx + rw - r, ry + rh)
        ctx.lineTo(rx + r, ry + rh)
        ctx.quadraticCurveTo(rx, ry + rh, rx, ry + rh - r)
        ctx.lineTo(rx, ry + r)
        ctx.quadraticCurveTo(rx, ry, rx + r, ry)
        ctx.closePath()

        // Gradient fill
        const grad = ctx.createLinearGradient(rx, ry, rx + rw, ry + rh)
        grad.addColorStop(0, 'rgba(108, 92, 231, 0.85)')
        grad.addColorStop(1, 'rgba(162, 155, 254, 0.85)')
        ctx.fillStyle = grad
        ctx.fill()
        ctx.strokeStyle = 'rgba(108, 92, 231, 0.9)'
        ctx.lineWidth = 1.5
        ctx.stroke()

        // Label
        const label = (node.title || '').length > 12
          ? node.title.substring(0, 11) + '…'
          : (node.title || '')
        ctx.fillStyle = '#ffffff'
        ctx.font = 'bold 10px Inter, sans-serif'
        ctx.textAlign = 'center'
        ctx.textBaseline = 'middle'
        ctx.fillText(label, node.x, node.y)
      } else {
        // Circle for external
        ctx.beginPath()
        ctx.arc(node.x, node.y, node.radius, 0, Math.PI * 2)
        const grad = ctx.createRadialGradient(node.x, node.y, 0, node.x, node.y, node.radius)
        grad.addColorStop(0, 'rgba(0, 206, 201, 0.7)')
        grad.addColorStop(1, 'rgba(0, 206, 201, 0.4)')
        ctx.fillStyle = grad
        ctx.fill()
        ctx.strokeStyle = 'rgba(0, 206, 201, 0.8)'
        ctx.lineWidth = 1
        ctx.stroke()

        // Label
        const label = (node.title || '').length > 10
          ? node.title.substring(0, 9) + '…'
          : (node.title || '')
        ctx.fillStyle = '#ffffff'
        ctx.font = '9px Inter, sans-serif'
        ctx.textAlign = 'center'
        ctx.textBaseline = 'middle'
        ctx.fillText(label, node.x, node.y)
      }
    }

    ctx.restore()
  }, [dimensions])

  // Resize observer
  useEffect(() => {
    const container = containerRef.current
    if (!container) return
    const observer = new ResizeObserver(entries => {
      for (const entry of entries) {
        const { width, height } = entry.contentRect
        if (width > 0 && height > 0) {
          setDimensions({ width: Math.floor(width), height: Math.max(500, Math.floor(height)) })
        }
      }
    })
    observer.observe(container)
    return () => observer.disconnect()
  }, [])

  // Main effect — set up simulation and animation loop
  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return
    const ctx = canvas.getContext('2d')

    const sim = initSimulation()
    simRef.current = sim

    if (!sim) {
      ctx.clearRect(0, 0, dimensions.width, dimensions.height)
      return
    }

    // Reset cooling on new data
    sim.coolingFactor = 1.0

    const tick = () => {
      simulate(sim)
      draw(ctx, sim)
      animFrameRef.current = requestAnimationFrame(tick)
    }

    // Run intense simulation first to settle layout
    for (let i = 0; i < 100; i++) {
      simulate(sim)
    }

    animFrameRef.current = requestAnimationFrame(tick)

    return () => {
      if (animFrameRef.current) cancelAnimationFrame(animFrameRef.current)
    }
  }, [initSimulation, simulate, draw, dimensions])

  // Mouse interaction handlers
  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return

    const getMousePos = (e) => {
      const rect = canvas.getBoundingClientRect()
      const sim = simRef.current
      if (!sim) return { x: 0, y: 0 }
      return {
        x: (e.clientX - rect.left - sim.panX) / sim.zoom,
        y: (e.clientY - rect.top - sim.panY) / sim.zoom,
      }
    }

    const findNode = (x, y) => {
      const sim = simRef.current
      if (!sim) return null
      // Reverse iterate so top nodes are hit first
      for (let i = sim.nodes.length - 1; i >= 0; i--) {
        const n = sim.nodes[i]
        const dx = x - n.x
        const dy = y - n.y
        const hitRadius = n.type === 'post' ? n.radius * 1.2 : n.radius
        if (dx * dx + dy * dy < hitRadius * hitRadius) return n
      }
      return null
    }

    const onMouseDown = (e) => {
      const sim = simRef.current
      if (!sim) return
      
      lastDownRef.current = { x: e.clientX, y: e.clientY, time: Date.now() }
      
      const { x, y } = getMousePos(e)
      const node = findNode(x, y)
      if (node) {
        sim.dragging = node
        sim.offsetX = x - node.x
        sim.offsetY = y - node.y
        sim.coolingFactor = 0.3  // reheat slightly
        canvas.style.cursor = 'grabbing'
      } else {
        // Pan
        sim.isPanning = true
        sim.panStartX = e.clientX - sim.panX
        sim.panStartY = e.clientY - sim.panY
        canvas.style.cursor = 'move'
      }
    }

    const onMouseMove = (e) => {
      const sim = simRef.current
      if (!sim) return

      if (sim.dragging) {
        const { x, y } = getMousePos(e)
        sim.dragging.x = x - sim.offsetX
        sim.dragging.y = y - sim.offsetY
        sim.dragging.vx = 0
        sim.dragging.vy = 0
      } else if (sim.isPanning) {
        sim.panX = e.clientX - sim.panStartX
        sim.panY = e.clientY - sim.panStartY
        // Persist view state
        viewStateRef.current.panX = sim.panX
        viewStateRef.current.panY = sim.panY
      } else {
        // Tooltip
        const { x, y } = getMousePos(e)
        const node = findNode(x, y)
        if (node) {
          const rect = canvas.getBoundingClientRect()
          setTooltip({
            x: e.clientX - rect.left,
            y: e.clientY - rect.top - 10,
            title: node.title,
            url: node.url,
            type: node.type,
          })
          canvas.style.cursor = 'pointer'
        } else {
          setTooltip(null)
          canvas.style.cursor = 'default'
        }
      }
    }

    const onMouseUp = (e) => {
      const sim = simRef.current
      if (!sim) return

      // Detect click vs drag
      const dx = e.clientX - lastDownRef.current.x
      const dy = e.clientY - lastDownRef.current.y
      const dist = Math.sqrt(dx * dx + dy * dy)
      const time = Date.now() - lastDownRef.current.time

      if (dist < 5 && time < 300) {
        // This was a click, not a significant drag
        const { x, y } = getMousePos(e)
        const node = findNode(x, y)
        if (node && node.url) {
          window.open(node.url, '_blank')
        }
      }

      sim.dragging = null
      sim.isPanning = false
      canvas.style.cursor = 'default'
    }

    const onWheel = (e) => {
      e.preventDefault()
      const sim = simRef.current
      if (!sim) return
      const delta = e.deltaY > 0 ? 0.9 : 1.1
      const newZoom = Math.max(0.3, Math.min(3, sim.zoom * delta))

      // Zoom toward mouse position
      const rect = canvas.getBoundingClientRect()
      const mx = e.clientX - rect.left
      const my = e.clientY - rect.top

      sim.panX = mx - (mx - sim.panX) * (newZoom / sim.zoom)
      sim.panY = my - (my - sim.panY) * (newZoom / sim.zoom)
      sim.zoom = newZoom

      // Persist view state
      viewStateRef.current.panX = sim.panX
      viewStateRef.current.panY = sim.panY
      viewStateRef.current.zoom = sim.zoom
    }

    const onDblClick = (e) => {
      const sim = simRef.current
      if (!sim) return
      const { x, y } = getMousePos(e)
      const node = findNode(x, y)
      if (node && node.url) {
        window.open(node.url, '_blank')
      }
    }

    canvas.addEventListener('mousedown', onMouseDown)
    canvas.addEventListener('mousemove', onMouseMove)
    canvas.addEventListener('mouseup', onMouseUp)
    canvas.addEventListener('mouseleave', onMouseUp)
    canvas.addEventListener('wheel', onWheel, { passive: false })
    canvas.addEventListener('dblclick', onDblClick)

    return () => {
      canvas.removeEventListener('mousedown', onMouseDown)
      canvas.removeEventListener('mousemove', onMouseMove)
      canvas.removeEventListener('mouseup', onMouseUp)
      canvas.removeEventListener('mouseleave', onMouseUp)
      canvas.removeEventListener('wheel', onWheel)
      canvas.removeEventListener('dblclick', onDblClick)
    }
  }, [])

  if (!nodes || nodes.length === 0) {
    return (
      <div className="empty-state">
        <div className="empty-state-icon">🔗</div>
        <div className="empty-state-title">No Link Data</div>
        <div className="empty-state-text">Click Refresh to scan your published posts for links</div>
      </div>
    )
  }

  return (
    <div className="link-map-container">
      <div className="link-map-legend">
        <div className="link-map-legend-item">
          <span className="link-map-legend-dot" style={{ background: 'var(--accent-primary)' }} />
          <span>Post (internal)</span>
        </div>
        <div className="link-map-legend-item">
          <span className="link-map-legend-dot" style={{ background: 'var(--accent-secondary)', borderRadius: '50%' }} />
          <span>External site</span>
        </div>
        <div className="link-map-legend-item">
          <span className="link-map-legend-line" style={{ borderBottom: '2px solid var(--accent-primary)' }} />
          <span>Internal link</span>
        </div>
        <div className="link-map-legend-item">
          <span className="link-map-legend-line" style={{ borderBottom: '2px dashed var(--accent-secondary)' }} />
          <span>External link</span>
        </div>
        <div className="link-map-legend-hint">
          Drag nodes · Click or Double-click to open URL · Scroll to zoom
        </div>
      </div>
      <div className="link-map-canvas-wrapper" ref={containerRef}>
        <canvas
          ref={canvasRef}
          width={dimensions.width}
          height={dimensions.height}
          style={{ display: 'block' }}
        />
        {tooltip && (
          <div
            className="link-map-tooltip"
            style={{
              left: tooltip.x,
              top: tooltip.y,
              transform: 'translate(-50%, -100%)',
            }}
          >
            <div className="link-map-tooltip-title">{tooltip.title}</div>
            <div className="link-map-tooltip-url">{tooltip.url}</div>
            <div className="link-map-tooltip-type">{tooltip.type === 'post' ? 'Internal Post' : 'External Site'}</div>
          </div>
        )}
      </div>
    </div>
  )
}

LinkMapGraph.propTypes = {
  nodes: PropTypes.array,
  edges: PropTypes.array,
}
