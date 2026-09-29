import React from 'react';

export type BadgeVariant = 'success' | 'warning' | 'danger' | 'info' | 'ai' | 'neutral';

interface BadgeProps {
  children: React.ReactNode;
  variant?: BadgeVariant;
  size?: 'sm' | 'md';
  className?: string;
}

export const Badge: React.FC<BadgeProps> = ({
  children,
  variant = 'neutral',
  size = 'md',
  className = ''
}) => {
  const variantStyles: Record<BadgeVariant, string> = {
    success: 'bg-emerald-50 text-emerald-700 border-emerald-200',
    warning: 'bg-amber-50 text-amber-800 border-amber-200',
    danger: 'bg-rose-50 text-rose-700 border-rose-200',
    info: 'bg-blue-50 text-blue-700 border-blue-200',
    ai: 'bg-purple-50 text-ai-700 border-purple-200 font-medium',
    neutral: 'bg-cloud-200 text-obsidian-700 border-cloud-300'
  };

  const sizeStyles = size === 'sm' ? 'px-2 py-0.5 text-xs font-medium' : 'px-2.5 py-1 text-xs font-semibold';

  return (
    <span className={`inline-flex items-center rounded-md border ${variantStyles[variant]} ${sizeStyles} ${className}`}>
      {children}
    </span>
  );
};
