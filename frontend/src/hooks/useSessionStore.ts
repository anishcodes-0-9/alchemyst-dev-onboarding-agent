import { useEffect } from "react";
import { useSessionStore } from "../stores/sessionStore";
import { getSession } from "../services/api";

export function useSessionRestore() {
  const {
    sessionId,
    setStage,
    setIntegration,
    setMemoryActive,
    setCodeLanguage,
  } = useSessionStore();

  useEffect(() => {
    // try to restore session state from backend on load
    getSession(sessionId)
      .then((res) => {
        const data = res.data;
        if (data.stage) setStage(data.stage);
        if (data.integration) {
          setIntegration(data.integration);
          if (data.integration.language)
            setCodeLanguage(data.integration.language);
        }
        if (data.memoryActive) setMemoryActive(data.memoryActive);
      })
      .catch(() => {
        // session not found on backend — fresh start, no action needed
      });
  }, []);
}
