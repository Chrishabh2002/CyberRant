import React, { useState } from 'react';
import { agentApi } from '../api/agentApi';
import StateBadge from '../components/StateBadge';
import ResponseViewer from '../components/ResponseViewer';
import ApprovalModal from '../components/ApprovalModal';

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

    return (
        <div className="min-h-screen bg-[#fcfcfc] text-slate-900 selection:bg-red-100 selection:text-red-900 p-4 md:p-8 font-sans">
            <div className="max-w-5xl mx-auto">
                {/* Header Card */}
                <div className="bg-white rounded-[2.5rem] shadow-[0_20px_50px_rgba(0,0,0,0.02)] border border-slate-100 overflow-hidden mb-10 transition-all">
                    <div className="bg-slate-950 px-10 py-8 flex flex-col md:flex-row justify-between items-center gap-6 border-b border-white/5">
                        <div className="flex items-center gap-6">
                            <div className="w-14 h-14 bg-red-600 rounded-3xl flex items-center justify-center shadow-[0_10px_20px_rgba(220,38,38,0.2)] transform -rotate-3 hover:rotate-0 transition-transform cursor-pointer">
                                <span className="text-white text-3xl font-black italic tracking-tighter">!</span>
                            </div>
                            <div>
                                <h1 className="text-3xl font-black italic tracking-tighter text-white">CYBER<span className="text-red-500">RANT</span> <span className="text-slate-600 font-medium not-italic ml-2 text-xl">V-LABS</span></h1>
                                <p className="text-[10px] text-slate-500 uppercase tracking-[0.4em] font-black mt-1">Advanced Threat Intelligence • Agent Control</p>
                            </div>
                        </div>
                        <StateBadge state={state} />
                    </div>

                    <div className="p-10">
                        <div className="grid grid-cols-1 lg:grid-cols-12 gap-10 mb-12">
                            {/* Agent Selection */}
                            <div className="lg:col-span-8">
                                <label className="block text-[10px] font-black text-slate-400 uppercase mb-4 tracking-widest pl-1">Target Intelligence Node</label>
                                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                                    {AGENTS.map(agent => (
                                        <button
                                            key={agent.id}
                                            onClick={() => setSelectedAgent(agent)}
                                            className={`group relative p-5 rounded-[1.75rem] border-[3px] transition-all duration-500 ${selectedAgent.id === agent.id
                                                ? "border-red-600 bg-red-50/20 shadow-[0_15px_30px_rgba(220,38,38,0.03)]"
                                                : "border-slate-50 bg-slate-50/30 hover:border-slate-200"
                                                }`}
                                        >
                                            <div className="flex items-center gap-4">
                                                <div className={`w-12 h-12 rounded-2xl flex items-center justify-center font-black text-lg transition-all ${selectedAgent.id === agent.id ? "bg-red-600 text-white shadow-lg shadow-red-500/20" : "bg-slate-200 text-slate-400 group-hover:bg-slate-300 group-hover:text-slate-500"}`}>
                                                    {agent.id[0]}
                                                </div>
                                                <div className="text-left">
                                                    <p className={`text-sm font-black tracking-tight ${selectedAgent.id === agent.id ? "text-slate-900" : "text-slate-500"}`}>{agent.name}</p>
                                                    <p className="text-[10px] text-slate-400 font-black mt-0.5 tracking-wider uppercase opacity-70">
                                                        {agent.type === 'guidance' ? '○ Learning Module' : '○ Action Protocol'}
                                                    </p>
                                                </div>
                                            </div>
                                        </button>
                                    ))}
                                </div>
                            </div>

                            {/* Status Info */}
                            <div className="lg:col-span-4">
                                <label className="block text-[10px] font-black text-slate-400 uppercase mb-4 tracking-widest pl-1">System Entropy</label>
                                <div className="p-6 bg-slate-950 rounded-[1.75rem] border border-white/5 shadow-2xl relative overflow-hidden group">
                                    <div className="absolute top-0 right-0 p-2 opacity-10">
                                        <div className="w-16 h-16 border-4 border-red-500 rounded-full animate-ping" />
                                    </div>
                                    <ul className="space-y-4 text-[10px] text-slate-400 font-black uppercase tracking-widest relative z-10">
                                        <li className="flex items-center justify-between">
                                            <span>Red-Line Policy</span>
                                            <span className="text-emerald-500">ACTIVE</span>
                                        </li>
                                        <li className="flex items-center justify-between">
                                            <span>HITL Buffer</span>
                                            <span className="text-emerald-500">ENABLED</span>
                                        </li>
                                        <li className="flex items-center justify-between">
                                            <span>Zero-Trust Auth</span>
                                            <span className="text-red-500">LOCKED</span>
                                        </li>
                                    </ul>
                                </div>
                            </div>
                        </div>

                        {/* Query Input */}
                        <div className="mb-10 relative">
                            <label className="block text-[10px] font-black text-slate-400 uppercase mb-4 tracking-widest pl-1">Input Natural Language Intent</label>
                            <div className="group relative">
                                <textarea
                                    className="w-full bg-slate-50/50 border-[3px] border-slate-50 focus:border-red-600 focus:bg-white p-8 rounded-[2rem] text-sm font-bold transition-all duration-500 outline-none min-h-[180px] shadow-inner text-slate-800 placeholder:text-slate-200 placeholder:font-black"
                                    placeholder="e.g., 'Analyze the recent breach attempt at Node-C...'"
                                    value={query}
                                    onChange={(e) => setQuery(e.target.value)}
                                    disabled={state === "SYSTEM_OFFLINE" || state === "PROCESSING"}
                                />
                                <div className="absolute bottom-6 right-8 text-[9px] font-black text-slate-300 uppercase tracking-[0.2em] bg-white px-3 py-1 rounded-full border border-slate-50 shadow-sm">
                                    {query.length} SYMBOLS
                                </div>
                            </div>
                        </div>

                        {/* Controls */}
                        <div className="flex flex-col sm:flex-row gap-5">
                            <button
                                onClick={handleExecute}
                                disabled={!query || state === "SYSTEM_OFFLINE" || state === "PROCESSING"}
                                className={`flex-[2.5] py-6 rounded-3xl text-white font-black uppercase tracking-[0.4em] text-xs transition-all duration-500 shadow-2xl active:scale-[0.97] disabled:active:scale-100 ${!query || state === "SYSTEM_OFFLINE" || state === "PROCESSING"
                                    ? "bg-slate-100 text-slate-300 cursor-not-allowed shadow-none"
                                    : "bg-red-600 hover:bg-slate-950 shadow-red-600/20"
                                    }`}
                            >
                                <span className="flex items-center justify-center gap-3">
                                    {state === "PROCESSING" && <div className="w-5 h-5 border-2 border-white/20 border-t-white rounded-full animate-spin" />}
                                    {state === "PROCESSING" ? "DECIPHERING..." : "DISPATCH SIGNAL"}
                                </span>
                            </button>
                            <button
                                onClick={() => { setQuery(""); setLastResponse(null); setState("IDLE"); }}
                                className="flex-1 py-6 bg-white hover:bg-slate-50 text-slate-400 border-[3px] border-slate-50 font-black uppercase tracking-[0.3em] text-[9px] rounded-3xl transition-all duration-300 active:scale-[0.97]"
                            >
                                PURGE BUFFER
                            </button>
                        </div>
                    </div>
                </div>

                {/* Response Container */}
                <div id="response-anchor" className="scroll-mt-10">
                    <ResponseViewer response={lastResponse} />
                </div>

                <div className="mt-16 text-center space-y-2">
                    <div className="w-10 h-0.5 bg-slate-100 mx-auto mb-6" />
                    <p className="text-slate-300 text-[9px] font-black uppercase tracking-[0.5em]">
                        CyberRant Enterprise Intelligence Gateway v4.2.1
                    </p>
                    <p className="text-slate-200 text-[8px] font-black uppercase tracking-[0.2em]">
                        Securing Infrastructure for a Post-Human Future
                    </p>
                </div>
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
