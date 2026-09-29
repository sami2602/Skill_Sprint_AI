import React from 'react';
import { VerificationStatus } from '../../types';
import { CheckCircle2, AlertTriangle, AlertCircle, HelpCircle, XCircle } from 'lucide-react';

interface VerificationDecisionBadgeProps {
  status: VerificationStatus;
  size?: 'sm' | 'md' | 'lg';
}

export const VerificationDecisionBadge: React.FC<VerificationDecisionBadgeProps> = ({
  status,
  size = 'md'
}) => {
  const configs: Record<VerificationStatus, { label: string; bg: string; text: string; border: string; icon: React.ReactNode }> = {
    VERIFIED: {
      label: 'Verified (100% Grounded)',
      bg: 'bg-emerald-50',
      text: 'text-emerald-800',
      border: 'border-emerald-300',
      icon: <CheckCircle2 className="h-4 w-4 text-emerald-600 shrink-0" />
    },
    VERIFIED_WITH_WARNING: {
      label: 'Verified with Warning',
      bg: 'bg-amber-50',
      text: 'text-amber-800',
      border: 'border-amber-300',
      icon: <AlertTriangle className="h-4 w-4 text-amber-600 shrink-0" />
    },
    INCOMPLETE: {
      label: 'Incomplete Plan',
      bg: 'bg-rose-50',
      text: 'text-rose-800',
      border: 'border-rose-300',
      icon: <XCircle className="h-4 w-4 text-rose-600 shrink-0" />
    },
    UNSUPPORTED: {
      label: 'Unsupported Claim',
      bg: 'bg-purple-50',
      text: 'text-purple-800',
      border: 'border-purple-300',
      icon: <HelpCircle className="h-4 w-4 text-purple-600 shrink-0" />
    },
    CONTRADICTORY: {
      label: 'Policy Contradiction',
      bg: 'bg-red-100',
      text: 'text-red-900',
      border: 'border-red-400',
      icon: <AlertCircle className="h-4 w-4 text-red-700 shrink-0" />
    },
    MANUAL_REVIEW_REQUIRED: {
      label: 'Manual Review Required',
      bg: 'bg-amber-100',
      text: 'text-amber-900',
      border: 'border-amber-400',
      icon: <AlertTriangle className="h-4 w-4 text-amber-700 shrink-0" />
    }
  };

  const config = configs[status] || configs.VERIFIED;

  const sizeStyles = {
    sm: 'px-2 py-0.5 text-xs gap-1',
    md: 'px-3 py-1 text-xs gap-1.5 font-semibold',
    lg: 'px-4 py-2 text-sm gap-2 font-bold'
  };

  return (
    <span className={`inline-flex items-center rounded-lg border ${config.bg} ${config.text} ${config.border} ${sizeStyles[size]}`}>
      {config.icon}
      <span>{config.label}</span>
    </span>
  );
};
