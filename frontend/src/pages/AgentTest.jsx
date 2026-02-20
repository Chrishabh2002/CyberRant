import React, { useState } from 'react';
import { agentApi } from '../api/agentApi';
import StateBadge from '../components/StateBadge';
import ResponseViewer from '../components/ResponseViewer';
import ApprovalModal from '../components/ApprovalModal';
import MissionDashboard from '../components/MissionDashboard';
import CyberWorldMap from '../components/CyberWorldMap';

const AGENTS = [
    { id: "ASK_RANT", name: "Ask Rant AI", type: "guidance" },
    { id: "RANT_COPILOT", name: "Rant AI Agent", type: "action" }
];

export default function AgentTest() {
    const [selectedAgent, setSelectedAgent] = useState(AGENTS[0]);
    const [query, setQuery] = useState("");
    const [state, setState] = useState("IDLE");
    const [lastResponse, setLastResponse] = useState(null);
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [isLeaOnline, setIsLeaOnline] = useState(false);
    const [showCommunity, setShowCommunity] = useState(true);

    const TRENDING_TOPICS = [
        { topic: "Zero-Trust Strategy", trend: "+42%", severity: "LOW" },
        { topic: "API Key Leakages", trend: "+128%", severity: "CRITICAL" },
        { topic: "Quantum Encryption", trend: "+12%", severity: "LOW" },
        { topic: "Supply Chain Risk", trend: "+65%", severity: "HIGH" }
    ];

    const COMMUNITY_DISCUSSIONS = [
        { user: "SOC_PRO_99", title: "New bypass for Port 443 discovered?", comments: 12 },
        { user: "CYBER_GURU", title: "Best practices for EDR hardening", comments: 45 },
        { user: "DEV_SEC", title: "CI/CD pipeline security metrics", comments: 8 }
    ];

    const handleExecute = async () => {
        if (!query) return;

        setState("PROCESSING");
        setLastResponse(null);

        try {
            const result = await agentApi.execute(selectedAgent.id, query);
            setLastResponse(result);
            setState(result.state);

            if (result.state === "awaiting_approval" || result.state === "APPROVAL_REQUIRED") {
                setIsModalOpen(true);
            }
        } catch (err) {
            console.error(err);
            setState("ERROR");
            setLastResponse({ error: err.message });
        }
    };

    const handleApproval = async (decision) => {
        setIsModalOpen(false);
        setState("PROCESSING");

        try {
            const result = await agentApi.respondToApproval(lastResponse.trace_id, decision);
            setLastResponse(result);
            setState(result.state);
        } catch (err) {
            setState("ERROR");
            setLastResponse({ error: err.message });
        }
    };

    // Global Status Polling for Live Missions
    React.useEffect(() => {
        let interval;
        const isPending = (s) => ["EXECUTING", "PROCESSING", "PENDING", "QUEUED"].includes(s?.toUpperCase());

        if (lastResponse?.trace_id && (isPending(state) || isPending(lastResponse.media_status?.audio_status))) {
            interval = setInterval(async () => {
                try {
                    const updated = await agentApi.getStatus(lastResponse.trace_id);
                    if (updated) {
                        setLastResponse(updated);
                        if (updated.state) setState(updated.state);

                        const isNoLongerPending = !isPending(updated.state) &&
                            !isPending(updated.media_status?.audio_status) &&
                            !isPending(updated.media_status?.video_status);

                        if (isNoLongerPending) {
                            clearInterval(interval);
                        }
                    }
                } catch (e) {
                    console.error("Status Poll Error:", e);
                }
            }, 1000);
        }
        return () => clearInterval(interval);
    }, [lastResponse?.trace_id, state]);

    return (
        <div className="min-h-screen bg-[#020617] text-slate-100 selection:bg-red-500/30 selection:text-white p-0 font-sans red-gradient-bg cyber-grid">
            <div className="flex h-screen overflow-hidden">
                {/* Left Sidebar - Community Intel */}
                {showCommunity && (
                    <aside className="w-80 border-r border-white/5 bg-slate-950/50 backdrop-blur-3xl overflow-y-auto hidden xl:block animate-in slide-in-from-left-10 duration-700">
                        <div className="p-8 space-y-10">
                            <div>
                                <h2 className="text-[10px] font-black text-slate-500 uppercase tracking-[0.4em] mb-6">Trending Analytics</h2>
                                <div className="space-y-4">
                                    {TRENDING_TOPICS.map((t, idx) => (
                                        <div key={idx} className="p-4 rounded-2xl bg-white/5 border border-white/5 hover:border-white/10 transition-all cursor-pointer group">
                                            <div className="flex justify-between items-center">
                                                <span className="text-xs font-bold text-slate-300">{t.topic}</span>
                                                <span className={`${t.trend.startsWith('+') ? 'text-emerald-400' : 'text-red-400'} text-[9px] font-black`}>{t.trend}</span>
                                            </div>
                                            <div className={`h-1 w-full bg-slate-800 rounded-full mt-3 overflow-hidden`}>
                                                <div className={`h-full ${t.severity === 'CRITICAL' ? 'bg-red-500' : 'bg-blue-500'} w-2/3`} />
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>

                            <div>
                                <div className="flex items-center justify-between mb-6">
                                    <h2 className="text-[10px] font-black text-slate-500 uppercase tracking-[0.4em]">Community Intel</h2>
                                    <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
                                </div>
                                <div className="space-y-6">
                                    {COMMUNITY_DISCUSSIONS.map((d, idx) => (
                                        <div key={idx} className="space-y-2 group cursor-pointer">
                                            <div className="flex items-center gap-2">
                                                <div className="w-5 h-5 rounded-full bg-slate-800 text-[8px] flex items-center justify-center font-black text-slate-400">{d.user[0]}</div>
                                                <span className="text-[9px] font-black text-slate-600 uppercase tracking-widest">{d.user}</span>
                                            </div>
                                            <p className="text-[11px] font-bold text-slate-400 group-hover:text-white transition-colors leading-relaxed">{d.title}</p>
                                            <div className="flex items-center gap-3 text-[9px] font-black text-slate-600 uppercase">
                                                <span>{d.comments} INSIGHTS</span>
                                                <span className="w-1 h-1 rounded-full bg-slate-800" />
                                                <span>2m ago</span>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                                <button className="w-full mt-8 py-4 border border-white/5 rounded-2xl text-[9px] font-black text-slate-500 uppercase tracking-widest hover:bg-white/5 transition-all">
                                    Browse All Discussions
                                </button>
                            </div>
                        </div>
                    </aside>
                )}

                {/* Main Content Area */}
                <main className="flex-1 flex flex-col relative overflow-hidden">
                    {/* Top Stats Bar */}
                    <header className="h-20 border-b border-white/5 bg-slate-950/30 backdrop-blur-md flex items-center justify-between px-10 z-20">
                        <div className="flex items-center gap-6">
                            <h1 className="text-xl font-black italic tracking-tighter text-white">RANT AI <span className="text-red-500 font-medium not-italic ml-2 text-sm opacity-50 tracking-[0.3em]">CO-PILOT</span></h1>
                        </div>
                        <div className="flex items-center gap-8">
                            <div className="flex items-center gap-3">
                                <span className="text-[9px] font-black text-slate-500 uppercase tracking-widest">Global Threat</span>
                                <div className="flex gap-1">
                                    <div className="w-3 h-1 bg-emerald-500 rounded-full" />
                                    <div className="w-3 h-1 bg-emerald-500 rounded-full" />
                                    <div className="w-3 h-1 bg-slate-700 rounded-full" />
                                </div>
                            </div>
                            <StateBadge state={state} />
                        </div>
                    </header>

                    {/* Scrollable Workspace */}
                    <div className="flex-1 overflow-y-auto scroll-smooth custom-scrollbar">
                        <div className="max-w-5xl mx-auto p-10 space-y-12 pb-40">
                            {/* Agent Logic Selector */}
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                {AGENTS.map(agent => (
                                    <button
                                        key={agent.id}
                                        onClick={() => setSelectedAgent(agent)}
                                        className={`group relative p-8 rounded-[2rem] border-2 transition-all duration-500 ${selectedAgent.id === agent.id
                                            ? "border-red-600/50 bg-red-600/5 shadow-[0_0_50px_rgba(220,38,38,0.1)]"
                                            : "border-white/5 bg-white/5 hover:border-white/10"
                                            }`}
                                    >
                                        <div className="flex items-center gap-6">
                                            <div className={`w-14 h-14 rounded-3xl flex items-center justify-center font-black text-xl transition-all ${selectedAgent.id === agent.id ? "bg-red-600 text-white shadow-[0_10px_20px_rgba(220,38,38,0.3)]" : "bg-slate-800 text-slate-500 group-hover:bg-slate-700"}`}>
                                                {agent.id === "ASK_RANT" ? "A" : "B"}
                                            </div>
                                            <div className="text-left">
                                                <p className={`text-lg font-black tracking-tighter ${selectedAgent.id === agent.id ? "text-white" : "text-slate-400"}`}>{agent.name}</p>
                                                <p className="text-[10px] text-slate-500 font-black mt-1 tracking-[0.2em] uppercase">
                                                    {agent.type === 'guidance' ? '○ Educational Mode' : '○ Operational Mode'}
                                                </p>
                                            </div>
                                        </div>
                                    </button>
                                ))}
                            </div>

                            {/* Response Display Area */}
                            {lastResponse && (
                                <div id="response-anchor" className="space-y-10 animate-in slide-in-from-bottom-10 duration-700">
                                    <ResponseViewer response={lastResponse} />
                                </div>
                            )}
                        </div>
                    </div>

                    {/* Bottom Prompt Bar - Fixed and Premium */}
                    <div className="absolute bottom-0 left-0 right-0 p-10 bg-gradient-to-t from-[#020617] via-[#020617] to-transparent z-10">
                        <div className="max-w-4xl mx-auto">
                            <div className="glass-panel p-2 flex items-end gap-4 border-white/10 shadow-2xl">
                                <div className="flex-1 relative">
                                    <textarea
                                        className="w-full bg-transparent border-none p-6 text-sm font-bold text-white placeholder:text-slate-600 outline-none min-h-[60px] max-h-[300px] resize-none"
                                        placeholder={selectedAgent.id === "ASK_RANT" ? "Ask anything about cybersecurity..." : "Enter operational command (e.g. scan net 10.0.0.1)..."}
                                        value={query}
                                        onChange={(e) => setQuery(e.target.value)}
                                        onKeyDown={(e) => {
                                            if (e.key === 'Enter' && !e.shiftKey) {
                                                e.preventDefault();
                                                handleExecute();
                                            }
                                        }}
                                        disabled={state === "PROCESSING"}
                                    />
                                    <div className="absolute top-6 left-6 pointer-events-none opacity-0 transition-opacity">
                                        {/* Animation for typing could go here */}
                                    </div>
                                </div>
                                <div className="flex flex-col gap-2 p-4">
                                    <button
                                        onClick={handleExecute}
                                        disabled={!query || state === "PROCESSING"}
                                        className={`w-14 h-14 rounded-2xl flex items-center justify-center transition-all duration-300 shadow-xl ${!query || state === "PROCESSING" ? "bg-slate-800 text-slate-600 cursor-not-allowed" : "bg-red-600 hover:bg-red-500 text-white shadow-red-600/30 active:scale-90"}`}
                                    >
                                        {state === "PROCESSING" ? <div className="w-5 h-5 border-2 border-white/20 border-t-white rounded-full animate-spin" /> :
                                            <svg className="w-6 h-6 transform rotate-45" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="3" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"></path></svg>
                                        }
                                    </button>
                                    <button
                                        onClick={() => { setQuery(""); setLastResponse(null); setState("IDLE"); }}
                                        className="text-[9px] font-black text-slate-600 uppercase tracking-widest hover:text-white transition-colors"
                                    >
                                        Clear
                                    </button>
                                </div>
                            </div>
                            <div className="mt-4 flex justify-between items-center px-6">
                                <p className="text-[9px] font-black text-slate-700 uppercase tracking-[0.3em]">
                                    {selectedAgent.id === "ASK_RANT" ? "Ask Rant AI v3.1 • Learning & Knowledge Engine" : "Action Copilot v4.2 • Task Execution Engine"}
                                </p>
                                <div className="flex items-center gap-4">
                                    <span className="text-[9px] font-black text-slate-500 uppercase">Tokens: {query.length}</span>
                                    <button onClick={() => setShowCommunity(!showCommunity)} className="text-[9px] font-black text-red-600/60 uppercase tracking-widest hover:text-red-500 transition-colors">
                                        {showCommunity ? "Hide Community" : "Show Community"}
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </main>
            </div>

            <ApprovalModal
                isOpen={isModalOpen}
                plan={lastResponse?.action_plan}
                onApprove={() => handleApproval("approve")}
                onReject={() => handleApproval("reject")}
            />
        </div>
    );
}
