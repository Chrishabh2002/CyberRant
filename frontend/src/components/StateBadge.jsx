import React from 'react';

const stateColors = {
    IDLE: "bg-gray-100 text-gray-800",
    PROCESSING: "bg-blue-100 text-blue-800 animate-pulse",
    AWAITING_APPROVAL: "bg-yellow-100 text-yellow-800 border border-yellow-400",
    APPROVAL_REQUIRED: "bg-yellow-100 text-yellow-800 border border-yellow-400",
    PARTIAL_SUCCESS: "bg-purple-100 text-purple-800",
    COMPLETED: "bg-green-100 text-green-800",
    BLOCKED: "bg-red-100 text-red-800",
    REFUSED: "bg-orange-100 text-orange-800",
    SYSTEM_OFFLINE: "bg-black text-white",
    ERROR: "bg-red-600 text-white",
};

export default function StateBadge({ state }) {
    const normalizedState = (state || "IDLE").toUpperCase();
    const colorClass = stateColors[normalizedState] || "bg-gray-100 text-gray-800";

    return (
        <span className={`px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider ${colorClass}`}>
            {state.replace(/_/g, " ")}
        </span>
    );
}
