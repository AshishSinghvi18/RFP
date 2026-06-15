import { Search, Sparkles } from 'lucide-react';
import { FormEvent, useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';

import Badge, { getScoreVariant } from '@/components/common/Badge';
import EmptyState from '@/components/common/EmptyState';
import LoadingSpinner from '@/components/common/LoadingSpinner';
import { getApiErrorMessage } from '@/services/api';
import { searchOpportunities } from '@/services/opportunities';
import type { Opportunity, SearchFilters } from '@/utils/types';

const tabs: Array<{ label: string; value: NonNullable<SearchFilters['mode']> }> = [
  { label: 'Keyword', value: 'keyword' },
  { label: 'Semantic', value: 'semantic' },
  { label: 'Hybrid', value: 'hybrid' },
];

const SearchPage = () => {
  const navigate = useNavigate();
  const [query, setQuery] = useState('');
  const [mode, setMode] = useState<NonNullable<SearchFilters['mode']>>('hybrid');
  const [results, setResults] = useState<Opportunity[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const runSearch = async (searchQuery: string, searchMode: NonNullable<SearchFilters['mode']>) => {
    if (!searchQuery.trim()) {
      setResults([]);
      return;
    }

    setLoading(true);
    setError('');

    try {
      const response = await searchOpportunities({ query: searchQuery.trim(), mode: searchMode, page: 1, page_size: 12 });
      setResults(response.items);
    } catch (searchError) {
      setError(getApiErrorMessage(searchError, 'Unable to run search.'));
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (!query.trim()) {
      return;
    }

    const timer = window.setTimeout(() => {
      void runSearch(query, mode);
    }, 400);

    return () => window.clearTimeout(timer);
  }, [mode, query]);

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    void runSearch(query, mode);
  };

  return (
    <div className="space-y-6">
      <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
        <div className="mx-auto max-w-4xl space-y-6">
          <div className="text-center">
            <div className="mx-auto inline-flex rounded-2xl bg-blue-50 p-3 text-blue-600">
              <Sparkles className="h-7 w-7" />
            </div>
            <h1 className="mt-4 text-3xl font-semibold text-slate-900">Search the global opportunity graph</h1>
            <p className="mt-2 text-sm text-slate-500">Blend keyword precision with semantic retrieval to surface the best-fit opportunities faster.</p>
          </div>

          <form className="space-y-4" onSubmit={handleSubmit}>
            <div className="flex items-center gap-3 rounded-2xl border border-slate-200 px-5 py-4 focus-within:border-blue-500 focus-within:ring-4 focus-within:ring-blue-100">
              <Search className="h-5 w-5 text-slate-400" />
              <input
                value={query}
                onChange={(event) => setQuery(event.target.value)}
                placeholder="Try: digital health tenders in Southeast Asia"
                className="w-full border-none bg-transparent text-base text-slate-900 outline-none placeholder:text-slate-400"
              />
            </div>

            <div className="flex flex-wrap items-center justify-between gap-4">
              <div className="inline-flex rounded-2xl bg-slate-100 p-1">
                {tabs.map((tab) => (
                  <button
                    key={tab.value}
                    type="button"
                    onClick={() => setMode(tab.value)}
                    className={[
                      'rounded-xl px-4 py-2 text-sm font-medium transition',
                      mode === tab.value ? 'bg-white text-blue-600 shadow-sm' : 'text-slate-600',
                    ].join(' ')}
                  >
                    {tab.label}
                  </button>
                ))}
              </div>

              <button
                type="submit"
                className="rounded-2xl bg-blue-600 px-5 py-3 text-sm font-semibold text-white shadow-lg shadow-blue-600/20 transition hover:bg-blue-700"
              >
                Search
              </button>
            </div>
          </form>
        </div>
      </section>

      {error ? <div className="rounded-2xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">{error}</div> : null}

      <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
        <div className="mb-6 flex items-center justify-between">
          <div>
            <h2 className="text-lg font-semibold text-slate-900">Results</h2>
            <p className="text-sm text-slate-500">{results.length} matches found</p>
          </div>
        </div>

        {loading ? (
          <LoadingSpinner label="Searching opportunities..." />
        ) : results.length ? (
          <div className="space-y-4">
            {results.map((result) => (
              <button
                key={result.id}
                type="button"
                onClick={() => navigate(`/opportunities/${result.id}`)}
                className="w-full rounded-2xl border border-slate-200 p-5 text-left transition hover:border-blue-200 hover:bg-blue-50/40"
              >
                <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
                  <div>
                    <h3 className="text-lg font-semibold text-slate-900">{result.title}</h3>
                    <p className="mt-2 text-sm leading-7 text-slate-600">
                      {result.summary ?? result.description ?? 'No result snippet is currently available for this opportunity.'}
                    </p>
                    <div className="mt-4 flex flex-wrap gap-2 text-xs font-medium text-slate-500">
                      <span className="rounded-full bg-slate-100 px-3 py-1">{result.country ?? 'Unknown country'}</span>
                      <span className="rounded-full bg-slate-100 px-3 py-1">{result.region ?? 'Unknown region'}</span>
                      <span className="rounded-full bg-slate-100 px-3 py-1">{result.category ?? 'Uncategorized'}</span>
                    </div>
                  </div>
                  <Badge text={`Score ${result.score ?? 0}`} variant={getScoreVariant(result.score)} size="md" />
                </div>
              </button>
            ))}
          </div>
        ) : (
          <EmptyState
            icon={Search}
            title="No search results yet"
            description="Enter a query to explore opportunities by keyword, semantic meaning, or a hybrid approach."
          />
        )}
      </section>
    </div>
  );
};

export default SearchPage;
