import React, { useState } from 'react'
import { MapContainer, TileLayer, CircleMarker, Polyline, Popup } from 'react-leaflet'
import { LineChart, Line, BarChart, Bar, Legend, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer } from 'recharts'
import { Play, Activity, Map as MapIcon, BarChart2 } from 'lucide-react'
import benchmarkData from './assets/benchmark_data.json'

const ROUTE_COLORS = ['#4f46e5', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#14b8a6']

function App() {
  const [loading, setLoading] = useState(false)
  const [activeTab, setActiveTab] = useState('map')
  const [params, setParams] = useState({
    n_customers: 20,
    vehicle_capacity: 50,
    swarm_size: 20,
    iterations: 50,
    k_subswarms: 3
  })
  
  const [result, setResult] = useState(null)
  
  const handleOptimize = async () => {
    setLoading(true)
    try {
      const response = await fetch('/api/optimize', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(params)
      })
      
      const data = await response.json()
      setResult(data)
    } catch (err) {
      console.error(err)
      alert("Cannot reach the optimization server. Please check if the FastAPI backend is running.")
    } finally {
      setLoading(false)
    }
  }

  // Format history for Recharts
  const chartData = result?.history.map((cost, idx) => ({
    iteration: idx + 1,
    cost: cost
  })) || []

  // Center Map on nodes
  const mapCenter = result?.nodes && result.nodes.length > 0
    ? [
        result.nodes.reduce((sum, n) => sum + n.lat, 0) / result.nodes.length,
        result.nodes.reduce((sum, n) => sum + n.lng, 0) / result.nodes.length
      ]
    : [37.8243, -122.2316]

  return (
    <div className="dashboard-container">
      {/* Sidebar */}
      <aside className="glass-panel sidebar">
        <div className="header">
          <h1><Activity size={24} color="#4f46e5" /> Q-Route</h1>
          <p>Quantum-Inspired VRP Solver</p>
        </div>
        
        <div className="tabs-container" style={{ display: 'flex', gap: '8px', marginBottom: '24px' }}>
          <button 
            className={`tab-btn ${activeTab === 'map' ? 'active' : ''}`}
            onClick={() => setActiveTab('map')}
            style={{ flex: 1, padding: '8px', borderRadius: '6px', border: 'none', cursor: 'pointer', background: activeTab === 'map' ? '#4f46e5' : '#e2e8f0', color: activeTab === 'map' ? 'white' : '#475569', fontWeight: 600, fontSize: 13, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 6 }}
          >
            <MapIcon size={16} /> Map
          </button>
          <button 
            className={`tab-btn ${activeTab === 'benchmarks' ? 'active' : ''}`}
            onClick={() => setActiveTab('benchmarks')}
            style={{ flex: 1, padding: '8px', borderRadius: '6px', border: 'none', cursor: 'pointer', background: activeTab === 'benchmarks' ? '#4f46e5' : '#e2e8f0', color: activeTab === 'benchmarks' ? 'white' : '#475569', fontWeight: 600, fontSize: 13, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 6 }}
          >
            <BarChart2 size={16} /> Benchmarks
          </button>
        </div>
        
        <div className="control-group">
          <h3>Problem Settings</h3>
          <div className="input-field">
            <label>Customers <span>{params.n_customers}</span></label>
            <input 
              type="range" min="5" max="50" 
              value={params.n_customers}
              onChange={e => setParams({...params, n_customers: parseInt(e.target.value)})}
            />
          </div>
          <div className="input-field">
            <label>Vehicle Capacity <span>{params.vehicle_capacity}</span></label>
            <input 
              type="range" min="20" max="100" 
              value={params.vehicle_capacity}
              onChange={e => setParams({...params, vehicle_capacity: parseInt(e.target.value)})}
            />
          </div>
        </div>

        <div className="control-group">
          <h3>Algorithm Settings</h3>
          <div className="input-field">
            <label>Swarm Size <span>{params.swarm_size}</span></label>
            <input 
              type="range" min="10" max="50" 
              value={params.swarm_size}
              onChange={e => setParams({...params, swarm_size: parseInt(e.target.value)})}
            />
          </div>
          <div className="input-field">
            <label>Iterations <span>{params.iterations}</span></label>
            <input 
              type="range" min="10" max="100" 
              value={params.iterations}
              onChange={e => setParams({...params, iterations: parseInt(e.target.value)})}
            />
          </div>
          <div className="input-field">
            <label>Consensus Groups <span>{params.k_subswarms}</span></label>
            <input 
              type="range" min="1" max="10" 
              value={params.k_subswarms}
              onChange={e => setParams({...params, k_subswarms: parseInt(e.target.value)})}
            />
          </div>
        </div>

        <button 
          className="btn-primary" 
          onClick={handleOptimize}
          disabled={loading}
          style={{ marginTop: 'auto' }}
        >
          {loading ? <Activity className="spinner" size={20} /> : <Play size={20} />}
          {loading ? 'Optimizing...' : 'Run Optimization'}
        </button>
      </aside>

      {/* Main Content */}
      <main className="main-content" style={activeTab === 'benchmarks' ? { display: 'block', height: '100%' } : {}}>
        
        {activeTab === 'map' && (
          <>
        {/* Analytics Panel */}
        <section className="glass-panel" style={{ padding: 20 }}>
          <div className="analytics-container analytics-grid">
            
            {/* Convergence Chart */}
            <div className="chart-section" style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
              <h4 style={{ fontSize: 13, color: '#718096', marginBottom: 16, textTransform: 'uppercase', letterSpacing: '0.05em', fontWeight: 600 }}>Convergence History</h4>
              {result ? (
                <div style={{ flex: 1, minHeight: 0 }}>
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={chartData} margin={{ top: 10, right: 30, left: 10, bottom: 20 }}>
                      <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="rgba(0,0,0,0.05)" />
                      <XAxis dataKey="iteration" axisLine={false} tickLine={false} tick={{fill: '#a0aec0', fontSize: 11}} tickMargin={10} label={{ value: 'Iteration', position: 'insideBottom', offset: -15, fill: '#718096', fontSize: 12, fontWeight: 500 }} />
                      <YAxis axisLine={false} tickLine={false} tick={{fill: '#a0aec0', fontSize: 11}} domain={['auto', 'auto']} width={60} tickMargin={10} label={{ value: 'Cost', angle: -90, position: 'insideLeft', offset: 0, fill: '#718096', fontSize: 12, fontWeight: 500, style: { textAnchor: 'middle' } }} />
                      <RechartsTooltip 
                        contentStyle={{ borderRadius: 8, border: 'none', boxShadow: '0 10px 15px -3px rgba(0,0,0,0.1)', background: 'rgba(255,255,255,0.95)', backdropFilter: 'blur(8px)' }}
                        itemStyle={{ color: '#4f46e5', fontWeight: 600 }}
                        labelStyle={{ color: '#718096', fontSize: 12, marginBottom: 4 }}
                      />
                      <Line type="monotone" dataKey="cost" stroke="#4f46e5" strokeWidth={3} dot={false} activeDot={{ r: 6, fill: '#4f46e5', stroke: '#fff', strokeWidth: 2 }} />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              ) : (
                <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#cbd5e1', fontSize: 13 }}>
                  Run optimization to view convergence history
                </div>
              )}
            </div>

            {/* Robustness Metrics */}
            <div className="metrics-section" style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
               <h4 style={{ fontSize: 13, color: '#718096', marginBottom: 16, textTransform: 'uppercase', letterSpacing: '0.05em', fontWeight: 600 }}>Route Scenarios</h4>
               {result ? (
                 <div className="table-container" style={{ overflowY: 'auto', paddingRight: 4, flex: 1 }}>
                   <table className="data-table">
                     <thead>
                       <tr>
                         <th>Vehicle</th>
                         <th className="text-right">Avg Cost</th>
                         <th className="text-right">Worst Case</th>
                         <th className="text-right"><span title="Lambda Robustness Score (L=0.5)" style={{cursor: 'help'}}>Lambda</span></th>
                       </tr>
                     </thead>
                     <tbody>
                       {result.routes.map((route, idx) => (
                         <tr key={`metric-${idx}`}>
                           <td>
                             <div className="vehicle-label">
                               <div className="vehicle-dot" style={{ background: ROUTE_COLORS[idx % ROUTE_COLORS.length] }} />
                               Vehicle {route.vehicle_id}
                             </div>
                           </td>
                           <td className="text-right"><strong style={{ color: '#2d3748' }}>{route.metrics?.avg?.toFixed(1) || '0.0'}</strong></td>
                           <td className="text-right"><strong style={{ color: '#ef4444' }}>{route.metrics?.worst?.toFixed(1) || '0.0'}</strong></td>
                           <td className="text-right"><strong style={{ color: '#4f46e5' }}>{route.metrics?.lambda_score?.toFixed(1) || '0.0'}</strong></td>
                         </tr>
                       ))}
                     </tbody>
                   </table>
                 </div>
               ) : (
                 <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#cbd5e1', fontSize: 13 }}>
                  Run optimization to view scenario metrics
                 </div>
               )}
            </div>
            </div>
        </section>

        {/* Map Panel */}
        <section className="glass-panel" style={{ padding: 16 }}>
          <div className="map-container">
            {result ? (
              <MapContainer 
                center={mapCenter} 
                zoom={14} 
                style={{ height: '100%', width: '100%', borderRadius: 12 }}
                key={result.nodes[0].id} // Force re-render on new data
              >
                <TileLayer
                  url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                  attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
                />
                
                {/* Draw Nodes */}
                {result.nodes.map(node => (
                  <CircleMarker
                    key={`node-${node.id}`}
                    center={[node.lat, node.lng]}
                    radius={node.is_depot ? 6 : 4}
                    pathOptions={{
                      color: node.is_depot ? '#ef4444' : '#4f46e5',
                      fillColor: node.is_depot ? '#ef4444' : '#4f46e5',
                      fillOpacity: 1
                    }}
                  >
                    <Popup>
                      Node {node.id} <br/>
                      {node.is_depot ? 'Depot' : `Demand: ${node.demand}`}
                    </Popup>
                  </CircleMarker>
                ))}

                {/* Draw Routes */}
                {result.routes.map((routeData, idx) => {
                  const color = ROUTE_COLORS[idx % ROUTE_COLORS.length]
                  // Map graph_route node IDs to coordinates
                  const positions = routeData.path_coordinates || routeData.graph_route.map(nodeId => {
                    const node = result.nodes.find(n => n.id === nodeId)
                    return [node.lat, node.lng]
                  })
                  
                  return (
                    <Polyline
                      key={`route-${idx}`}
                      positions={positions}
                      pathOptions={{ color, weight: 3, opacity: 0.8 }}
                    />
                  )
                })}
              </MapContainer>
            ) : (
              <div style={{ height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#718096', fontSize: 14 }}>
                Set parameters and run optimization to generate routes
              </div>
            )}
          </div>
        </section>
        </>
        )}

        {activeTab === 'benchmarks' && (
          <section className="glass-panel" style={{ padding: 32, height: '100%', overflowY: 'auto' }}>
            <h2 style={{ marginBottom: 24, color: '#1e293b', display: 'flex', alignItems: 'center', gap: 8 }}>
              <BarChart2 size={24} color="#4f46e5" /> Ablation Studies & Benchmarks
            </h2>
            
            <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: 32 }}>
              {/* Convergence Plot */}
              <div className="chart-card" style={{ background: 'rgba(255,255,255,0.5)', padding: 24, borderRadius: 12, border: '1px solid rgba(255,255,255,0.6)' }}>
                <h3 style={{ fontSize: 16, color: '#334155', marginBottom: 16 }}>Convergence History: Algorithm Comparison</h3>
                <div style={{ height: 350 }}>
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={benchmarkData.convergence} margin={{ top: 10, right: 30, left: 10, bottom: 20 }}>
                      <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="rgba(0,0,0,0.05)" />
                      <XAxis dataKey="iteration" axisLine={false} tickLine={false} tick={{fill: '#a0aec0'}} label={{ value: 'Iteration', position: 'insideBottom', offset: -10, fill: '#718096' }} />
                      <YAxis axisLine={false} tickLine={false} tick={{fill: '#a0aec0'}} domain={['auto', 'auto']} width={70} label={{ value: 'Global Best Cost', angle: -90, position: 'insideLeft', offset: 0, fill: '#718096' }} />
                      <RechartsTooltip contentStyle={{ borderRadius: 8, border: 'none', boxShadow: '0 10px 15px -3px rgba(0,0,0,0.1)' }} />
                      <Legend verticalAlign="top" height={36} iconType="circle" />
                      <Line type="monotone" dataKey="Standard PSO" stroke="#ef4444" strokeWidth={2} dot={false} />
                      <Line type="monotone" dataKey="Canonical QPSO" stroke="#f59e0b" strokeWidth={2} dot={false} />
                      <Line type="monotone" dataKey="Q-Route" stroke="#4f46e5" strokeWidth={3} dot={false} activeDot={{ r: 6 }} />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
                <p style={{ fontSize: 13, color: '#64748b', marginTop: 12 }}>
                  * Q-Route (Blue) utilizes classical-quantum-walk reseeding and discrete Prins decoding to escape local minima faster than standard classical baselines.
                </p>
              </div>

              {/* Redundancy Curve */}
              <div className="chart-card" style={{ background: 'rgba(255,255,255,0.5)', padding: 24, borderRadius: 12, border: '1px solid rgba(255,255,255,0.6)' }}>
                <h3 style={{ fontSize: 16, color: '#334155', marginBottom: 16 }}>Darwinism Consensus: Redundancy (R) Curve</h3>
                <div style={{ height: 350 }}>
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={benchmarkData.redundancy} margin={{ top: 10, right: 30, left: 10, bottom: 20 }}>
                      <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="rgba(0,0,0,0.05)" />
                      <XAxis dataKey="subswarms" axisLine={false} tickLine={false} tick={{fill: '#a0aec0'}} label={{ value: 'Number of Independent Sub-Swarms (K)', position: 'insideBottom', offset: -10, fill: '#718096' }} />
                      <YAxis axisLine={false} tickLine={false} tick={{fill: '#a0aec0'}} label={{ value: 'Avg Agreement Count (R)', angle: -90, position: 'insideLeft', offset: 0, fill: '#718096' }} />
                      <RechartsTooltip contentStyle={{ borderRadius: 8, border: 'none', boxShadow: '0 10px 15px -3px rgba(0,0,0,0.1)' }} />
                      <Legend verticalAlign="top" height={36} iconType="circle" />
                      <Bar dataKey="redundancy" name="Observed Redundancy (R)" fill="#10b981" radius={[4, 4, 0, 0]} />
                      <Line type="step" dataKey="threshold" name="Consensus Threshold [ceil(K/2)]" stroke="#ef4444" strokeWidth={2} dot={false} isAnimationActive={false} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
                <p style={{ fontSize: 13, color: '#64748b', marginTop: 12 }}>
                  * The redundancy count R scales linearly/logarithmically with K, mimicking the classic signature of redundant information proliferation in Quantum Darwinism.
                </p>
              </div>
            </div>
          </section>
        )}

      </main>
    </div>
  )
}

export default App
