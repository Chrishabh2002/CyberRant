import React from 'react';

export default function ApprovalModal({ isOpen, plan, onApprove, onReject }) {
    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-md flex items-center justify-center z-[100] p-4 animate-in fade-in duration-300">
            <div className="bg-white rounded-[2.5rem] shadow-[0_25px_50px_-12px_rgba(0,0,0,0.5)] max-w-lg w-full overflow-hidden border border-slate-100 animate-in zoom-in-95 slide-in-from-bottom-8 duration-500">
                <div className="bg-slate-950 p-8 text-center border-b border-white/5">
                    <div className="w-16 h-16 bg-amber-500 rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-xl shadow-amber-500/20">
                        <span className="text-slate-900 text-3xl font-black italic">!</span>
                    </div>
                    <h2 className="text-xl font-black text-white italic tracking-tight uppercase">Manual Intervention Required</h2>
                    <p className="text-[10px] text-slate-500 font-black uppercase tracking-[0.3em] mt-2">Operational Safety Buffer • Level 4 Approval</p>
                </div>

                <div className="p-10">
                    <p className="text-sm text-slate-600 font-medium leading-relaxed mb-8 text-center italic">
                        The <strong>Rant AI Agent</strong> has formulated a remediation plan for the current threat profile. Human authorization is mandatory for deployment.
                    </p>

                    <div className="space-y-4 mb-10">
                        <label className="block text-[10px] font-black text-slate-400 uppercase tracking-widest pl-1">Proposed Execution Parameters</label>
                        <div className="bg-slate-50 rounded-3xl p-6 border-2 border-slate-100 shadow-inner group">
                            <div className="grid grid-cols-2 gap-4">
                                <ApprovalItem label="Operation" value={plan?.action || plan?.operation} highlight />
                                <ApprovalItem label="Entity ID" value={plan?.entity_id || plan?.entity} />
                                <ApprovalItem label="Risk Vector" value={plan?.risk || plan?.risk_score} danger={plan?.risk === 'HIGH' || plan?.risk_score > 0.7} />
                                <ApprovalItem label="Policy Ref" value="CR-OP-SEC-9" />
                            </div>
                            <div className="mt-6 pt-6 border-t border-slate-200">
                                <p className="text-[9px] font-black text-slate-400 uppercase tracking-widest mb-2">Justification</p>
                                <p className="text-xs font-bold text-slate-700 italic">"{plan?.justification || 'No justification provided by agent.'}"</p>
                            </div>
                        </div>
                    </div>

                    <div className="flex flex-col sm:flex-row gap-4">
                        <button
                            onClick={onReject}
                            className="flex-1 py-5 bg-white hover:bg-slate-50 text-slate-400 border-[3px] border-slate-50 font-black uppercase tracking-[0.2em] text-[10px] rounded-3xl transition-all active:scale-[0.97]"
                        >
                            Abort Signal
                        </button>
                        <button
                            onClick={onApprove}
                            className="flex-[1.5] py-5 bg-red-600 hover:bg-slate-950 text-white font-black uppercase tracking-[0.3em] text-[10px] rounded-3xl transition-all shadow-2xl shadow-red-500/20 active:scale-[0.97]"
                        >
                            Authorize Deployment
                        </button>
                    </div>
                </div>

                <div className="bg-slate-50 py-4 text-center border-t border-slate-100">
                    <p className="text-[8px] font-black text-slate-300 uppercase tracking-widest">Decision Hash: CR-{Math.random().toString(36).substring(7).toUpperCase()}</p>
                </div>
            </div>
        </div>
    );
}

function ApprovalItem({ label, value, highlight, danger }) {
    return (
        <div>
            <p className="text-[8px] font-black text-slate-400 uppercase tracking-widest mb-1">{label}</p>
            <p className={`text-xs font-black truncate ${highlight ? 'text-blue-600' : danger ? 'text-red-500' : 'text-slate-900'}`}>{value || 'UNKNOWN'}</p>
        </div>
    );
}
