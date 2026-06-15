import {
  Activity,
  Globe2,
  Radar,
  ShieldCheck,
  Target,
  TrendingUp,
} from 'lucide-react';
import { useEffect, useMemo, useState } from 'react';
import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';

import Badge, { formatStatusLabel, getScoreVariant, getStatusBadgeClass } from '@/components/common/Badge';
import EmptyState from '@/components/common/EmptyState';
import LoadingSpinner from '@/components/common/LoadingSpinner';
import { getApiErrorMessage } from '@/services/api';
import { getHeatmap, getSummary, getTrends } from '@/services/dashboard';
import { searchOpportunities } from '@/services/opportunities';
import type { DashboardSummary, HeatmapData, Opportunity, TrendData } from '@/utils/types';

const kpiCardSkeleton = Array.from({ length: 6 }, (_, index) => index);

const DashboardPage = () => {
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [trends, setTrends] = useState<TrendData[]>([]);
  const [heatmap, setHeatmap] = useState<HeatmapData[]>([]);
  const [topOpportunities, setTopOpportunities] = useState<Opportunity[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const loadDashboard = async () => {
      setLoading(true);
      setError('');

      try {
        const [summaryResponse, trendResponse, heatmapResponse, opportunitiesResponse] = await Promise.all([
          getSummary(),
          getTrends(),
          getHeatmap(),
          searchOpportunities({ page: 1, page_size: 20 }),
        ]);

        setSummary(summaryResponse);
        setTrends(trendResponse.slice(-12));
        setHeatmap(heatmapResponse);
        setTopOpportunities(
          [...opportunitiesResponse.items]
            .sort((left, right) => (right.score ?? 0) - (left.score ?? 0))
            .slice(0, 5),
        );
      } catch (loadError) {
        setError(getApiErrorMessage(loadError, 'Unable to load dashboard insights.'));
      } finally {
        setLoading(false);
      }
    };

    void loadDashboard();
  }, []);

  const regionTotals = useMemo(() => {
    const totals = heatmap.reduce<Record<string, number>>((accumulator, item) => {
      accumulator[item.region] = (accumulator[item.region] ?? 0) + item.count;
      return accumulator;
    }, {});

    return Object.entries(totals)
      .map(([region, count]) => ({ region, count }))
      .sort((left, right) => right.count - left.count);
  }, [heatmap]);

  const kpis = summary
    ? [
        {
          label: 'Total Opportunities',
          value: summary.total_opportunities,
          icon: Target,
          accent: 'bg-blue-50 text-blue-600',
        },
        {
          label: 'New This Week',
          value: summary.new_this_week,
          icon: TrendingUp,
          accent: 'bg-indigo-50 text-indigo-600',
        },
        {
          label: 'High Priority',
          value: summary.high_priority,
          icon: Radar,
          accent: 'bg-emerald-50 text-emerald-600',
        },
        {
          label: 'Active RFPs',
          value: summary.active_rfps,
          icon: Activity,
          accent: 'bg-orange-50 text-orange-600',
        },
        {
          label: 'Regions Covered',
          value: summary.regions_covered,
          icon: Globe2,
          accent: 'bg-violet-50 text-violet-600',
        },
        {
          label: 'Crawl Success Rate',
          value: `${summary.crawl_success_rate.toFixed(1)}%`,
          icon: ShieldCheck,
          accent: 'bg-sky-50 text-sky-600',
        },
      ]
    : [];

  return (
    <div className="space-y-6">
      {error ? <div className="rounded-2xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">{error}</div> : null}

      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {loading
          ? kpiCardSkeleton.map((item) => (
              <div key={item} className="animate-pulse rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
                <div className="h-10 w-10 rounded-xl bg-slate-200" />
                <div className="mt-5 h-4 w-28 rounded bg-slate-200" />
                <div className="mt-3 h-8 w-20 rounded bg-slate-200" />
              </div>
            ))
          : kpis.map(({ label, value, icon: Icon, accent }) => (
              <div key={label} className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
                <div className="flex items-start justify-between">
                  <div>
                    <p className="text-sm font-medium text-slate-500">{label}</p>
                    <p className="mt-4 text-3xl font-semibold text-slate-900">{value}</p>
                  </div>
                  <div className={['rounded-2xl p-3', accent].join(' ')}>
                    <Icon className="h-6 w-6" />
                  </div>
                </div>
              </div>
            ))}
      </section>

      <section className="grid gap-6 xl:grid-cols-[1.4fr_1fr]">
        <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
          <div className="mb-6 flex items-center justify-between">
            <div>
              <h3 className="text-lg font-semibold text-slate-900">Opportunity Trend</h3>
              <p className="text-sm text-slate-500">Opportunity flow over the last 12 weeks</p>
            </div>
          </div>

          {loading ? (
            <div className="h-80 animate-pulse rounded-2xl bg-slate-100" />
          ) : trends.length ? (
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={trends}>
                  <defs>
                    <linearGradient id="trendFill" x1="0" x2="0" y1="0" y2="1">
                      <stop offset="5%" stopColor="#2563EB" stopOpacity={0.28} />
                      <stop offset="95%" stopColor="#2563EB" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" vertical={false} />
                  <XAxis dataKey="period" tickLine={false} axisLine={false} tick={{ fill: '#64748B', fontSize: 12 }} />
                  <YAxis tickLine={false} axisLine={false} tick={{ fill: '#64748B', fontSize: 12 }} />
                  <Tooltip />
                  <Area type="monotone" dataKey="count" stroke="#2563EB" fill="url(#trendFill)" strokeWidth={3} />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <EmptyState icon={TrendingUp} title="No trend data yet" description="Opportunity trend data will appear once weekly ingestion completes." />
          )}
        </div>

        <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
          <div className="mb-6">
            <h3 className="text-lg font-semibold text-slate-900">Region Heatmap</h3>
            <p className="text-sm text-slate-500">Opportunity concentration by region</p>
          </div>

          {loading ? (
            <div className="h-80 animate-pulse rounded-2xl bg-slate-100" />
          ) : regionTotals.length ? (
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={regionTotals} layout="vertical" margin={{ left: 12 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" horizontal={false} />
                  <XAxis type="number" tickLine={false} axisLine={false} tick={{ fill: '#64748B', fontSize: 12 }} />
                  <YAxis
                    type="category"
                    dataKey="region"
                    tickLine={false}
                    axisLine={false}
                    tick={{ fill: '#64748B', fontSize: 12 }}
                    width={110}
                  />
                  <Tooltip />
                  <Bar dataKey="count" fill="#2563EB" radius={[0, 8, 8, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <EmptyState icon={Globe2} title="No region data found" description="Heatmap data will appear when source crawls generate regional opportunity matches." />
          )}
        </div>
      </section>

      <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
        <div className="mb-6 flex items-center justify-between">
          <div>
            <h3 className="text-lg font-semibold text-slate-900">Top Opportunities</h3>
            <p className="text-sm text-slate-500">Highest scoring opportunities in the pipeline</p>
          </div>
        </div>

        {loading ? (
          <LoadingSpinner label="Loading top opportunities..." />
        ) : topOpportunities.length ? (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-slate-200 text-sm">
              <thead>
                <tr className="text-left text-slate-500">
                  <th className="pb-3 font-medium">Title</th>
                  <th className="pb-3 font-medium">Country</th>
                  <th className="pb-3 font-medium">Category</th>
                  <th className="pb-3 font-medium">Score</th>
                  <th className="pb-3 font-medium">Status</th>
                  <th className="pb-3 font-medium">Deadline</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {topOpportunities.map((opportunity) => (
                  <tr key={opportunity.id} className="text-slate-700">
                    <td className="py-4 pr-4">
                      <div>
                        <p className="font-medium text-slate-900">{opportunity.title}</p>
                        <p className="mt-1 text-xs text-slate-500">{opportunity.institution ?? 'Institution not specified'}</p>
                      </div>
                    </td>
                    <td className="py-4 pr-4">{opportunity.country ?? '—'}</td>
                    <td className="py-4 pr-4">{opportunity.category ?? '—'}</td>
                    <td className="py-4 pr-4">
                      <Badge text={`${opportunity.score ?? 0}`} variant={getScoreVariant(opportunity.score)} size="md" />
                    </td>
                    <td className="py-4 pr-4">
                      <Badge
                        text={formatStatusLabel(opportunity.status)}
                        size="md"
                        className={getStatusBadgeClass(opportunity.status)}
                      />
                    </td>
                    <td className="py-4">{opportunity.deadline ? new Date(opportunity.deadline).toLocaleDateString() : 'TBD'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <EmptyState icon={Target} title="No opportunities available" description="Top opportunities will appear once records are scored and ingested." />
        )}
      </section>
    </div>
  );
};

export default DashboardPage;
