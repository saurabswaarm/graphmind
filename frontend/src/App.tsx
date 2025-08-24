import { useCallback } from 'react';
import {
  ReactFlow,
  addEdge,
  useNodesState,
  useEdgesState,
  Controls,
  MiniMap,
  Background,
  BackgroundVariant,
  ConnectionMode,
  type Node,
  type Edge,
  type Connection,
} from '@xyflow/react';

import '@xyflow/react/dist/style.css';
import './App.css';
import './flow-styles.css';

// Initial nodes
const initialNodes: Node[] = [
  {
    id: '1',
    position: { x: 250, y: 25 },
    data: { label: 'Entity A' },
    type: 'default',
  },
  {
    id: '2',
    position: { x: 100, y: 125 },
    data: { label: 'Entity B' },
    type: 'default',
  },
  {
    id: '3',
    position: { x: 400, y: 125 },
    data: { label: 'Entity C' },
    type: 'default',
  },
];

// Initial edges
const initialEdges: Edge[] = [
  { id: 'e1-2', source: '1', target: '2', animated: true },
  { id: 'e1-3', source: '1', target: '3' },
];

function App() {
  const [nodes, , onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

  const onConnect = useCallback(
    (params: Connection) => setEdges((eds: Edge[]) => addEdge(params, eds)),
    [setEdges],
  );

  return (
    <div className="App">
      <header className="App-header">
        <h1>GraphApp - Interactive Graph Visualization</h1>
        <p>Drag nodes to rearrange • Connect nodes by dragging from handles • Use controls to navigate</p>
      </header>
      <div className="graph-container">
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          connectionMode={ConnectionMode.Loose}
          fitView
        >
          <Controls />
          <MiniMap />
          <Background variant={BackgroundVariant.Dots} gap={12} size={1} />
        </ReactFlow>
      </div>
    </div>
  )
}

export default App
