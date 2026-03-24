import { AppLayout } from "./components/layout/AppLayout";
import { useSessionRestore } from "./hooks/useSessionRestore";

function App() {
  useSessionRestore();
  return <AppLayout />;
}

export default App;
