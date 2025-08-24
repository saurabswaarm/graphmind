import { useCallback, useState } from 'react';
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
  Panel,
  Handle,
  Position,
} from '@xyflow/react';

import '@xyflow/react/dist/style.css';
import '../styles/flow-styles.css';

// TextBoxNode component
function TextBoxNode({ onSave, onCancel }: { onSave: (text: string) => void; onCancel: () => void }) {
  const [text, setText] = useState('');
  
  const handleSave = () => {
    if (text.trim()) {
      onSave(text.trim());
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSave();
    } else if (e.key === 'Escape') {
      onCancel();
    }
  };

  return (
    <div className="text-box-node">
      <Handle type="target" position={Position.Top} />
      <textarea
        value={text}
        onChange={(e) => setText(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="Type something..."
        rows={3}
        cols={20}
      />
      <div className="text-box-actions">
        <button onClick={handleSave} disabled={!text.trim()}>
          Save
        </button>
        <button onClick={onCancel}>
          Cancel
        </button>
      </div>
      <Handle type="source" position={Position.Bottom} />
    </div>
  );
}

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

function GraphEditor() {
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);
  const [showTextBox, setShowTextBox] = useState(false);
  const [textBoxPosition, setTextBoxPosition] = useState({ x: 0, y: 0 });

  const onConnect = useCallback(
    (params: Connection) => setEdges((eds: Edge[]) => addEdge(params, eds)),
    [setEdges],
  );

  const onDoubleClick = useCallback((event: React.MouseEvent) => {
    // Get the position relative to the ReactFlow canvas
    const reactFlowBounds = event.currentTarget.getBoundingClientRect();
    const position = {
      x: event.clientX - reactFlowBounds.left,
      y: event.clientY - reactFlowBounds.top,
    };
    
    setTextBoxPosition(position);
    setShowTextBox(true);
  }, []);

  const addNode = useCallback((text: string) => {
    const newNode: Node = {
      id: `node-${Date.now()}`,
      position: textBoxPosition,
      data: { label: text },
      type: 'default',
    };
    
    setNodes((nds: Node[]) => [...nds, newNode]);
    setShowTextBox(false);
  }, [setNodes, textBoxPosition]);

  // Node types
  const nodeTypes = {
    textBox: (props: any) => <TextBoxNode {...props} onSave={addNode} onCancel={() => setShowTextBox(false)} />,
  };

  return (
    <div className="graph-container">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        onDoubleClick={onDoubleClick}
        connectionMode={ConnectionMode.Loose}
        fitView
        nodeTypes={nodeTypes}
      >
        <Controls />
        <MiniMap />
        <Background variant={BackgroundVariant.Dots} gap={12} size={1} onDoubleClick={onDoubleClick}/>
        
        {showTextBox && (
          <Panel position="top-left" style={{ position: 'absolute', left: textBoxPosition.x, top: textBoxPosition.y }}>
            <TextBoxNode 
              onSave={addNode}
              onCancel={() => setShowTextBox(false)}
            />
          </Panel>
        )}
      </ReactFlow>
    </div>
  );
}

export default GraphEditor;
