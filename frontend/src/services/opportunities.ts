import { get, patch, post } from '@/services/api';
import type {
  Comment,
  Opportunity,
  OpportunityDetail,
  PaginatedResponse,
  SearchFilters,
} from '@/utils/types';

export const searchOpportunities = (filters: SearchFilters) =>
  post<PaginatedResponse<Opportunity>>('/opportunities/search', filters);

export const getOpportunity = (id: string) =>
  get<OpportunityDetail>(`/opportunities/${id}`);

export const updateOpportunity = (id: string, data: Partial<OpportunityDetail>) =>
  patch<OpportunityDetail>(`/opportunities/${id}`, data);

export const addComment = (id: string, content: string) =>
  post<Comment>(`/opportunities/${id}/comments`, { content });

export const getComments = (id: string) =>
  get<Comment[]>(`/opportunities/${id}/comments`);
