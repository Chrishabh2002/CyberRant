import React, { useEffect, useState } from 'react';
import { socket } from '../api/socket'; // Assuming socket.io-client is available

export default function CyberWorldMap({ onStatusUpdate }) {
    const [ecosystem, setEcosystem] = useState({ nodes: {}, global_threat_level: "LOW", active_missions: 0 });
    const [thoughts, setThoughts] = useState([]);

    useEffect(() => {
        // Listen for live ecosystem updates
        const onEcosystemUpdate = (data) => {
            setEcosystem(data);
            if (onStatusUpdate) {
                onStatusUpdate(data.nodes && Object.keys(data.nodes).length > 0);
            }
        };

        const onCognitiveEvent = (event) => {
            setThoughts(prev => [event, ...prev].slice(0, 4));
        };

        socket.on("ecosystem_update", onEcosystemUpdate);
        socket.on("cognitive_event", onCognitiveEvent);

        return () => {
            socket.off("ecosystem_update", onEcosystemUpdate);
            socket.off("cognitive_event", onCognitiveEvent);
        };
    }, []);

    const nodes = Object.entries(ecosystem.nodes);

    return (
        <div className="bg-slate-950 rounded-[2.5rem] p-8 border border-white/5 shadow-2xl overflow-hidden relative group">
            <div className="absolute top-0 right-0 p-8 opacity-20 pointer-events-none">
                <div className="w-64 h-64 border-2 border-red-500 rounded-full animate-[ping_10s_infinite]" />
            </div>

            <div className="flex justify-between items-center mb-10 relative z-10">
                <div>
                    <h2 className="text-xl font-black italic tracking-tighter text-white">VIRTUAL <span className="text-red-500">WORLD</span> CORE</h2>
                    <p className="text-[10px] text-slate-500 font-bold uppercase tracking-[0.4em] mt-1">Live Autonomous Ecosystem Telemetry</p>
                </div>
                <div className="flex gap-10">
                    <div className="flex gap-4">
                        <Safeguard label="Neural Shielding" active={true} />
                        <Safeguard label="Entropy Stabilizer" active={true} />
                        <Safeguard label="Zero-Trust Bridge" active={ecosystem.nodes && Object.keys(ecosystem.nodes).length > 0} />
                    </div>
                    <div className="flex gap-6 border-l border-white/5 pl-10">
                        <div className="text-right">
                            <p className="text-[8px] text-slate-500 font-black uppercase tracking-widest">Global Threat</p>
                            <p className="text-xs font-black text-emerald-500 uppercase">{ecosystem.global_threat_level}</p>
                        </div>
                        <div className="text-right">
                            <p className="text-[8px] text-slate-500 font-black uppercase tracking-widest">Active Missions</p>
                            <p className="text-xs font-black text-red-500 animate-pulse">{ecosystem.active_missions}</p>
                        </div>
                    </div>
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 relative z-10">
                {nodes.length > 0 ? nodes.map(([id, node]) => (
                    <div key={id} className="p-6 bg-white/5 rounded-3xl border border-white/5 hover:border-red-500/30 transition-all duration-500 group overflow-hidden relative">
                        <div className="absolute -bottom-1 -right-1 w-12 h-12 bg-red-500/5 rounded-full blur-xl group-hover:bg-red-500/20 transition-all" />

                        <div className="flex justify-between items-start mb-6">
                            <div className="w-10 h-10 bg-slate-800 rounded-2xl flex items-center justify-center text-xl shadow-inner italic font-black text-red-500">N</div>
                            <span className="text-[8px] font-black text-emerald-500 bg-emerald-500/10 px-2 py-1 rounded uppercase tracking-widest">Online</span>
                        </div>

                        <h3 className="text-xs font-black text-slate-200 uppercase tracking-widest mb-4 truncate">{id}</h3>

                        <div className="space-y-4">
                            <StatBar label="Neural CPU" value={node.stats.cpu} color="bg-red-500" />
                            <StatBar label="Memory Sync" value={node.stats.memory} color="bg-blue-500" />
                            <StatBar label="Disk Load" value={node.stats.disk} color="bg-slate-500" />
                        </div>

                        <div className="mt-6 flex justify-between items-center text-[7px] font-black text-slate-600 uppercase tracking-widest">
                            <span>Latency: 24ms</span>
                            <span>Region: Sandbox-7</span>
                        </div>
                    </div>
                )) : (
                    <div className="col-span-full py-20 flex flex-col items-center justify-center border-2 border-dashed border-white/5 rounded-[2rem] opacity-30">
                        <span className="text-4xl mb-4">🌐</span>
                        <p className="text-xs font-black uppercase tracking-[0.3em] text-slate-500">Awaiting Neural Link to Virtual World...</p>
                    </div>
                )}
            </div>

            {/* Neural Thought Stream */}
            <div className="mt-10 p-5 bg-slate-900/80 rounded-3xl border border-white/5 relative overflow-hidden">
                <div className="absolute top-0 right-0 p-3">
                    <div className="text-[7px] font-black text-slate-700 uppercase tracking-widest">Ambient Neural Stream</div>
                </div>
                <div className="flex flex-col gap-3">
                    {thoughts.length > 0 ? thoughts.map((t, idx) => (
                        <div key={idx} className="flex items-center gap-3 animate-in slide-in-from-left duration-700" style={{ opacity: 1 - idx * 0.2 }}>
                            <div className="w-1.5 h-1.5 bg-red-600 rounded-full animate-pulse shadow-[0_0_5px_rgba(220,38,38,0.5)]" />
                            <p className="text-[10px] font-mono text-slate-400">
                                <span className="text-slate-600">[{new Date(t.timestamp * 1000).toLocaleTimeString()}]</span> {t.message}
                            </p>
                        </div>
                    )) : (
                        <div className="flex items-center gap-3 opacity-30">
                            <div className="w-1.5 h-1.5 bg-slate-700 rounded-full" />
                            <p className="text-[10px] font-mono text-slate-600 italic">Synchronizing neural awareness baseline...</p>
                        </div>
                    )}
                </div>
            </div>

            <div className="mt-8 pt-6 border-t border-white/5 flex justify-between items-center relative z-10">
                <div className="flex gap-4 items-center">
                    <div className="flex -space-x-2">
                        {[1, 2, 3].map(i => (
                            <div key={i} className="w-6 h-6 rounded-full border-2 border-slate-950 bg-slate-800 flex items-center justify-center text-[8px] font-black text-slate-400 uppercase">A{i}</div>
                        ))}
                    </div>
                    <span className="text-[8px] font-black text-slate-500 uppercase tracking-widest">Simulated Agents Active</span>
                </div>
                <div className="text-[7px] font-mono text-slate-700 uppercase tracking-widest">
                    Kernel: CyberOS-4.9.2-RT | Entropy: Balanced
                </div>
            </div>
        </div>
    );
}

function Safeguard({ label, active }) {
    return (
        <div className={`px-4 py-2 rounded-2xl border flex items-center gap-3 transition-all duration-500 ${active ? 'bg-white/5 border-white/5 opacity-100' : 'bg-transparent border-white/5 opacity-20'}`}>
            <div className={`w-1.5 h-1.5 rounded-full ${active ? 'bg-red-500 animate-pulse shadow-[0_0_8px_rgba(239,68,68,0.5)]' : 'bg-slate-700'}`} />
            <span className="text-[9px] font-black text-slate-400 uppercase tracking-widest">{label}</span>
        </div>
    );
}

function StatBar({ label, value, color }) {
    return (
        <div className="space-y-1.5">
            <div className="flex justify-between items-center text-[8px] font-black text-slate-500 uppercase tracking-tighter px-0.5">
                <span>{label}</span>
                <span>{value}%</span>
            </div>
            <div className="h-1 w-full bg-slate-900 rounded-full overflow-hidden shadow-inner">
                <div
                    className={`h-full ${color} transition-all duration-1000 ease-out shadow-[0_0_10px_rgba(0,0,0,0.5)]`}
                    style={{ width: `${value}%` }}
                />
            </div>
        </div>
    );
}
