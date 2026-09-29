import React from 'react';
import { FolderOpen } from 'lucide-react';
import { Button } from './Button';

interface EmptyStateProps {
  title: string;
  description: string;
  actionLabel?: string;
  onAction?: () => void;
  icon?: React.ReactNode;
}

export const EmptyState: React.FC<EmptyStateProps> = ({
  title,
  description,
  actionLabel,
  onAction,
  icon
}) => {
  return (
    <div className="flex flex-col items-center justify-center p-12 text-center bg-white border border-cloud-200 rounded-xl">
      <div className="p-3 bg-cloud-100 rounded-full text-obsidian-400 mb-4">
        {icon || <FolderOpen className="h-8 w-8 text-electric-600" />}
      </div>
      <h3 className="text-base font-bold font-heading text-obsidian">{title}</h3>
      <p className="text-sm text-obsidian-400 mt-1 max-w-md">{description}</p>
      {actionLabel && onAction && (
        <div className="mt-6">
          <Button onClick={onAction} variant="primary" size="sm">
            {actionLabel}
          </Button>
        </div>
      )}
    </div>
  );
};
