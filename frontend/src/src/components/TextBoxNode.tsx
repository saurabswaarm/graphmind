import { useState, useRef, useEffect } from 'react';
import { Handle, Position } from '@xyflow/react';
import "../styles/flow-styles.css"

interface TextBoxNodeProps {
  onSave: (text: string) => void;
  onCancel: () => void;
}

function TextBoxNode({ onSave, onCancel }: TextBoxNodeProps) {
  const [text, setText] = useState('');
  const inputRef = useRef<HTMLTextAreaElement>(null);
  
  useEffect(() => {
    // Focus the input when component mounts
    if (inputRef.current) {
      inputRef.current.focus();
    }
  }, []);

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
        ref={inputRef}
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

export default TextBoxNode;
