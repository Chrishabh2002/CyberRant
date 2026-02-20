import React, { useEffect, useState } from 'react';
import { agentApi } from '../api/agentApi';

export default function MissionDashboard({ response, state, isOnline, originalQuery }) {
    const [files, setFiles] = useState([]);

    useEffect(() => {
        if (response?.trace_id && (response?.execution_available || isOnline)) {
            // Initial poll
            agentApi.getSandboxFiles(response.trace_id);

            // Refresh on status changes
            const interval = setInterval(() => {
                if (response.trace_id) {
                    setFiles(response.sandbox_files || []);
                }
            }, 2000);
            return () => clearInterval(interval);
        }
    }, [response?.trace_id, response?.sandbox_files, isOnline]);

    if (!response || response.agent_type === 'ASK_RANT') return null;

    const { intent, risk, phases, mode, execution_available } = response;
    const finalOnlineStatus = isOnline !== undefined ? isOnline : execution_available;
    const displayIntent = (intent && intent.length > 15 && intent !== "System Query") ? intent : originalQuery;

    return (
        <div className="mt-8 bg-slate-950 rounded-[2rem] border border-white/5 overflow-hidden shadow-2xl animate-in zoom-in-95 duration-500 font-sans">
            <div className="px-8 py-6 border-b border-white/5 flex justify-between items-center bg-gradient-to-r from-slate-950 to-slate-900">
                <div className="flex items-center gap-4">
                    <div className="w-3 h-3 bg-red-500 rounded-full animate-pulse shadow-[0_0_10px_rgba(239,68,68,0.5)]" />
                    <h2 className="text-[10px] font-black text-white uppercase tracking-[0.4em]">Autonomous Mission Ecosystem</h2>
                </div>
                <div className="flex items-center gap-6">
                    <div className="text-right">
                        <p className="text-[8px] text-slate-500 font-black uppercase tracking-widest">Environment Status</p>
                        <p className={`text-[10px] font-black ${finalOnlineStatus ? 'text-emerald-500' : 'text-red-500'} uppercase mt-0.5`}>
                            {finalOnlineStatus ? 'BRIDGE READY' : 'BRIDGE OFFLINE'}
                        </p>
                    </div>
                </div>
            </div>

            <div className="p-8 grid grid-cols-1 lg:grid-cols-12 gap-10">
                {/* Intent & Context */}
                <div className="lg:col-span-4 space-y-8">
                    <div>
                        <label className="text-[9px] font-black text-slate-500 uppercase tracking-widest block mb-4">Tactical Objective</label>
                        <div className="p-5 bg-white/5 rounded-2x border border-white/5 relative overflow-hidden group">
                            <div className="absolute top-0 left-0 w-1 h-full bg-red-600 opacity-50 group-hover:opacity-100 transition-opacity" />
                            <p className="text-[11px] font-bold text-slate-200 leading-relaxed italic">
                                "{displayIntent || "Intelligence analysis in progress..."}"
                            </p>
                        </div>
                    </div>

                    <div>
                        <label className="text-[9px] font-black text-slate-500 uppercase tracking-widest block mb-4">Ecosystem Artifacts</label>
                        <div className="space-y-2 max-h-[200px] overflow-y-auto pr-2 custom-scrollbar">
                            {(files.length > 0) ? files.map((file, idx) => (
                                <div key={idx} className="flex items-center justify-between p-3 bg-slate-900/50 rounded-xl border border-white/5 hover:border-red-500/20 transition-colors group">
                                    <div className="flex items-center gap-3">
                                        <div className="w-6 h-6 bg-slate-800 rounded-lg flex items-center justify-center text-[10px]">
                                            {file.is_dir ? '📁' : '📄'}
                                        </div>
                                        <div>
                                            <p className="text-[10px] font-bold text-slate-300 group-hover:text-white transition-colors capitalize">{file.name}</p>
                                            <p className="text-[8px] text-slate-600 font-black">{(file.size / 1024).toFixed(1)} KB</p>
                                        </div>
                                    </div>
                                    <div className="w-2 h-2 rounded-full bg-emerald-500 opacity-20 group-hover:opacity-100 transition-opacity" />
                                </div>
                            )) : (
                                <div className="p-8 border-2 border-dashed border-white/5 rounded-2xl flex flex-col items-center justify-center text-center">
                                    <span className="text-xl mb-2 opacity-20">📥</span>
                                    <p className="text-[9px] text-slate-600 font-black uppercase tracking-widest">No Artifacts Generated</p>
                                </div>
                            )}
                        </div>
                    </div>
                </div>

                {/* Phase Roadmap */}
                <div className="lg:col-span-8">
                    <label className="text-[9px] font-black text-slate-500 uppercase tracking-widest block mb-6">Mission Phase Decomposition</label>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                        {(phases || []).map((phase, idx) => (
                            <div key={idx} className={`relative p-6 rounded-[1.75rem] border transition-all duration-500 group ${phase.permission_required ? 'bg-red-950/20 border-red-500/10 hover:border-red-500/30' : 'bg-slate-900/40 border-white/5 opacity-60'}`}>
                                <div className="flex justify-between items-start mb-4">
                                    <span className={`text-[10px] font-black italic tracking-tighter ${phase.permission_required ? 'text-red-500' : 'text-slate-700'}`}>PHASE_0{idx + 1}</span>
                                    {phase.permission_required && (
                                        <span className="text-[8px] font-black text-white bg-red-600 px-3 py-1 rounded-full uppercase tracking-widest shadow-lg shadow-red-600/20">Authorization Lock</span>
                                    )}
                                </div>
                                <h3 className="text-sm font-black text-slate-100 group-hover:translate-x-1 transition-transform">{phase.name}</h3>
                                <p className="text-[9px] text-slate-500 font-bold mt-2 leading-relaxed">
                                    {phase.permission_required ? "Governance boundary requires physical operator signing to proceed." : "Autonomous sub-routine active... No block detected."}
                                </p>
                            </div>
                        ))}
                    </div>
                </div>
            </div>

            <div className="bg-white/5 p-4 flex justify-between items-center text-[8px] font-black text-slate-500 uppercase tracking-[0.4em] px-8 border-t border-white/5">
                <span className="flex items-center gap-2">
                    <span className="w-1.5 h-1.5 bg-emerald-500 rounded-full animate-pulse" />
                    INTELLIGENCE NODE: CyberRant-V-Labs-Edge-01
                </span>
                <span className="flex items-center gap-4">
                    <span>Buffer Load</span>
                    <div className="w-32 h-1 bg-slate-900 rounded-full overflow-hidden">
                        <div className="w-2/3 h-full bg-red-600 animate-pulse" />
                    </div>
                </span>
            </div>
        </div>
    );
}
