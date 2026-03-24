import { AppLayout } from "./components/layout/AppLayout";
import { useSessionRestore } from "./hooks/useSessionStore";

function App() {
  useSessionRestore();
  return <AppLayout />;
}

export default App;
