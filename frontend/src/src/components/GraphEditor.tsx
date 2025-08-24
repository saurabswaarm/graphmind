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
  useReactFlow,
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
          maxWidth : "100%",
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

// Custom Node component with delete button and key-value pair functionality
interface CustomNodeData {
  label: string;
  keyValuePairs?: { key: string; value: string }[];
}

interface CustomNodeProps {
  id: string;
  data: CustomNodeData;
}

function CustomNode({ id, data }: CustomNodeProps) {
  const { setNodes } = useReactFlow();
  const [showForm, setShowForm] = useState(false);
  const [keyValuePairs, setKeyValuePairs] = useState<{ key: string; value: string }[]>(data.keyValuePairs || []);
  const [newKey, setNewKey] = useState("");
  const [newValue, setNewValue] = useState("");

  const handleDelete = () => {
    setNodes((nds) => nds.filter((node) => node.id !== id));
  };

  const handleAddKeyValuePair = () => {
    if (newKey.trim() && newValue.trim()) {
      const updatedPairs = [...keyValuePairs, { key: newKey.trim(), value: newValue.trim() }];
      setKeyValuePairs(updatedPairs);
      setNodes((nds) =>
        nds.map((node) =>
          node.id === id
            ? { ...node, data: { ...node.data, keyValuePairs: updatedPairs } }
            : node
        )
      );
      setNewKey("");
      setNewValue("");
    }
  };

  const handleRemoveKeyValuePair = (index: number) => {
    const updatedPairs = keyValuePairs.filter((_, i) => i !== index);
    setKeyValuePairs(updatedPairs);
    setNodes((nds) =>
      nds.map((node) =>
        node.id === id
          ? { ...node, data: { ...node.data, keyValuePairs: updatedPairs } }
          : node
      )
    );
  };

  return (
    <div className="custom-node">
      <Handle type="target" position={Position.Top} />
      <div className="node-header">
        <div className="node-label">{data.label}</div>
        <button className="delete-button" onClick={handleDelete}>
          ×
        </button>
      </div>
      {keyValuePairs.length > 0 && (
        <div className="key-value-container">
          {keyValuePairs.map((pair, index) => (
            <div key={index} className="key-value-pair">
              <span className="key">{pair.key}:</span>
              <span className="value">{pair.value}</span>
              <button 
                className="remove-pair-button" 
                onClick={() => handleRemoveKeyValuePair(index)}
              >
                ×
              </button>
            </div>
          ))}
        </div>
      )}
      <button className="add-pair-button" onClick={() => setShowForm(!showForm)}>
        {showForm ? "Cancel" : "Add Property"}
      </button>
      {showForm && (
        <div className="key-value-form">
          <input
            type="text"
            placeholder="Key"
            value={newKey}
            onChange={(e) => setNewKey(e.target.value)}
          />
          <input
            type="text"
            placeholder="Value"
            value={newValue}
            onChange={(e) => setNewValue(e.target.value)}
          />
          <button onClick={handleAddKeyValuePair}>Add</button>
        </div>
      )}
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
    type: "custom",
  },
  {
    id: "2",
    position: { x: 100, y: 125 },
    data: { label: "Entity B" },
    type: "custom",
  },
  {
    id: "3",
    position: { x: 400, y: 125 },
    data: { label: "Entity C" },
    type: "custom",
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
  const reactFlow = useReactFlow();

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

  const addNode =
  //  useCallback(
    (text: string) => {
      debugger
      console.log(textBoxPosition)
      const newNode: Node = {
        id: `node-${Date.now()}`,
        position: textBoxPosition,
        data: { label: text },
        type: "custom",
      };

      setNodes((nds: Node[]) => [...nds, newNode]);
      setShowTextBox(false);
    };
  //   [setNodes, textBoxPosition]
  // );

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
      custom: CustomNode,
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

          // Convert screen coordinates to flow coordinates
          const position = reactFlow.screenToFlowPosition({
            x: e.clientX,
            y: e.clientY,
          });

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
