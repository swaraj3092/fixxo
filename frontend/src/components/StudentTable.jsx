import React, { useState } from 'react';

export default function StudentTable({ students, onRefresh }) {
  const [searchTerm, setSearchTerm] = useState('');

  const filteredStudents = students.filter(student =>
    student.student_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    student.college_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
    student.hostel_name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div>
      {/* Search Bar */}
      <div className="mb-4">
        <input
          type="text"
          placeholder="🔍 Search by name, ID, or hostel..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="w-full px-4 py-3 bg-gray-700/50 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-purple-500 transition"
        />
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b border-gray-700">
              <th className="text-left py-3 px-4 text-gray-400 font-semibold">Name</th>
              <th className="text-left py-3 px-4 text-gray-400 font-semibold">College ID</th>
              <th className="text-left py-3 px-4 text-gray-400 font-semibold">Hostel</th>
              <th className="text-left py-3 px-4 text-gray-400 font-semibold">Room</th>
              <th className="text-left py-3 px-4 text-gray-400 font-semibold">Phone</th>
              <th className="text-left py-3 px-4 text-gray-400 font-semibold">Status</th>
            </tr>
          </thead>
          <tbody>
            {filteredStudents.map((student) => (
              <tr key={student.id} className="border-b border-gray-700/50 hover:bg-gray-700/30 transition">
                <td className="py-3 px-4 text-white font-medium">{student.student_name}</td>
                <td className="py-3 px-4 text-gray-300 font-mono text-sm">{student.college_id}</td>
                <td className="py-3 px-4 text-gray-300">{student.hostel_name}</td>
                <td className="py-3 px-4 text-gray-300">{student.room_number}</td>
                <td className="py-3 px-4 text-gray-400 text-sm">{student.phone_number.replace('whatsapp:', '')}</td>
                <td className="py-3 px-4">
                  <span className="bg-green-500/20 text-green-300 px-3 py-1 rounded-full text-xs font-semibold">
                    ✅ Active
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>

        {filteredStudents.length === 0 && (
          <div className="text-center py-12 text-gray-400">
            No students found matching "{searchTerm}"
          </div>
        )}
      </div>
    </div>
  );
}