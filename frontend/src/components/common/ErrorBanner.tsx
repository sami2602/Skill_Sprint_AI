import React from 'react';
import { AlertTriangle, RefreshCw } from 'lucide-react';
import { Button } from './Button';

interface ErrorBannerProps {
  title?: string;
  message: string;
  onRetry?: () => void;
}

export const ErrorBanner: React.FC<ErrorBannerProps> = ({
  title = 'Service Communication Error',
  message,
  onRetry
}) => {
  return (
    <div className="p-4 rounded-xl bg-rose-50 border border-rose-200 flex items-start gap-3 text-rose-800 my-4">
      <AlertTriangle className="h-5 w-5 shrink-0 text-rose-600 mt-0.5" />
      <div className="flex-1">
        <h4 className="text-sm font-bold font-heading">{title}</h4>
        <p className="text-xs text-rose-700 mt-0.5">{message}</p>
      </div>
      {onRetry && (
        <Button
          onClick={onRetry}
          variant="outline"
          size="sm"
          className="border-rose-300 text-rose-800 hover:bg-rose-100 bg-white"
          leftIcon={<RefreshCw className="h-3.5 w-3.5" />}
        >
          Retry
        </Button>
      )}
    </div>
  );
};
