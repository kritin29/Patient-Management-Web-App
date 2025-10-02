'use client';

import React, { useState } from 'react';
import axios from 'axios';
import { useMutation, useQueryClient } from '@tanstack/react-query';

type Comm = {
  id?: string;
  channel: string;
  body: string;
  logged_by?: string;
  ts?: string;
};

export default function CommunicationsTab({ communications, studentId }: { communications: Comm[]; studentId: string }) {
  const [channel, setChannel] = useState<'call' | 'email' | 'sms'>('call');
  const [body, setBody] = useState('');
  const queryClient = useQueryClient();

  const mutation = useMutation({
    mutationFn: (payload: { channel: string; body: string; logged_by: string }) =>
      axios.post(`http://127.0.0.1:8000/api/students/${studentId}/communications`, payload),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['student', studentId] }),
  });

  const saving = !!mutation.isPending;
  const failed = !!mutation.isError;

  const handleSubmit = () => {
    if (!body.trim()) return;
    mutation.mutate({ channel, body, logged_by: 'Admin' });
    setBody('');
  };

  return (
    <div>
      <div className="mb-4 p-3 bg-white border rounded">
        <div className="flex gap-2 items-center">
          <select value={channel} onChange={(e) => setChannel(e.target.value as any)} className="p-2 border rounded">
            <option value="call">Call</option>
            <option value="email">Email</option>
            <option value="sms">SMS</option>
          </select>
          <input
            value={body}
            onChange={(e) => setBody(e.target.value)}
            placeholder="Write a short log (e.g. left voicemail)"
            className="flex-1 p-2 border rounded"
          />
          <button onClick={handleSubmit} className="px-3 py-1 bg-blue-600 text-white rounded" disabled={saving}>
            {saving ? 'Logging…' : 'Log'}
          </button>
        </div>
        {failed && <p className="text-red-500 mt-2 text-sm">Failed to log communication</p>}
      </div>

      <div className="space-y-3">
        {(!communications || communications.length === 0) && <p className="text-gray-500">No communications yet.</p>}
        {communications?.map((c, idx) => (
          <div key={c.id ?? idx} className="p-3 rounded border bg-gray-50">
            <div className="flex justify-between items-baseline">
              <div className="font-semibold text-sm">{c.channel.toUpperCase()}</div>
              <div className="text-xs text-gray-400">{c.ts ? new Date(c.ts).toLocaleString() : ''}</div>
            </div>
            <div className="mt-1 text-gray-700">{c.body}</div>
            <div className="text-xs text-gray-400 mt-1">Logged by {c.logged_by ?? '—'}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
