import React, { useEffect, useRef } from 'react';

export default function TerminalView({ logs, status }) {
    const scrollRef = useRef(null);

    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, [logs]);

    return (
        <div className="bg-slate-950 rounded-[2rem] border border-white/10 overflow-hidden shadow-2xl animate-in zoom-in-95 duration-500">
            {/* Terminal Header */}
            <div className="bg-slate-900 px-6 py-4 flex items-center justify-between border-b border-white/5">
                <div className="flex items-center gap-3">
                    <div className="flex gap-1.5">
                        <div className="w-2.5 h-2.5 rounded-full bg-red-500/50" />
                        <div className="w-2.5 h-2.5 rounded-full bg-amber-500/50" />
                        <div className="w-2.5 h-2.5 rounded-full bg-emerald-500/50" />
                    </div>
                    <span className="text-[10px] font-black text-slate-500 uppercase tracking-[0.3em] ml-2">Secure Shell Terminal v1.02</span>
                </div>
                <div className="flex items-center gap-3">
                    <div className={`px-2 py-0.5 rounded text-[8px] font-black uppercase tracking-tighter ${status === 'EXECUTING' ? 'bg-cyan-500/10 text-cyan-400 animate-pulse' : status === 'PROCESSING' ? 'bg-blue-500/10 text-blue-400 animate-pulse' : 'bg-emerald-500/10 text-emerald-400'}`}>
                        {status}
                    </div>
                </div>
            </div>

            {/* Terminal Body */}
            <div
                ref={scrollRef}
                className="p-6 h-[400px] overflow-y-auto font-mono text-[12px] leading-relaxed selection:bg-cyan-500/30 selection:text-white"
            >
                {logs && logs.length > 0 ? (
                    <div className="space-y-1">
                        {logs.map((log, i) => (
                            <div key={i} className="flex gap-4">
                                <span className="text-slate-600 select-none w-6 text-right opacity-30">{i + 1}</span>
                                <span className={log.startsWith('[!]') ? 'text-red-400' : log.startsWith('[+]') ? 'text-emerald-400' : log.startsWith('[*]') ? 'text-blue-400' : 'text-slate-300'}>
                                    {log}
                                </span>
                            </div>
                        ))}
                        {status === 'EXECUTING' && (
                            <div className="flex gap-4 items-center">
                                <span className="text-slate-600 select-none w-6 text-right opacity-30">{logs.length + 1}</span>
                                <span className="text-cyan-400 animate-pulse">[WAITING FOR IO]</span>
                                <span className="w-2 h-4 bg-cyan-500 animate-pulse" />
                            </div>
                        )}
                        {status === 'PROCESSING' && (
                            <div className="space-y-1">
                                <div className="flex gap-4">
                                    <span className="text-slate-600 select-none w-6 text-right opacity-30">{logs.length + 1}</span>
                                    <span className="text-blue-400">[*] Finalizing telemetry integrity check... Done.</span>
                                </div>
                                <div className="flex gap-4">
                                    <span className="text-slate-600 select-none w-6 text-right opacity-30">{logs.length + 2}</span>
                                    <span className="text-blue-400 animate-pulse">[*] Synthesizing executive briefing via CyberRant AI...</span>
                                </div>
                            </div>
                        )}
                    </div>
                ) : (
                    <div className="h-full flex flex-col items-center justify-center text-center space-y-4 opacity-30">
                        <div className="w-12 h-12 border-2 border-slate-700 rounded-full border-t-slate-500 animate-spin" />
                        <p className="text-[10px] font-black uppercase tracking-[0.3em] text-slate-500">Initializing Secure Bridge...</p>
                    </div>
                )}
            </div>

            {/* Terminal Footer */}
            <div className="bg-slate-900/50 px-6 py-3 flex items-center justify-between text-[8px] font-black text-slate-600 uppercase tracking-widest border-t border-white/5">
                <span>CyberRant SOC Environment</span>
                <span>Connection: Encrypted (AES-256)</span>
            </div>
        </div>
    );
}
