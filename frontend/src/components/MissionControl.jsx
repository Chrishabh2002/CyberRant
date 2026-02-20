import React, { useState } from 'react';
import { agentApi } from '../api/agentApi';

export default function MissionControl({ traceId, onDecision }) {
    const [status, setStatus] = useState('PENDING'); // PENDING | SENDING | DONE

    const handleDecision = async (decision) => {
        setStatus('SENDING');
        try {
            const res = await agentApi.respondToApproval(traceId, decision);
            setStatus('DONE');
            if (onDecision) onDecision(decision, res);
        } catch (e) {
            console.error("Authorization failed", e);
            setStatus('PENDING');
        }
    };

    if (status === 'DONE') {
        return (
            <div className="mt-6 p-6 bg-emerald-50 rounded-[2rem] border-2 border-emerald-100 flex items-center justify-center gap-3 animate-in zoom-in-95">
                <div className="w-8 h-8 rounded-full bg-emerald-500 text-white flex items-center justify-center text-xl font-black">✓</div>
                <p className="text-xs font-black text-emerald-800 uppercase tracking-widest">Mission Authorized. Dispatching Agents...</p>
            </div>
        );
    }

    return (
        <div className="mt-8 p-10 bg-gradient-to-br from-amber-50 to-orange-50 rounded-[2.5rem] border-4 border-white shadow-2xl relative overflow-hidden group">
            <div className="absolute top-0 right-0 p-6 opacity-10">
                <span className="text-6xl font-black">🛡️</span>
            </div>

            <div className="relative z-10">
                <div className="flex items-center gap-4 mb-6">
                    <div className="w-12 h-12 rounded-2xl bg-amber-500 text-white flex items-center justify-center text-2xl shadow-lg animate-pulse">
                        🔑
                    </div>
                    <div>
                        <h3 className="text-sm font-black text-amber-900 uppercase tracking-[0.2em]">Operator Authorization Required</h3>
                        <p className="text-[10px] text-amber-700/60 font-bold uppercase tracking-widest mt-1 italic">Human-In-The-Loop Governance protocol active</p>
                    </div>
                </div>

                <p className="text-[11px] text-amber-900/80 leading-relaxed font-bold mb-8 max-w-2xl">
                    The agent is requesting permission to execute technical commands on your environment.
                    Review the <span className="text-amber-600">Operations Plan</span> above carefully before signing.
                </p>

                <div className="flex items-center gap-4">
                    <button
                        disabled={status === 'SENDING'}
                        onClick={() => handleDecision('approve')}
                        className="flex-1 bg-amber-600 hover:bg-amber-700 text-white py-4 rounded-2xl font-black text-xs uppercase tracking-[0.3em] transition-all shadow-xl shadow-amber-600/20 active:scale-95 flex items-center justify-center gap-3 border-b-4 border-amber-900/30"
                    >
                        {status === 'SENDING' ? 'Dispatching...' : 'Approve & Dispatch [✔]'}
                    </button>
                    <button
                        disabled={status === 'SENDING'}
                        onClick={() => handleDecision('reject')}
                        className="px-8 bg-white hover:bg-red-50 text-red-600 py-4 rounded-2xl font-black text-xs uppercase tracking-[0.3em] transition-all border-2 border-red-100 active:scale-95"
                    >
                        Abort [✖]
                    </button>
                </div>
            </div>

            {/* Security Disclaimer */}
            <div className="mt-6 pt-6 border-t border-amber-900/10 flex justify-between items-center opacity-40">
                <p className="text-[8px] font-black text-amber-900 uppercase tracking-widest">Zero-Trust Buffer: Active</p>
                <p className="text-[8px] font-black text-amber-900 uppercase tracking-widest">Trace ID: {traceId}</p>
            </div>
        </div>
    );
}
