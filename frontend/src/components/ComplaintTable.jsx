import React from 'react';

export default function ComplaintTable({ complaints, compact = false, onRefresh }) {
  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'URGENT': return 'bg-red-500/20 text-red-300 border-red-500/50';
      case 'HIGH':   return 'bg-orange-500/20 text-orange-300 border-orange-500/50';
      case 'MEDIUM': return 'bg-yellow-500/20 text-yellow-300 border-yellow-500/50';
      case 'LOW':    return 'bg-blue-500/20 text-blue-300 border-blue-500/50';
      default:       return 'bg-gray-500/20 text-gray-300 border-gray-500/50';
    }
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case 'RESOLVED':     return { cls: 'bg-green-500/20 text-green-300',  label: '✅ Resolved' };
      case 'CANT_RESOLVE': return { cls: 'bg-red-500/20 text-red-300',      label: "❌ Can't Resolve" };
      case 'IN_PROGRESS':  return { cls: 'bg-blue-500/20 text-blue-300',    label: '🔧 In Progress' };
      default:             return { cls: 'bg-yellow-500/20 text-yellow-300', label: '⏳ Pending' };
    }
  };

  const getCategoryIcon = (category) => {
    const icons = {
      PLUMBING:    '🚰',
      ELECTRICAL:  '⚡',
      WIFI:        '📶',
      CLEANLINESS: '🧹',
      SECURITY:    '🔒',
      FOOD:        '🍽️',
      FURNITURE:   '🪑',
      OTHER:       '📋'
    };
    return icons[category] || '📋';
  };

  return (
    <div className="overflow-x-auto">
      <table className="w-full">
        <thead>
          <tr className="border-b border-gray-700">
            <th className="text-left py-3 px-4 text-gray-400 font-semibold">ID</th>
            <th className="text-left py-3 px-4 text-gray-400 font-semibold">Student</th>
            {!compact && <th className="text-left py-3 px-4 text-gray-400 font-semibold">Location</th>}
            <th className="text-left py-3 px-4 text-gray-400 font-semibold">Category</th>
            <th className="text-left py-3 px-4 text-gray-400 font-semibold">Priority</th>
            <th className="text-left py-3 px-4 text-gray-400 font-semibold">Status</th>
            <th className="text-left py-3 px-4 text-gray-400 font-semibold">Extras</th>
            <th className="text-left py-3 px-4 text-gray-400 font-semibold">Time</th>
          </tr>
        </thead>
        <tbody>
          {complaints.map((complaint) => {
            const status = getStatusBadge(complaint.status);
            return (
              <tr key={complaint.id} className="border-b border-gray-700/50 hover:bg-gray-700/30 transition">
                <td className="py-3 px-4">
                  <span className="text-purple-400 font-mono text-sm font-bold">
                    #{complaint.resolve_token?.slice(0, 8)}
                  </span>
                </td>
                <td className="py-3 px-4 text-white">{complaint.student_name}</td>
                {!compact && (
                  <td className="py-3 px-4 text-gray-300 text-sm">
                    {complaint.hostel_name}, Room {complaint.room_number}
                  </td>
                )}
                <td className="py-3 px-4">
                  <span className="flex items-center space-x-2">
                    <span>{getCategoryIcon(complaint.category)}</span>
                    <span className="text-gray-300 text-sm">{complaint.category}</span>
                  </span>
                </td>
                <td className="py-3 px-4">
                  <span className={`px-3 py-1 rounded-full text-xs font-semibold border ${getPriorityColor(complaint.priority)}`}>
                    {complaint.priority}
                  </span>
                </td>
                <td className="py-3 px-4">
                  <span className={`px-3 py-1 rounded-full text-xs font-semibold ${status.cls}`}>
                    {status.label}
                  </span>
                </td>
                <td className="py-3 px-4">
                  <div className="flex gap-1">
                    {complaint.media_url && (
                      <span className="px-2 py-1 rounded-full text-xs bg-indigo-500/20 text-indigo-300">
                        📷
                      </span>
                    )}
                    {complaint.cant_resolve_reason && (
                      <span className="px-2 py-1 rounded-full text-xs bg-red-500/20 text-red-300" title={complaint.cant_resolve_reason}>
                        ⚠️
                      </span>
                    )}
                  </div>
                </td>
                <td className="py-3 px-4 text-gray-400 text-sm">
                  {new Date(complaint.created_at).toLocaleString()}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>

      {complaints.length === 0 && (
        <div className="text-center py-12 text-gray-400">
          No complaints yet
        </div>
      )}
    </div>
  );
}