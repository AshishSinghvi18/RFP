import { ChevronLeft, ChevronRight, Download, Filter, Search } from 'lucide-react';
import { ChangeEvent, FormEvent, useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';

import Badge, { formatStatusLabel, getScoreVariant, getStatusBadgeClass } from '@/components/common/Badge';
import EmptyState from '@/components/common/EmptyState';
import LoadingSpinner from '@/components/common/LoadingSpinner';
import { getApiErrorMessage } from '@/services/api';
import { searchOpportunities } from '@/services/opportunities';
import type { Opportunity, PaginatedResponse, SearchFilters } from '@/utils/types';

const regionOptions = ['Africa', 'Asia', 'Europe', 'Latin America', 'Middle East', 'North America', 'Oceania'];
const countryOptions = ['India', 'Indonesia', 'Kenya', 'Saudi Arabia', 'Singapore', 'United Arab Emirates', 'United Kingdom'];
const categoryOptions = ['Digital Infrastructure', 'Energy', 'Healthcare', 'Public Safety', 'Smart Cities', 'Transport'];
const statusOptions = ['signal_detected', 'under_review', 'qualified', 'active', 'pursuing', 'closed_won', 'closed_lost', 'archived'];
const standardsOptions = ['ISO 27001', 'NIST', 'SOC 2', 'GDPR', 'PCI DSS'];

const defaultFilters: SearchFilters = {
  query: '',
  regions: [],
  countries: [],
  categories: [],
  standards: [],
  status: [],
  page: 1,
  page_size: 10,
};

const getMultiSelectValues = (event: ChangeEvent<HTMLSelectElement>) =>
  Array.from(event.target.selectedOptions, (option) => option.value);

const OpportunityExplorerPage = () => {
  const navigate = useNavigate();
  const [showFilters, setShowFilters] = useState(true);
  const [draftFilters, setDraftFilters] = useState<SearchFilters>(defaultFilters);
  const [filters, setFilters] = useState<SearchFilters>(defaultFilters);
  const [results, setResults] = useState<PaginatedResponse<Opportunity> | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const loadOpportunities = async () => {
      setLoading(true);
      setError('');

      try {
        const response = await searchOpportunities(filters);
        setResults(response);
      } catch (loadError) {
        setError(getApiErrorMessage(loadError, 'Unable to fetch opportunities.'));
      } finally {
        setLoading(false);
      }
    };

    void loadOpportunities();
  }, [filters]);

  const totalPages = useMemo(() => {
    if (!results) {
      return 1;
    }

    return Math.max(1, Math.ceil(results.total / results.page_size));
  }, [results]);

  const applyFilters = (event?: FormEvent) => {
    event?.preventDefault();
    setFilters({ ...draftFilters, page: 1, page_size: filters.page_size ?? 10 });
  };

  const goToPage = (page: number) => {
    setFilters((current) => ({ ...current, page }));
  };

  return (
    <div className="space-y-6">
      <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
        <form className="flex flex-col gap-4 lg:flex-row lg:items-center" onSubmit={applyFilters}>
          <div className="flex flex-1 items-center gap-3 rounded-2xl border border-slate-200 px-4 py-3 focus-within:border-blue-500 focus-within:ring-4 focus-within:ring-blue-100">
            <Search className="h-5 w-5 text-slate-400" />
            <input
              value={draftFilters.query ?? ''}
              onChange={(event) => setDraftFilters((current) => ({ ...current, query: event.target.value }))}
              placeholder="Search opportunities, regulators, sectors, or standards"
              className="w-full border-none bg-transparent text-sm text-slate-900 outline-none placeholder:text-slate-400"
            />
          </div>

          <div className="flex flex-wrap gap-3">
            <button
              type="button"
              onClick={() => setShowFilters((current) => !current)}
              className="inline-flex items-center gap-2 rounded-2xl border border-slate-200 px-4 py-3 text-sm font-medium text-slate-700 transition hover:bg-slate-50"
            >
              <Filter className="h-4 w-4" />
              Filters
            </button>
            <button
              type="button"
              className="inline-flex items-center gap-2 rounded-2xl border border-slate-200 px-4 py-3 text-sm font-medium text-slate-400"
            >
              <Download className="h-4 w-4" />
              Export
            </button>
            <button
              type="submit"
              className="rounded-2xl bg-blue-600 px-5 py-3 text-sm font-semibold text-white shadow-lg shadow-blue-600/20 transition hover:bg-blue-700"
            >
              Search
            </button>
          </div>
        </form>
      </div>

      {showFilters ? (
        <form className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm" onSubmit={applyFilters}>
          <div className="grid gap-5 md:grid-cols-2 xl:grid-cols-4">
            <label className="space-y-2 text-sm font-medium text-slate-700">
              <span>Region</span>
              <select
                value={draftFilters.regions?.[0] ?? ''}
                onChange={(event) => setDraftFilters((current) => ({ ...current, regions: event.target.value ? [event.target.value] : [] }))}
                className="w-full rounded-xl border border-slate-200 px-3 py-2.5 text-sm text-slate-900 outline-none focus:border-blue-500"
              >
                <option value="">All regions</option>
                {regionOptions.map((option) => (
                  <option key={option} value={option}>
                    {option}
                  </option>
                ))}
              </select>
            </label>

            <label className="space-y-2 text-sm font-medium text-slate-700">
              <span>Country</span>
              <select
                value={draftFilters.countries?.[0] ?? ''}
                onChange={(event) => setDraftFilters((current) => ({ ...current, countries: event.target.value ? [event.target.value] : [] }))}
                className="w-full rounded-xl border border-slate-200 px-3 py-2.5 text-sm text-slate-900 outline-none focus:border-blue-500"
              >
                <option value="">All countries</option>
                {countryOptions.map((option) => (
                  <option key={option} value={option}>
                    {option}
                  </option>
                ))}
              </select>
            </label>

            <label className="space-y-2 text-sm font-medium text-slate-700">
              <span>Category</span>
              <select
                multiple
                value={draftFilters.categories ?? []}
                onChange={(event) => setDraftFilters((current) => ({ ...current, categories: getMultiSelectValues(event) }))}
                className="min-h-28 w-full rounded-xl border border-slate-200 px-3 py-2.5 text-sm text-slate-900 outline-none focus:border-blue-500"
              >
                {categoryOptions.map((option) => (
                  <option key={option} value={option}>
                    {option}
                  </option>
                ))}
              </select>
            </label>

            <label className="space-y-2 text-sm font-medium text-slate-700">
              <span>Status</span>
              <select
                multiple
                value={draftFilters.status ?? []}
                onChange={(event) => setDraftFilters((current) => ({ ...current, status: getMultiSelectValues(event) }))}
                className="min-h-28 w-full rounded-xl border border-slate-200 px-3 py-2.5 text-sm text-slate-900 outline-none focus:border-blue-500"
              >
                {statusOptions.map((option) => (
                  <option key={option} value={option}>
                    {formatStatusLabel(option)}
                  </option>
                ))}
              </select>
            </label>

            <label className="space-y-2 text-sm font-medium text-slate-700">
              <span>Score minimum</span>
              <input
                type="number"
                min={0}
                max={100}
                value={draftFilters.score_min ?? ''}
                onChange={(event) =>
                  setDraftFilters((current) => ({
                    ...current,
                    score_min: event.target.value ? Number(event.target.value) : undefined,
                  }))
                }
                className="w-full rounded-xl border border-slate-200 px-3 py-2.5 text-sm text-slate-900 outline-none focus:border-blue-500"
              />
            </label>

            <label className="space-y-2 text-sm font-medium text-slate-700">
              <span>Score maximum</span>
              <input
                type="number"
                min={0}
                max={100}
                value={draftFilters.score_max ?? ''}
                onChange={(event) =>
                  setDraftFilters((current) => ({
                    ...current,
                    score_max: event.target.value ? Number(event.target.value) : undefined,
                  }))
                }
                className="w-full rounded-xl border border-slate-200 px-3 py-2.5 text-sm text-slate-900 outline-none focus:border-blue-500"
              />
            </label>

            <label className="space-y-2 text-sm font-medium text-slate-700">
              <span>Date from</span>
              <input
                type="date"
                value={draftFilters.date_from ?? ''}
                onChange={(event) => setDraftFilters((current) => ({ ...current, date_from: event.target.value || undefined }))}
                className="w-full rounded-xl border border-slate-200 px-3 py-2.5 text-sm text-slate-900 outline-none focus:border-blue-500"
              />
            </label>

            <label className="space-y-2 text-sm font-medium text-slate-700">
              <span>Date to</span>
              <input
                type="date"
                value={draftFilters.date_to ?? ''}
                onChange={(event) => setDraftFilters((current) => ({ ...current, date_to: event.target.value || undefined }))}
                className="w-full rounded-xl border border-slate-200 px-3 py-2.5 text-sm text-slate-900 outline-none focus:border-blue-500"
              />
            </label>

            <label className="space-y-2 text-sm font-medium text-slate-700">
              <span>Standards</span>
              <select
                multiple
                value={draftFilters.standards ?? []}
                onChange={(event) => setDraftFilters((current) => ({ ...current, standards: getMultiSelectValues(event) }))}
                className="min-h-28 w-full rounded-xl border border-slate-200 px-3 py-2.5 text-sm text-slate-900 outline-none focus:border-blue-500"
              >
                {standardsOptions.map((option) => (
                  <option key={option} value={option}>
                    {option}
                  </option>
                ))}
              </select>
            </label>
          </div>
        </form>
      ) : null}

      <div className="rounded-2xl border border-slate-200 bg-white shadow-sm">
        <div className="flex items-center justify-between border-b border-slate-200 px-6 py-4">
          <div>
            <h3 className="text-lg font-semibold text-slate-900">Opportunity Explorer</h3>
            <p className="text-sm text-slate-500">{results?.total ?? 0} opportunities matched</p>
          </div>
        </div>

        {error ? <div className="border-b border-rose-200 bg-rose-50 px-6 py-3 text-sm text-rose-700">{error}</div> : null}

        {loading ? (
          <LoadingSpinner label="Loading opportunities..." />
        ) : results?.items.length ? (
          <>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-slate-200 text-sm">
                <thead className="bg-slate-50 text-left text-slate-500">
                  <tr>
                    {['ID', 'Country', 'Region', 'Regulator', 'Title', 'Category', 'Score', 'Status', 'Owner', 'Updated'].map((column) => (
                      <th key={column} className="px-6 py-3 font-medium">
                        {column}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {results.items.map((opportunity) => (
                    <tr
                      key={opportunity.id}
                      className="cursor-pointer text-slate-700 transition hover:bg-blue-50/50"
                      onClick={() => navigate(`/opportunities/${opportunity.id}`)}
                    >
                      <td className="px-6 py-4 font-medium text-slate-900">#{opportunity.id.slice(0, 8)}</td>
                      <td className="px-6 py-4">{opportunity.country ?? '—'}</td>
                      <td className="px-6 py-4">{opportunity.region ?? '—'}</td>
                      <td className="px-6 py-4">{opportunity.institution ?? '—'}</td>
                      <td className="px-6 py-4">
                        <div className="max-w-sm">
                          <p className="font-medium text-slate-900">{opportunity.title}</p>
                          <p className="mt-1 truncate text-xs text-slate-500">{opportunity.summary ?? opportunity.description ?? 'No summary available.'}</p>
                        </div>
                      </td>
                      <td className="px-6 py-4">{opportunity.category ?? '—'}</td>
                      <td className="px-6 py-4">
                        <Badge text={`${opportunity.score ?? 0}`} variant={getScoreVariant(opportunity.score)} />
                      </td>
                      <td className="px-6 py-4">
                        <Badge
                          text={formatStatusLabel(opportunity.status)}
                          className={getStatusBadgeClass(opportunity.status)}
                        />
                      </td>
                      <td className="px-6 py-4">{opportunity.owner_id ? opportunity.owner_id.slice(0, 8) : 'Unassigned'}</td>
                      <td className="px-6 py-4">{new Date(opportunity.updated_at).toLocaleDateString()}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <div className="flex flex-col gap-3 border-t border-slate-200 px-6 py-4 sm:flex-row sm:items-center sm:justify-between">
              <p className="text-sm text-slate-500">
                Page {results.page} of {totalPages}
              </p>
              <div className="flex items-center gap-2">
                <button
                  type="button"
                  onClick={() => goToPage(Math.max(1, (results.page ?? 1) - 1))}
                  disabled={(results.page ?? 1) <= 1}
                  className="inline-flex items-center gap-2 rounded-xl border border-slate-200 px-3 py-2 text-sm font-medium text-slate-700 transition hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-50"
                >
                  <ChevronLeft className="h-4 w-4" />
                  Previous
                </button>
                <button
                  type="button"
                  onClick={() => goToPage(Math.min(totalPages, (results.page ?? 1) + 1))}
                  disabled={(results.page ?? 1) >= totalPages}
                  className="inline-flex items-center gap-2 rounded-xl border border-slate-200 px-3 py-2 text-sm font-medium text-slate-700 transition hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-50"
                >
                  Next
                  <ChevronRight className="h-4 w-4" />
                </button>
              </div>
            </div>
          </>
        ) : (
          <div className="p-6">
            <EmptyState
              icon={Search}
              title="No opportunities found"
              description="Try broadening your filters or adjusting score thresholds to uncover more matches."
            />
          </div>
        )}
      </div>
    </div>
  );
};

export default OpportunityExplorerPage;
