import React from 'react';

export default function StatsCards({ stats }) {
  if (!stats) return null;

  const cards = [
    {
      title: 'Total Students',
      value: stats.total_students,
      icon: '👥',
      color: 'from-blue-500 to-blue-600',
      bgColor: 'bg-blue-500/10',
      borderColor: 'border-blue-500/50'
    },
    {
      title: 'Total Complaints',
      value: stats.total_complaints,
      icon: '🎫',
      color: 'from-purple-500 to-purple-600',
      bgColor: 'bg-purple-500/10',
      borderColor: 'border-purple-500/50'
    },
    {
      title: 'Pending',
      value: stats.pending_complaints,
      icon: '⏳',
      color: 'from-yellow-500 to-yellow-600',
      bgColor: 'bg-yellow-500/10',
      borderColor: 'border-yellow-500/50'
    },
    {
      title: 'Resolved',
      value: stats.resolved_complaints,
      icon: '✅',
      color: 'from-green-500 to-green-600',
      bgColor: 'bg-green-500/10',
      borderColor: 'border-green-500/50'
    }
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      {cards.map((card, index) => (
        <div
          key={index}
          className={`${card.bgColor} backdrop-blur-lg border ${card.borderColor} rounded-2xl p-6 transform hover:scale-105 transition-all cursor-pointer`}
        >
          <div className="flex items-center justify-between mb-4">
            <div className="text-4xl">{card.icon}</div>
            <div className={`bg-gradient-to-r ${card.color} text-white text-2xl font-bold px-4 py-2 rounded-lg shadow-lg`}>
              {card.value}
            </div>
          </div>
          <h3 className="text-gray-300 font-semibold text-lg">{card.title}</h3>
        </div>
      ))}
    </div>
  );
}