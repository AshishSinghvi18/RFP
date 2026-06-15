import { get } from '@/services/api';
import type { DashboardSummary, HeatmapData, TrendData } from '@/utils/types';

export const getSummary = () => get<DashboardSummary>('/dashboard/summary');

export const getTrends = () => get<TrendData[]>('/dashboard/trends');

export const getHeatmap = () => get<HeatmapData[]>('/dashboard/heatmap');
