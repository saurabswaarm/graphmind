import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import type { PayloadAction } from '@reduxjs/toolkit';
import type { Node, Edge } from '@xyflow/react';

// Define types
interface GraphState {
  nodes: Node[];
  edges: Edge[];
  loading: boolean;
  error: string | null;
}

// Initial state
const initialState: GraphState = {
  nodes: [
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
  ],
  edges: [
    { id: 'e1-2', source: '1', target: '2', animated: true },
    { id: 'e1-3', source: '1', target: '3' },
  ],
  loading: false,
  error: null,
};

// Dummy async thunk for fetching graph data
export const fetchGraphData = createAsyncThunk(
  'graph/fetchGraphData',
  async (_, { rejectWithValue }) => {
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // In a real app, this would fetch from an API
      return {
        nodes: initialState.nodes,
        edges: initialState.edges
      };
    } catch (error) {
      return rejectWithValue('Failed to fetch graph data');
    }
  }
);

// Dummy async thunk for saving graph data
export const saveGraphData = createAsyncThunk(
  'graph/saveGraphData',
  async (graphData: { nodes: Node[]; edges: Edge[] }, { rejectWithValue }) => {
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // In a real app, this would save to an API
      return graphData;
    } catch (error) {
      return rejectWithValue('Failed to save graph data');
    }
  }
);

// Graph slice
const graphSlice = createSlice({
  name: 'graph',
  initialState,
  reducers: {
    addNode: (state, action: PayloadAction<Node>) => {
      state.nodes.push(action.payload);
    },
    removeNode: (state, action: PayloadAction<string>) => {
      state.nodes = state.nodes.filter(node => node.id !== action.payload);
      // Also remove any edges connected to this node
      state.edges = state.edges.filter(
        edge => edge.source !== action.payload && edge.target !== action.payload
      );
    },
    addEdge: (state, action: PayloadAction<Edge>) => {
      state.edges.push(action.payload);
    },
    updateNode: (state, action: PayloadAction<Node>) => {
      const index = state.nodes.findIndex(node => node.id === action.payload.id);
      if (index !== -1) {
        state.nodes[index] = action.payload;
      }
    },
  },
  extraReducers: (builder) => {
    builder
      // Fetch graph data
      .addCase(fetchGraphData.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchGraphData.fulfilled, (state, action) => {
        state.loading = false;
        state.nodes = action.payload.nodes;
        state.edges = action.payload.edges;
      })
      .addCase(fetchGraphData.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })
      // Save graph data
      .addCase(saveGraphData.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(saveGraphData.fulfilled, (state) => {
        state.loading = false;
      })
      .addCase(saveGraphData.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      });
  },
});

export const { addNode, removeNode, addEdge, updateNode } = graphSlice.actions;

export default graphSlice.reducer;
