import { ChatPanel } from "../chat/ChatPanel";
import { IntegrationCard } from "../card/IntegrationCard";

export function AppLayout() {
  return (
    <div className="flex h-screen bg-white overflow-hidden">
      {/* left — chat panel 60% */}
      <div className="flex flex-col w-full md:w-[60%] border-r border-gray-100">
        <ChatPanel />
      </div>

      {/* right — integration card 40% */}
      <div className="hidden md:flex flex-col w-[40%]">
        <IntegrationCard />
      </div>
    </div>
  );
}
