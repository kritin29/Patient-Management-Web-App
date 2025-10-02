'use client';

import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import axios from 'axios';
import { useParams, useRouter } from 'next/navigation';
import NotesTab from '../../components/students/NotesTab';
import InteractionsTab from '../../components/students/InteractionsTab';
import CommunicationsTab from '../../components/students/CommunicationsTab';

type Student = {
  id: string;
  name: string;
  email?: string;
  phone?: string;
  grade?: number;
  country?: string;
  application_status?: string;
};

export default function StudentDetailPage() {
  const params = useParams();
  const router = useRouter();
  const studentId = typeof params?.id === 'string' ? params.id : undefined;

  const [activeTab, setActiveTab] = useState<'notes' | 'interactions' | 'communications'>('notes');

  const query = useQuery<
    { student: Student; notes: any[]; interactions: any[]; communications: any[] },
    Error
  >({
    queryKey: ['student', studentId],
    queryFn: async () => {
      if (!studentId) throw new Error('Missing student id');
      const res = await axios.get(`http://127.0.0.1:8000/api/students/${studentId}`);
      return res.data;
    },
    enabled: !!studentId,
    staleTime: 1000 * 60, // 1 minute
  });

  if (!studentId) {
    return (
      <div className="p-6">
        <p className="text-red-500">No student selected.</p>
        <button className="mt-3 text-blue-600" onClick={() => router.push('/')}>Back to list</button>
      </div>
    );
  }

  if (query.isLoading) return <p className="p-6">Loading student...</p>;
  if (query.isError) return <p className="p-6 text-red-500">Error loading student: {query.error?.message}</p>;

  const data = query.data!;
  const student = data.student;

  return (
    <div className="p-8 max-w-4xl mx-auto">
      <div className="mb-6">
        <button className="text-blue-600 mb-3" onClick={() => router.push('/')}>← Back</button>
        <h1 className="text-3xl font-bold">{student.name}</h1>
        <p className="text-gray-600">
          {student.email ?? '—'} • {student.phone ?? '—'} • Grade {student.grade ?? '—'} • {student.country ?? '—'}
        </p>
        <div className="mt-3">
          <span className={`inline-block px-3 py-1 rounded-full text-sm text-white ${
            student.application_status === 'Exploring' ? 'bg-gray-500' :
            student.application_status === 'Shortlisting' ? 'bg-blue-600' :
            student.application_status === 'Applying' ? 'bg-yellow-500 text-black' :
            'bg-green-600'
          }`}>
            {student.application_status ?? 'Unknown'}
          </span>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-gray-200 mb-6">
        {[
          { key: 'notes', label: 'Notes' },
          { key: 'interactions', label: 'Interactions' },
          { key: 'communications', label: 'Communications' },
        ].map((t) => (
          <button
            key={t.key}
            onClick={() => setActiveTab(t.key as any)}
            className={`px-4 py-2 -mb-px ${activeTab === t.key ? 'border-b-2 border-blue-600 text-blue-600' : 'text-gray-600'}`}
          >
            {t.label}
          </button>
        ))}
      </div>

      {/* Content */}
      <div>
        {activeTab === 'notes' && <NotesTab notes={data.notes ?? []} studentId={studentId} />}
        {activeTab === 'interactions' && <InteractionsTab interactions={data.interactions ?? []} />}
        {activeTab === 'communications' && <CommunicationsTab communications={data.communications ?? []} studentId={studentId} />}
      </div>
    </div>
  );
}
