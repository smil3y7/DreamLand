/**
 * Interactive world map component using D3.js.
 * Displays dream locations as bubbles with zoom, pan, and drag functionality.
 */
import { useEffect, useRef, useState } from 'react'
import * as d3 from 'd3'
import LocationPopup from './LocationPopup'
import { ZoomIn, ZoomOut, Maximize2 } from 'lucide-react'
import { useTranslation } from '../lib/i18n'

export default function WorldMap({ 
  locations, 
  selectedLocation, 
  onLocationSelect,
  onLocationUpdate 
}) {
  const svgRef = useRef()
  const { t } = useTranslation()
  const [zoom, setZoom] = useState(1)
  const [editMode, setEditMode] = useState(false)

  useEffect(() => {
    if (!svgRef.current || !locations) return

    const svg = d3.select(svgRef.current)
    const width = svgRef.current.clientWidth
    const height = svgRef.current.clientHeight

    // Clear previous content
    svg.selectAll('*').remove()

    // Create zoom behavior
    const zoomBehavior = d3.zoom()
      .scaleExtent([0.5, 5])
      .on('zoom', (event) => {
        g.attr('transform', event.transform)
        setZoom(event.transform.k)
      })

    svg.call(zoomBehavior)

    // Main group for zooming/panning
    const g = svg.append('g')

    // Background grid
    const gridSize = 50
    const gridGroup = g.append('g').attr('class', 'grid')
    
    for (let x = -width; x < width * 2; x += gridSize) {
      gridGroup.append('line')
        .attr('x1', x)
        .attr('y1', -height)
        .attr('x2', x)
        .attr('y2', height * 2)
        .attr('stroke', '#374151')
        .attr('stroke-width', 0.5)
        .attr('opacity', 0.3)
    }
    
    for (let y = -height; y < height * 2; y += gridSize) {
      gridGroup.append('line')
        .attr('x1', -width)
        .attr('y1', y)
        .attr('x2', width * 2)
        .attr('y2', y)
        .attr('stroke', '#374151')
        .attr('stroke-width', 0.5)
        .attr('opacity', 0.3)
    }

    // Center axes
    g.append('line')
      .attr('x1', -width)
      .attr('y1', height / 2)
      .attr('x2', width * 2)
      .attr('y2', height / 2)
      .attr('stroke', '#4b5563')
      .attr('stroke-width', 1)
      .attr('opacity', 0.5)

    g.append('line')
      .attr('x1', width / 2)
      .attr('y1', -height)
      .attr('x2', width / 2)
      .attr('y2', height * 2)
      .attr('stroke', '#4b5563')
      .attr('stroke-width', 1)
      .attr('opacity', 0.5)

    // Scale for converting normalized coordinates to pixels
    const xScale = d3.scaleLinear()
      .domain([-1, 1])
      .range([width * 0.2, width * 0.8])

    const yScale = d3.scaleLinear()
      .domain([-1, 1])
      .range([height * 0.8, height * 0.2])

    // Radius scale based on frequency
    const radiusScale = d3.scaleSqrt()
      .domain([0, d3.max(locations, d => d.frequency) || 10])
      .range([20, 60])

    // Create location bubbles
    const bubbles = g.selectAll('.bubble')
      .data(locations)
      .enter()
      .append('g')
      .attr('class', 'bubble dream-bubble')
      .attr('transform', d => `translate(${xScale(d.x)}, ${yScale(d.y)})`)
      .style('cursor', editMode ? 'move' : 'pointer')

    // Bubble circles
    bubbles.append('circle')
      .attr('r', d => radiusScale(d.frequency))
      .attr('fill', d => d.color)
      .attr('fill-opacity', 0.6)
      .attr('stroke', d => d.color)
      .attr('stroke-width', 2)
      .on('click', function(event, d) {
        if (!editMode) {
          onLocationSelect(d)
        }
      })

    // Drag behavior for edit mode
    if (editMode) {
      const dragBehavior = d3.drag()
        .on('start', function() {
          d3.select(this).raise()
        })
        .on('drag', function(event, d) {
          const [x, y] = d3.pointer(event, g.node())
          d3.select(this).attr('transform', `translate(${x}, ${y})`)
        })
        .on('end', function(event, d) {
          const [x, y] = d3.pointer(event, g.node())
          const normalizedX = xScale.invert(x)
          const normalizedY = yScale.invert(y)
          
          // Clamp to -1, 1 range
          const clampedX = Math.max(-1, Math.min(1, normalizedX))
          const clampedY = Math.max(-1, Math.min(1, normalizedY))
          
          onLocationUpdate(d.id, { x: clampedX, y: clampedY })
        })

      bubbles.call(dragBehavior)
    }

    // Emoji/symbol text
    bubbles.append('text')
      .attr('text-anchor', 'middle')
      .attr('dy', '0.3em')
      .attr('font-size', d => radiusScale(d.frequency) * 0.5)
      .text(d => d.symbol || '📍')
      .style('pointer-events', 'none')

    // Location name
    bubbles.append('text')
      .attr('text-anchor', 'middle')
      .attr('dy', d => radiusScale(d.frequency) + 15)
      .attr('font-size', '12px')
      .attr('fill', '#e5e7eb')
      .text(d => d.name)
      .style('pointer-events', 'none')

    // Reset zoom function
    window.resetMapZoom = () => {
      svg.transition()
        .duration(750)
        .call(zoomBehavior.transform, d3.zoomIdentity)
    }

    // Zoom in/out functions
    window.zoomMapIn = () => {
      svg.transition()
        .duration(300)
        .call(zoomBehavior.scaleBy, 1.3)
    }

    window.zoomMapOut = () => {
      svg.transition()
        .duration(300)
        .call(zoomBehavior.scaleBy, 0.7)
    }

  }, [locations, selectedLocation, editMode, onLocationSelect, onLocationUpdate])

  return (
    <div className="relative w-full h-full bg-gray-900">
      <svg
        ref={svgRef}
        className="w-full h-full"
      />

      {/* Controls */}
      <div className="absolute top-4 right-4 flex flex-col gap-2">
        <button
          onClick={() => window.zoomMapIn?.()}
          className="p-2 bg-gray-800 hover:bg-gray-700 rounded shadow-lg"
          title="Zoom In"
        >
          <ZoomIn className="w-5 h-5" />
        </button>
        
        <button
          onClick={() => window.zoomMapOut?.()}
          className="p-2 bg-gray-800 hover:bg-gray-700 rounded shadow-lg"
          title="Zoom Out"
        >
          <ZoomOut className="w-5 h-5" />
        </button>
        
        <button
          onClick={() => window.resetMapZoom?.()}
          className="p-2 bg-gray-800 hover:bg-gray-700 rounded shadow-lg"
          title="Reset View"
        >
          <Maximize2 className="w-5 h-5" />
        </button>

        <button
          onClick={() => setEditMode(!editMode)}
          className={`p-2 rounded shadow-lg ${
            editMode 
              ? 'bg-blue-600 hover:bg-blue-700' 
              : 'bg-gray-800 hover:bg-gray-700'
          }`}
          title="Toggle Edit Mode"
        >
          ✏️
        </button>
      </div>

      {/* Zoom indicator */}
      <div className="absolute bottom-4 right-4 bg-gray-800 px-3 py-1 rounded text-sm">
        {Math.round(zoom * 100)}%
      </div>

      {/* Location popup */}
      {selectedLocation && (
        <LocationPopup
          location={selectedLocation}
          onClose={() => onLocationSelect(null)}
        />
      )}
    </div>
  )
}