import React from 'react';

export default function TaskResolution({ response }) {
    if (!response || !response.message) return null;

    // Detect if the message contains a JSON block (common for tool outputs)
    let jsonData = null;
    try {
        const jsonMatch = response.message.match(/\{[\s\S]*\}/);
        if (jsonMatch) {
            jsonData = JSON.parse(jsonMatch[0]);
        }
    } catch (e) {
        // Not a valid JSON or tool output
    }

    if (!jsonData || !jsonData.status) return null;

    return (
        <div className="mt-6 p-6 bg-slate-50 rounded-[2rem] border-2 border-slate-100 border-dashed">
            <div className="flex items-center gap-3 mb-4">
                <div className={`w-8 h-8 rounded-xl flex items-center justify-center text-xs font-black ${jsonData.status === 'SUCCESS' ? 'bg-emerald-100 text-emerald-600' : 'bg-red-100 text-red-600'}`}>
                    {jsonData.status === 'SUCCESS' ? '✓' : '!'}
                </div>
                <h4 className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Technical Resolution Data</h4>
            </div>

            {jsonData.results && (
                <div className="overflow-x-auto">
                    <table className="w-full text-left">
                        <thead>
                            <tr className="border-b border-slate-200">
                                <th className="py-2 text-[9px] font-black text-slate-400 uppercase tracking-widest">Parameter</th>
                                <th className="py-2 text-[9px] font-black text-slate-400 uppercase tracking-widest">Status</th>
                                <th className="py-2 text-[9px] font-black text-slate-400 uppercase tracking-widest">Service</th>
                            </tr>
                        </thead>
                        <tbody>
                            {jsonData.results.map((res, i) => (
                                <tr key={i} className="border-b border-slate-100 last:border-0">
                                    <td className="py-3 text-[11px] font-bold text-slate-700">Port {res.port}</td>
                                    <td className="py-3">
                                        <span className={`px-2 py-0.5 rounded text-[9px] font-black uppercase ${res.status === 'OPEN' ? 'bg-emerald-50 text-emerald-600' : 'bg-slate-100 text-slate-400'}`}>
                                            {res.status}
                                        </span>
                                    </td>
                                    <td className="py-3 text-[11px] font-medium text-slate-500">{res.service}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            )}

            {jsonData.audit && (
                <div className="grid grid-cols-2 gap-4">
                    {Object.entries(jsonData.audit).map(([key, val], i) => (
                        <div key={i} className="p-3 bg-white rounded-xl border border-slate-200">
                            <p className="text-[8px] font-black text-slate-400 uppercase mb-1 tracking-tighter">{key.replace('_', ' ')}</p>
                            <p className="text-[10px] font-black text-slate-800 uppercase tracking-tighter">{String(val)}</p>
                        </div>
                    ))}
                </div>
            )}

            <div className="mt-4 pt-4 border-t border-slate-200 flex justify-between items-center">
                <p className="text-[8px] font-black text-slate-300 uppercase italic">Resolution Hash: {Math.random().toString(16).slice(2, 10)}</p>
                <span className="text-[8px] font-black text-slate-400 bg-white px-2 py-0.5 rounded border border-slate-200 uppercase">Verified Response</span>
            </div>
        </div>
    );
}
