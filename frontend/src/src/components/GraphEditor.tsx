import { useCallback, useState, useEffect, useMemo } from "react";
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
} from "@xyflow/react";

import "@xyflow/react/dist/style.css";
import "../styles/flow-styles.css";

// TextBoxNode component
function TextBoxNode({
  onSave,
  onCancel,
}: {
  onSave: (text: string) => void;
  onCancel: () => void;
}) {
  const [text, setText] = useState("");

  const handleSave = () => {
    if (text.trim()) {
      onSave(text.trim());
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSave();
    } else if (e.key === "Escape") {
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
        cols={17}
        style={{
          maxWidth: "100%",
        }}
      />
      <div className="text-box-actions">
        <button onClick={handleSave} disabled={!text.trim()}>
          Save
        </button>
        <button onClick={onCancel}>Cancel</button>
      </div>
      <Handle type="source" position={Position.Bottom} />
    </div>
  );
}

// Initial nodes
const initialNodes: Node[] = [
  {
    id: "1",
    position: { x: 250, y: 25 },
    data: { label: "Entity A" },
    type: "default",
  },
  {
    id: "2",
    position: { x: 100, y: 125 },
    data: { label: "Entity B" },
    type: "default",
  },
  {
    id: "3",
    position: { x: 400, y: 125 },
    data: { label: "Entity C" },
    type: "default",
  },
];

// Initial edges
const initialEdges: Edge[] = [
  { id: "e1-2", source: "1", target: "2", animated: true },
  { id: "e1-3", source: "1", target: "3" },
];

function GraphEditor() {
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);
  const [showTextBox, setShowTextBox] = useState(false);
  const [textBoxPosition, setTextBoxPosition] = useState({ x: 0, y: 0 });
  const [panningEnabled, setPanningEnabled] = useState(false);

  // Handle keyboard events for panning
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.code === "Space") {
        setPanningEnabled(true);
      }
    };

    const handleKeyUp = (e: KeyboardEvent) => {
      if (e.code === "Space") {
        setPanningEnabled(false);
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    window.addEventListener("keyup", handleKeyUp);

    return () => {
      window.removeEventListener("keydown", handleKeyDown);
      window.removeEventListener("keyup", handleKeyUp);
    };
  }, []);

  const onConnect = useCallback(
    (params: Connection) => setEdges((eds: Edge[]) => addEdge(params, eds)),
    [setEdges]
  );

  const addNode = useCallback(
    (text: string) => {
      const newNode: Node = {
        id: `node-${Date.now()}`,
        position: textBoxPosition,
        data: { label: text },
        type: "default",
      };

      setNodes((nds: Node[]) => [...nds, newNode]);
      setShowTextBox(false);
    },
    [setNodes, textBoxPosition]
  );

  // Node types
  const nodeTypes = useMemo(
    () => ({
      textBox: (props: any) => (
        <TextBoxNode
          {...props}
          onSave={addNode}
          onCancel={() => setShowTextBox(false)}
        />
      ),
    }),
    []
  );

  return (
    <div className="graph-container">
      <ReactFlow
        debug={true}
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        connectionMode={ConnectionMode.Loose}
        fitView
        nodeTypes={nodeTypes}
        panOnDrag={panningEnabled}
        zoomOnScroll={true}
        zoomOnPinch={true}
        panOnScroll={false}
        selectionOnDrag={true}
        onPaneClick={(e: React.MouseEvent) => {
          // Handle both single and double clicks
          if (e.target !== e.currentTarget) return;

          const rect = e.currentTarget.getBoundingClientRect();
          const position = {
            x: e.clientX - rect.left,
            y: e.clientY - rect.top,
          };

          // Set click position for potential node creation
          setTextBoxPosition(position);

          // If text box is already shown, close it (single click behavior)
          if (showTextBox) {
            setShowTextBox(false);
          } else {
            // For double-click detection, we'll use a timeout
            // If another click comes within 300ms, it's a double-click
            // Otherwise, it's a single click
            // Since we can't detect the second click here, we'll show the text box immediately
            // and let the user decide
            setShowTextBox(true);
          }
        }}
        onPaneContextMenu={(e: React.MouseEvent) => {
          // Prevent context menu on pane
          e.preventDefault();
        }}
      >
        <Controls />
        <MiniMap />
        <Background variant={BackgroundVariant.Dots} gap={12} size={1} />

        {showTextBox && (
          <Panel
            position="top-left"
            style={{
              position: "absolute",
              left: textBoxPosition.x,
              top: textBoxPosition.y,
            }}
          >
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
