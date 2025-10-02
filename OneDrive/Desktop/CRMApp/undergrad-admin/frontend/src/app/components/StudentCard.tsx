'use client';

import React from 'react';
import { useRouter } from 'next/navigation';

type Student = {
  id: string;
  name: string;
  email?: string;
  grade?: number;
  application_status?: string;
  country?: string;
};

export default function StudentCard({ student }: { student: Student }) {
  const router = useRouter();

  const handleClick = () => {
    if (!student?.id) {
      console.warn('Student missing id', student);
      return;
    }
    router.push(`/students/${student.id}`);
  };

  return (
    <div
      role="button"
      tabIndex={0}
      onClick={handleClick}
      onKeyDown={(e) => { if (e.key === 'Enter') handleClick(); }}
      className="p-4 border rounded-lg shadow-sm hover:shadow-md transition cursor-pointer bg-white"
      style={{ WebkitTapHighlightColor: 'transparent' }}
      aria-label={`Open ${student.name}`}
    >
      <div className="flex items-start justify-between">
        <div>
          <h3 className="text-lg font-semibold">{student.name}</h3>
          <p className="text-sm text-gray-500">{student.email ?? '—'}</p>
          <p className="text-xs text-gray-400">{student.country ?? ''}</p>
        </div>
        <div className="text-right">
          <div className={`px-2 py-1 rounded-full text-xs font-medium ${
            student.application_status === 'Exploring' ? 'bg-gray-300 text-gray-800' :
            student.application_status === 'Shortlisting' ? 'bg-blue-500 text-white' :
            student.application_status === 'Applying' ? 'bg-yellow-300 text-black' :
            'bg-green-500 text-white'
          }`}>
            {student.application_status ?? '—'}
          </div>
        </div>
      </div>
    </div>
  );
}
