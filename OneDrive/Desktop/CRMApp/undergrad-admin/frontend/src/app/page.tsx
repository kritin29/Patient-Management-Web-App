// export default function Page() {
//   return (
//     <main className="flex items-center justify-center h-screen bg-gray-100">
//       <h1 className="text-4xl font-bold text-blue-600">Hello CRMApp!</h1>
//     </main>
//   );
// }

'use client';

import { useQuery } from '@tanstack/react-query';
import axios from 'axios';
import { useEffect } from 'react';
import StudentCard from './components/StudentCard';

type Student = {
  id: string;
  name: string;
  email: string;
  grade: number;
  application_status: string;
};

export default function HomePage() {
  const { data, isLoading, error } = useQuery<Student[], Error>({
    queryKey: ['students'],
    queryFn: async () => {
      const res = await axios.get('http://127.0.0.1:8000/api/students');
      return res.data.students;
    },
    
  });
    useEffect(() => {
      if (data) console.log('student ids:', data.map(s => s.id));
    }, [data]);

  if (isLoading) return <p className="p-4">Loading students...</p>;
  if (error) return <p className="p-4 text-red-500">Error loading students</p>;

  return (
    <div className="p-8 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {data?.map((student) => (
        <StudentCard key={student.id} student={student} />
      ))}
    </div>
  );
}
