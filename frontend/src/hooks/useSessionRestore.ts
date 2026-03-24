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
    getSession(sessionId)
      .then((res) => {
        const data = res.data;
        // only restore if session has actually progressed
        if (data.stage && data.stage !== "discover") setStage(data.stage);
        if (data.integration) {
          setIntegration(data.integration);
          if (data.integration.language)
            setCodeLanguage(data.integration.language);
        }
        if (data.memoryActive) setMemoryActive(data.memoryActive);
      })
      .catch(() => {
        // fresh session — backend doesn't know it yet, that's fine
        // no console error, no action needed
      });
  }, []);
}
