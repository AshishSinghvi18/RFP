import {
  ArrowLeft,
  CalendarDays,
  FileStack,
  Landmark,
  MessageSquare,
  Send,
  Sparkles,
  Wallet,
} from 'lucide-react';
import { FormEvent, useEffect, useMemo, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';

import Badge, { formatStatusLabel, getScoreVariant, getStatusBadgeClass } from '@/components/common/Badge';
import EmptyState from '@/components/common/EmptyState';
import LoadingSpinner from '@/components/common/LoadingSpinner';
import { getApiErrorMessage } from '@/services/api';
import { addComment, getComments, getOpportunity } from '@/services/opportunities';
import type { Comment, OpportunityDetail } from '@/utils/types';

const OpportunityDetailPage = () => {
  const navigate = useNavigate();
  const { id = '' } = useParams();
  const [opportunity, setOpportunity] = useState<OpportunityDetail | null>(null);
  const [comments, setComments] = useState<Comment[]>([]);
  const [commentText, setCommentText] = useState('');
  const [loading, setLoading] = useState(true);
  const [submittingComment, setSubmittingComment] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    const loadOpportunity = async () => {
      setLoading(true);
      setError('');

      try {
        const [opportunityResponse, commentsResponse] = await Promise.all([getOpportunity(id), getComments(id)]);
        setOpportunity(opportunityResponse);
        setComments(commentsResponse);
      } catch (loadError) {
        setError(getApiErrorMessage(loadError, 'Unable to load the selected opportunity.'));
      } finally {
        setLoading(false);
      }
    };

    if (id) {
      void loadOpportunity();
    }
  }, [id]);

  const reasoningPoints = useMemo(() => {
    if (!opportunity) {
      return [];
    }

    if (opportunity.ai_reasoning) {
      return opportunity.ai_reasoning
        .split(/\n|•/)
        .map((item) => item.trim())
        .filter(Boolean);
    }

    return [
      `Priority score of ${opportunity.score ?? 0} indicates current fit against strategic thresholds.`,
      `Opportunity status is ${formatStatusLabel(opportunity.status)}, requiring cross-functional review.`,
      `Relevant standards include ${opportunity.standards.length ? opportunity.standards.join(', ') : 'none specified yet'}.`,
    ];
  }, [opportunity]);

  const handleAddComment = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    if (!commentText.trim()) {
      return;
    }

    setSubmittingComment(true);

    try {
      const newComment = await addComment(id, commentText.trim());
      setComments((current) => [newComment, ...current]);
      setCommentText('');
    } catch (commentError) {
      setError(getApiErrorMessage(commentError, 'Unable to add comment.'));
    } finally {
      setSubmittingComment(false);
    }
  };

  if (loading) {
    return <LoadingSpinner label="Loading opportunity details..." />;
  }

  if (!opportunity) {
    return <EmptyState icon={FileStack} title="Opportunity unavailable" description={error || 'The requested opportunity could not be found.'} />;
  }

  return (
    <div className="space-y-6">
      <button
        type="button"
        onClick={() => navigate(-1)}
        className="inline-flex items-center gap-2 rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm font-medium text-slate-700 shadow-sm transition hover:bg-slate-50"
      >
        <ArrowLeft className="h-4 w-4" />
        Back
      </button>

      {error ? <div className="rounded-2xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">{error}</div> : null}

      <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
        <div className="flex flex-col gap-5 xl:flex-row xl:items-start xl:justify-between">
          <div className="max-w-3xl">
            <p className="text-sm font-medium text-blue-600">Opportunity #{opportunity.id.slice(0, 8)}</p>
            <h1 className="mt-2 text-3xl font-semibold text-slate-900">{opportunity.title}</h1>
            <p className="mt-3 text-sm leading-7 text-slate-600">
              {opportunity.summary ?? opportunity.ai_summary ?? opportunity.description ?? 'No summary has been generated yet.'}
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-3">
            <Badge text={`Score ${opportunity.score ?? 0}`} variant={getScoreVariant(opportunity.score)} size="md" />
            <Badge text={formatStatusLabel(opportunity.status)} size="md" className={getStatusBadgeClass(opportunity.status)} />
            <div className="rounded-2xl bg-slate-100 px-4 py-2.5 text-sm font-medium text-slate-700">
              Owner: {opportunity.owner_id ? opportunity.owner_id.slice(0, 8) : 'Unassigned'}
            </div>
          </div>
        </div>
      </section>

      <section className="grid gap-6 xl:grid-cols-[1.35fr_0.95fr]">
        <div className="space-y-6">
          <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
            <h2 className="text-lg font-semibold text-slate-900">Metadata</h2>
            <div className="mt-5 grid gap-4 md:grid-cols-2">
              {[
                { label: 'Country', value: opportunity.country ?? 'Not specified', icon: Landmark },
                { label: 'Institution', value: opportunity.institution ?? 'Not specified', icon: FileStack },
                { label: 'Budget', value: opportunity.budget ?? 'Not specified', icon: Wallet },
                {
                  label: 'Deadline',
                  value: opportunity.deadline ? new Date(opportunity.deadline).toLocaleDateString() : 'Not specified',
                  icon: CalendarDays,
                },
              ].map(({ label, value, icon: Icon }) => (
                <div key={label} className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
                  <div className="flex items-center gap-3">
                    <div className="rounded-xl bg-white p-2 text-blue-600 shadow-sm">
                      <Icon className="h-4 w-4" />
                    </div>
                    <div>
                      <p className="text-xs font-medium uppercase tracking-[0.2em] text-slate-400">{label}</p>
                      <p className="mt-1 text-sm font-semibold text-slate-900">{value}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            <div className="mt-5">
              <p className="text-xs font-medium uppercase tracking-[0.2em] text-slate-400">Standards</p>
              <div className="mt-3 flex flex-wrap gap-2">
                {opportunity.standards.length ? (
                  opportunity.standards.map((standard) => (
                    <span key={standard} className="rounded-full bg-blue-50 px-3 py-1 text-xs font-medium text-blue-700 ring-1 ring-blue-100">
                      {standard}
                    </span>
                  ))
                ) : (
                  <span className="text-sm text-slate-500">No standards tagged yet.</span>
                )}
              </div>
            </div>
          </div>

          <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
            <div className="mb-4 flex items-center gap-3">
              <div className="rounded-xl bg-blue-50 p-2 text-blue-600">
                <Sparkles className="h-5 w-5" />
              </div>
              <h2 className="text-lg font-semibold text-slate-900">AI Summary</h2>
            </div>
            <p className="text-sm leading-7 text-slate-600">
              {opportunity.ai_summary ?? opportunity.summary ?? opportunity.description ?? 'AI summary will appear after enrichment completes.'}
            </p>
          </div>

          <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
            <h2 className="text-lg font-semibold text-slate-900">AI Reasoning</h2>
            <ul className="mt-4 space-y-3 text-sm leading-7 text-slate-600">
              {reasoningPoints.map((point) => (
                <li key={point} className="flex gap-3">
                  <span className="mt-2 h-2 w-2 rounded-full bg-blue-600" />
                  <span>{point}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>

        <div className="space-y-6">
          <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
            <h2 className="text-lg font-semibold text-slate-900">Source Documents</h2>
            <div className="mt-4 space-y-3">
              {opportunity.source_url ? (
                <a
                  href={opportunity.source_url}
                  target="_blank"
                  rel="noreferrer"
                  className="inline-flex items-center gap-2 text-sm font-medium text-blue-600 transition hover:text-blue-700"
                >
                  <FileStack className="h-4 w-4" />
                  Open source record
                </a>
              ) : (
                <p className="text-sm text-slate-500">No source document links are currently available.</p>
              )}
            </div>
          </div>

          <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
            <div className="mb-4 flex items-center gap-3">
              <div className="rounded-xl bg-slate-100 p-2 text-slate-700">
                <MessageSquare className="h-5 w-5" />
              </div>
              <h2 className="text-lg font-semibold text-slate-900">Comments</h2>
            </div>

            <form className="mb-5 space-y-3" onSubmit={handleAddComment}>
              <textarea
                value={commentText}
                onChange={(event) => setCommentText(event.target.value)}
                rows={4}
                placeholder="Add capture strategy notes, qualification context, or follow-up tasks"
                className="w-full rounded-2xl border border-slate-200 px-4 py-3 text-sm text-slate-900 outline-none focus:border-blue-500 focus:ring-4 focus:ring-blue-100"
              />
              <button
                type="submit"
                disabled={submittingComment}
                className="inline-flex items-center gap-2 rounded-xl bg-blue-600 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-70"
              >
                <Send className="h-4 w-4" />
                {submittingComment ? 'Saving...' : 'Add Comment'}
              </button>
            </form>

            <div className="space-y-4">
              {comments.length ? (
                comments.map((comment) => (
                  <div key={comment.id} className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
                    <div className="flex items-center justify-between gap-3">
                      <p className="text-sm font-semibold text-slate-900">{comment.user.full_name}</p>
                      <p className="text-xs text-slate-500">{new Date(comment.created_at).toLocaleString()}</p>
                    </div>
                    <p className="mt-3 text-sm leading-6 text-slate-600">{comment.content}</p>
                  </div>
                ))
              ) : (
                <EmptyState icon={MessageSquare} title="No comments yet" description="Add context from your qualification review to help collaborators move faster." />
              )}
            </div>
          </div>

          <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
            <h2 className="text-lg font-semibold text-slate-900">Activity Timeline</h2>
            <div className="mt-4 rounded-2xl border border-dashed border-slate-300 bg-slate-50 px-4 py-6 text-sm text-slate-500">
              Timeline events such as assignment changes, AI re-scoring, and source updates will appear here.
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};

export default OpportunityDetailPage;
