import React from 'react';

export const LoadingSkeleton: React.FC<{ rows?: number; type?: 'card' | 'table' | 'text' }> = ({
  rows = 3,
  type = 'table'
}) => {
  if (type === 'card') {
    return (
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 animate-pulse">
        {Array.from({ length: rows }).map((_, i) => (
          <div key={i} className="h-32 bg-cloud-200 rounded-xl border border-cloud-300 p-4 flex flex-col justify-between">
            <div className="h-4 bg-cloud-300 rounded w-1/2"></div>
            <div className="h-8 bg-cloud-300 rounded w-3/4"></div>
            <div className="h-3 bg-cloud-300 rounded w-1/3"></div>
          </div>
        ))}
      </div>
    );
  }

  if (type === 'text') {
    return (
      <div className="space-y-2 animate-pulse">
        {Array.from({ length: rows }).map((_, i) => (
          <div key={i} className={`h-4 bg-cloud-200 rounded ${i % 2 === 0 ? 'w-full' : 'w-5/6'}`}></div>
        ))}
      </div>
    );
  }

  return (
    <div className="border border-cloud-200 rounded-xl overflow-hidden animate-pulse bg-white">
      <div className="h-10 bg-cloud-100 border-b border-cloud-200"></div>
      <div className="divide-y divide-cloud-200">
        {Array.from({ length: rows }).map((_, i) => (
          <div key={i} className="p-4 flex items-center justify-between gap-4">
            <div className="h-4 bg-cloud-200 rounded w-1/4"></div>
            <div className="h-4 bg-cloud-200 rounded w-1/3"></div>
            <div className="h-4 bg-cloud-200 rounded w-1/6"></div>
          </div>
        ))}
      </div>
    </div>
  );
};
