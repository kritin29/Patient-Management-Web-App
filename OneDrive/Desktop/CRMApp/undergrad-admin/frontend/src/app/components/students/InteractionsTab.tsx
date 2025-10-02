'use client';

import React from 'react';

type Interaction = {
  type: string;
  ts?: string;
  details?: string;
};

export default function InteractionsTab({ interactions }: { interactions: Interaction[] }) {
  if (!interactions || interactions.length === 0) {
    return <p className="text-gray-500">No interactions recorded.</p>;
  }

  return (
    <div className="space-y-3">
      {interactions.map((it, idx) => (
        <div key={idx} className="p-3 rounded border bg-white">
          <div className="flex justify-between items-baseline">
            <div className="text-sm font-semibold">{it.type}</div>
            <div className="text-xs text-gray-400">{it.ts ? new Date(it.ts).toLocaleString() : ''}</div>
          </div>
          <div className="mt-1 text-gray-700">{it.details}</div>
        </div>
      ))}
    </div>
  );
}
