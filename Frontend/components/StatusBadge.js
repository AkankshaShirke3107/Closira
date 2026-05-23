import React from 'react';
import Badge from './Badge';
import { StatusConfig } from '../constants/channels';

/**
 * Status badge — renders New (blue), Qualified (green), Escalated (red), etc.
 *
 * @param {string} status - One of 'new', 'qualified', 'escalated', 'processing', etc.
 */
export default function StatusBadge({ status }) {
  const config = StatusConfig[status];
  if (!config) return null;

  return (
    <Badge
      label={config.label}
      color={config.color}
      bgColor={config.bgColor}
    />
  );
}
