import { Provider } from "react-redux";
import store from "./store";
import GraphEditor from "./src/components/GraphEditor";
import "./App.css";
import "./src/styles/flow-styles.css";

function App() {
  return (
    <Provider store={store}>
      <div className="App">
        <header className="App-header">
          <h1>GraphApp - Interactive Graph Visualization</h1>
          <p>
            Drag nodes to rearrange • Connect nodes by dragging from handles •
            Use controls to navigate
          </p>
        </header>
        <GraphEditor />
      </div>
    </Provider>
  );
}

export default App;
