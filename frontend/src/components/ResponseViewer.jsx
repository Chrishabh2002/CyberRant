import React, { useState, useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { agentApi } from '../api/agentApi';
import TerminalView from './TerminalView';
import TaskResolution from './TaskResolution';
import MissionControl from './MissionControl';

export default function ResponseViewer({ response }) {
    const [showTechnical, setShowTechnical] = useState(false);
    const [responseState, setResponseState] = useState(response?.state || 'IDLE');
    const [mediaStatus, setMediaStatus] = useState(response?.media_status || null);
    const [mediaAssets, setMediaAssets] = useState(response?.media_assets || null);
    const [executionLogs, setExecutionLogs] = useState(response?.logs || []);
    const [activeTab, setActiveTab] = useState('BRIEFING'); // BRIEFING | TERMINAL
    const pollInterval = useRef(null);

    const [fullResponse, setFullResponse] = useState(response);

    // Sync state when initial response changes
    useEffect(() => {
        setFullResponse(response);
        setResponseState(response?.state || 'IDLE');
        setMediaStatus(response?.media_status || null);
        setMediaAssets(response?.media_assets || null);
        setExecutionLogs(response?.logs || []);

        // Auto-switch to terminal if executing
        if (response?.state === 'EXECUTING') {
            setActiveTab('TERMINAL');
        } else {
            setActiveTab('BRIEFING');
        }
    }, [response]);

    // Media & Assets Sync
    useEffect(() => {
        if (response?.media_status) {
            setMediaStatus(response.media_status);
            const { audio_status, video_status, audio_url, video_url } = response.media_status;
            const isPendingMedia = (s) => s === 'QUEUED' || s === 'PROCESSING' || s === 'PENDING';

            if (!isPendingMedia(audio_status) && !isPendingMedia(video_status) && (audio_url || video_url)) {
                setMediaAssets({
                    audio_url: audio_url ? `${agentApi.API_BASE_URL}${audio_url}?t=${Date.now()}` : null,
                    video_url: video_url ? `${agentApi.API_BASE_URL}${video_url}?t=${Date.now()}` : null
                });
            }
        }
    }, [response?.media_status]);

    if (!fullResponse) return null;

    const { state: originalState, message, output, trace_id, severity, error } = fullResponse;
    const state = responseState || originalState;

    // Normalize content (backend uses 'message' or 'output')
    const mainContent = output || message || "";

    // State mapping for visual feedback (Normalized SOC-grade set)
    const stateConfig = {
        BLOCKED: { banner: "bg-red-50 border-red-200 text-red-800", title: "Security Buffer Active", icon: "🛡️" },
        PROCESSING: { banner: "bg-blue-50 border-blue-200 text-blue-800", title: "Analysis in Progress", icon: "⚙️" },
        "TEXT READY": { banner: "bg-blue-50 border-blue-200 text-blue-800", title: "Intelligence Captured", icon: "📄" },
        "MEDIA READY": { banner: "bg-green-50 border-green-200 text-green-800", title: "Operational Briefing Enhanced", icon: "✅" },
        COMPLETED: { banner: "bg-green-50 border-green-200 text-green-800", title: "Briefing Finalized", icon: "✅" },
        AWAITING_APPROVAL: { banner: "bg-amber-50 border-amber-200 text-amber-900", title: "Operator Signing Required", icon: "🛡️" },
        EXECUTING: { banner: "bg-red-50 border-red-200 text-red-800", title: "Mission Dispatched", icon: "⚡" },
        FAILED: { banner: "bg-slate-900 border-white/10 text-slate-400", title: "Mission Standby", icon: "⏸️" }
    };

    const config = stateConfig[state?.toUpperCase()] || { banner: "bg-slate-50 border-slate-200", title: "System Insight", icon: "📋" };

    const isPending = (status) => status === 'QUEUED' || status === 'PROCESSING' || status === 'PENDING';

    return (
        <div className="mt-8 space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
            {/* Tab Navigation */}
            <div className="flex items-center gap-2 px-1">
                <button
                    onClick={() => setActiveTab('BRIEFING')}
                    className={`px-6 py-2 rounded-xl text-[10px] font-black uppercase tracking-widest transition-all ${activeTab === 'BRIEFING' ? 'bg-slate-900 text-white shadow-lg' : 'text-slate-400 hover:text-slate-600'}`}
                >
                    Strategic Briefing
                </button>
                <button
                    onClick={() => setActiveTab('TERMINAL')}
                    className={`px-6 py-2 rounded-xl text-[10px] font-black uppercase tracking-widest transition-all flex items-center gap-2 ${activeTab === 'TERMINAL' ? 'bg-slate-900 text-white shadow-lg' : 'text-slate-400 hover:text-slate-600'}`}
                >
                    Live Terminal
                    {state === 'EXECUTING' && <div className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-ping" />}
                </button>
            </div>

            {/* Content Area */}
            {activeTab === 'BRIEFING' ? (
                <div className={`p-8 rounded-[2rem] border-[3px] shadow-sm ${config.banner} transition-all duration-700`}>
                    <div className="flex items-center gap-4 mb-4">
                        <div className="w-12 h-12 rounded-2xl bg-white shadow-xl flex items-center justify-center text-2xl">
                            {config.icon}
                        </div>
                        <div className="flex flex-col flex-1">
                            <div className="flex items-center justify-between">
                                <h3 className="font-black text-xs uppercase tracking-[0.3em] font-sans">{config.title}</h3>
                                {severity && (
                                    <span className={`text-[9px] font-black px-3 py-1 rounded-full uppercase tracking-widest border ${severity === 'CRITICAL' ? 'bg-purple-50 text-purple-700 border-purple-100' :
                                        severity === 'HIGH' ? 'bg-orange-50 text-orange-700 border-orange-100' :
                                            severity === 'MEDIUM' ? 'bg-blue-50 text-blue-700 border-blue-100' :
                                                'bg-slate-50 text-slate-500 border-slate-100'
                                        }`}>
                                        Severity: {severity}
                                    </span>
                                )}
                            </div>
                            <p className="text-[9px] font-bold text-slate-400 uppercase tracking-widest mt-0.5">Primary Intelligence Dispatch</p>
                        </div>
                    </div>

                    {/* Section A: Primary Intelligence */}
                    <div className="prose prose-sm max-w-none text-slate-800 leading-relaxed font-medium mt-4">
                        {mainContent.includes("MISSION INTEGRITY SIGNATURE") && (
                            <div className="mb-6 flex items-center gap-3 p-3 bg-amber-500/5 border border-amber-500/20 rounded-2xl animate-in zoom-in-95 duration-700">
                                <div className="w-8 h-8 rounded-lg bg-amber-500 flex items-center justify-center text-xs animate-pulse">🔒</div>
                                <div>
                                    <p className="text-[9px] font-black text-amber-600 uppercase tracking-[0.2em]">Verified Intelligence</p>
                                    <p className="text-[8px] font-mono text-amber-500/70 font-bold uppercase">
                                        {mainContent.split('\n')[0].replace('REPORT HEADER: ', '')}
                                    </p>
                                </div>
                                <div className="ml-auto flex items-center gap-1 px-2 py-0.5 bg-amber-500/10 rounded-md">
                                    <span className="w-1 h-1 rounded-full bg-amber-500 animate-ping" />
                                    <span className="text-[7px] font-black text-amber-600 uppercase">Live</span>
                                </div>
                            </div>
                        )}
                        <ReactMarkdown remarkPlugins={[remarkGfm]}>
                            {error ? `**Notice:** Intelligence could not be fully compiled. ${error}` :
                                mainContent.includes("MISSION INTEGRITY SIGNATURE") ? mainContent.split('\n').slice(1).join('\n') : mainContent}
                        </ReactMarkdown>
                        <TaskResolution response={response} />
                    </div>

                    {/* Mission Authorization Layer */}
                    {state === 'AWAITING_APPROVAL' && (
                        <div className="mt-10 animate-in slide-in-from-top-4 duration-700">
                            <MissionControl
                                traceId={trace_id}
                                onDecision={(decision, result) => {
                                    if (result) {
                                        setFullResponse(result);
                                        setResponseState(result.state);
                                    } else {
                                        if (decision === 'approve') setResponseState('EXECUTING');
                                        else setResponseState('COMPLETED');
                                    }
                                }}
                            />
                        </div>
                    )}

                    {/* Section B & C: Multimodal & Controls */}
                    {(mediaAssets || mediaStatus) && (
                        <div className="mt-10 grid grid-cols-1 md:grid-cols-2 gap-6 p-8 bg-white/40 rounded-[2rem] backdrop-blur-xl border-2 border-white/50 border-dashed">
                            {/* Audio Module */}
                            <div className="space-y-4">
                                <p className="text-[10px] font-black text-blue-600 uppercase tracking-widest pl-1">Audio Briefing</p>
                                {isPending(mediaStatus?.audio_status) ? (
                                    <MediaStatusCard label="Audio Rendering" type="AUDIO" />
                                ) : mediaAssets?.audio_url ? (
                                    <div className="space-y-3">
                                        <div className="flex items-center gap-2 px-4 py-2 bg-green-50 rounded-full border border-green-100 w-fit">
                                            <span className="text-[10px] font-black text-green-600 uppercase tracking-widest">Audio Ready</span>
                                        </div>
                                        <audio controls className="w-full h-12 rounded-2xl shadow-inner bg-white/50">
                                            <source src={mediaAssets.audio_url} type="audio/mpeg" />
                                        </audio>
                                    </div>
                                ) : mediaStatus?.audio_status === 'FAILED' ? (
                                    <div className="p-4 bg-slate-50 rounded-2xl border border-slate-100">
                                        <p className="text-[10px] font-bold text-slate-500 italic">Media summary unavailable. Text briefing is complete.</p>
                                    </div>
                                ) : null}
                            </div>

                            {/* Video Module */}
                            <div className="space-y-4">
                                <p className="text-[10px] font-black text-purple-600 uppercase tracking-widest pl-1">Visual Summary</p>
                                {isPending(mediaStatus?.video_status) ? (
                                    <MediaStatusCard label="Video Rendering" type="VIDEO" />
                                ) : mediaAssets?.video_url ? (
                                    <div className="space-y-3">
                                        <div className="flex items-center gap-2 px-4 py-2 bg-green-50 rounded-full border border-green-100 w-fit">
                                            <span className="text-[10px] font-black text-green-600 uppercase tracking-widest">Video Ready</span>
                                        </div>
                                        <div className="rounded-2xl overflow-hidden border-2 border-white shadow-2xl">
                                            <video controls className="w-full aspect-video bg-slate-900">
                                                <source src={mediaAssets.video_url} type="video/mp4" />
                                            </video>
                                        </div>
                                    </div>
                                ) : mediaStatus?.video_status === 'FAILED' ? (
                                    <div className="p-4 bg-slate-50 rounded-2xl border border-slate-100">
                                        <p className="text-[10px] font-bold text-slate-500 italic">Media summary unavailable. Text briefing is complete.</p>
                                    </div>
                                ) : (
                                    <div className="h-24 flex items-center justify-center bg-slate-100/50 rounded-2xl border-2 border-slate-50 border-dashed">
                                        <p className="text-[9px] font-black text-slate-300 uppercase tracking-widest italic">Media Optional</p>
                                    </div>
                                )}
                            </div>
                        </div>
                    )}
                </div>
            ) : (
                <TerminalView logs={executionLogs} status={state} />
            )}

            {/* Technical Toggle */}
            <div className="flex justify-center">
                <button
                    onClick={() => setShowTechnical(!showTechnical)}
                    className="flex items-center gap-3 px-6 py-3 rounded-2xl text-[9px] font-black uppercase tracking-[0.3em] text-slate-400 hover:text-red-600 hover:bg-red-50 transition-all border-2 border-slate-50"
                >
                    {showTechnical ? "Minimize Diagnostics" : "Initialize Diagnostic Overlay"}
                </button>
            </div>

            {/* Developer Mode View */}
            {showTechnical && (
                <div className="bg-slate-950 rounded-[2.5rem] p-8 overflow-hidden border border-white/5 shadow-2xl animate-in zoom-in-95 duration-300">
                    <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
                        <TechItem label="Trace ID" value={trace_id} />
                        <TechItem label="State" value={state} />
                        <TechItem label="Severity" value={severity || "N/A"} status={severity} />
                        <TechItem label="Media Status" value={JSON.stringify(mediaStatus)} />
                    </div>

                    <div>
                        <p className="text-[9px] font-black text-slate-500 uppercase mb-3 tracking-widest pl-1">Raw Intelligence Payload</p>
                        <pre className="p-6 bg-black/40 rounded-[1.5rem] text-emerald-400 text-[11px] font-mono overflow-auto max-h-[400px] border border-white/5 shadow-inner leading-relaxed">
                            {JSON.stringify(response, null, 2)}
                        </pre>
                    </div>
                </div>
            )}
        </div>
    );
}

function MediaStatusCard({ label, type }) {
    return (
        <div className="flex items-center gap-4 p-5 bg-white rounded-2xl border-2 border-slate-50 shadow-sm transition-all animate-pulse">
            <div className={`w-10 h-10 rounded-xl flex items-center justify-center text-white ${type === 'AUDIO' ? 'bg-blue-500' : 'bg-purple-500'}`}>
                {type === 'AUDIO' ? '🔊' : '🎬'}
            </div>
            <div>
                <p className="text-[10px] font-black text-slate-800 uppercase tracking-widest">{label}</p>
                <div className="h-1 w-24 bg-slate-100 rounded-full mt-2 overflow-hidden">
                    <div className="h-full bg-slate-300 animate-[loading_1.5s_infinite]" />
                </div>
            </div>
        </div>
    );
}

function TechItem({ label, value, status }) {
    const statusColors = { CRITICAL: "text-red-500", HIGH: "text-orange-500", MEDIUM: "text-amber-500", LOW: "text-emerald-500" };
    return (
        <div className="p-4 bg-white/5 rounded-2xl border border-white/5">
            <p className="text-[8px] font-black text-slate-600 uppercase tracking-widest mb-1.5">{label}</p>
            <p className={`text-[10px] font-mono break-all font-black uppercase tracking-tighter ${status ? statusColors[status.toUpperCase()] : "text-slate-300"}`}>
                {value || "-"}
            </p>
        </div>
    );
}
