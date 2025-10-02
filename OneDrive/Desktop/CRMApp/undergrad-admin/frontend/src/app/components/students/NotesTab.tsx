'use client';

import React, { useState } from 'react';
import axios from 'axios';
import { useMutation, useQueryClient } from '@tanstack/react-query';

type Note = {
  id?: string;
  author: string;
  text: string;
  ts?: string;
};

export default function NotesTab({ notes, studentId }: { notes: Note[]; studentId: string }) {
  const [text, setText] = useState('');
  const queryClient = useQueryClient();

  const mutation = useMutation({
    mutationFn: (payload: { author: string; text: string }) =>
      axios.post(`http://127.0.0.1:8000/api/students/${studentId}/notes`, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['student', studentId] });
    },
  });

  // Use boolean helpers (preferred)
  const saving = !!mutation.isPending;
  const failed = !!mutation.isError;


  const handleSubmit = () => {
    if (!text.trim()) return;
    mutation.mutate({ author: 'Admin', text });
    setText('');
  };

//   const saving = mutation.status === 'loading';
//   const failed = mutation.status === 'error';

  return (
    <div>
      <div className="mb-4">
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Write an internal note..."
          className="w-full p-3 border rounded resize-none"
          rows={4}
        />
        <div className="flex items-center gap-3 mt-2">
          <button
            onClick={handleSubmit}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
            disabled={saving}
          >
            {saving ? 'Saving…' : 'Add Note'}
          </button>
          {failed && <p className="text-red-500 text-sm">Could not save note</p>}
        </div>
      </div>

      <div className="space-y-3">
        {(!notes || notes.length === 0) && <p className="text-gray-500">No notes yet.</p>}
        {notes?.map((n, idx) => (
          <div key={n.id ?? idx} className="p-3 rounded border bg-white shadow-sm">
            <div className="flex justify-between">
              <div className="text-sm font-semibold">{n.author}</div>
              <div className="text-xs text-gray-400">{n.ts ? new Date(n.ts).toLocaleString() : ''}</div>
            </div>
            <div className="mt-1 text-gray-700">{n.text}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
