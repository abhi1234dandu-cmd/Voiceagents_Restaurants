/**
 * Shared API types for Restaurant Voice SaaS.
 * Hand-maintained mirror of FastAPI OpenAPI (`GET /openapi-export.json`).
 * Regenerate via `npm run generate -w packages/shared-types` when the API is running.
 */

export type MembershipRole = "owner" | "admin" | "staff" | "viewer";
export type OrgStatus = "active" | "suspended" | "past_due";
export type ReservationStatus = "pending" | "confirmed" | "cancelled" | "no_show";

export interface Organization {
  id: string;
  name: string;
  slug: string;
  stripe_customer_id?: string | null;
  plan: string;
  status: OrgStatus;
  created_at: string;
}

export interface Restaurant {
  id: string;
  org_id: string;
  name: string;
  timezone: string;
  phone_e164?: string | null;
  address_json: Record<string, unknown>;
  transfer_number_e164?: string | null;
  sms_from_number?: string | null;
  hours_json: Record<string, unknown>;
  status: string;
  created_at: string;
}

export interface VoiceAgent {
  id: string;
  restaurant_id: string;
  twilio_number_sid?: string | null;
  twilio_phone_e164?: string | null;
  /** ElevenLabs voice id used for all spoken output */
  voice_id: string;
  language: string;
  system_prompt: string;
  greeting: string;
  transfer_policy_json: Record<string, unknown>;
  active: boolean;
  created_at: string;
}

export interface FAQ {
  id: string;
  restaurant_id: string;
  question: string;
  answer: string;
  tags: string[];
  active: boolean;
}

export interface MenuItem {
  id: string;
  menu_id: string;
  name: string;
  description: string;
  price_cents: number;
  category: string;
  allergens_json: string[];
  available: boolean;
}

export interface Reservation {
  id: string;
  restaurant_id: string;
  guest_name: string;
  guest_phone: string;
  party_size: number;
  starts_at: string;
  status: ReservationStatus;
  source: string;
  notes?: string | null;
  confirmation_code: string;
}

export interface Call {
  id: string;
  restaurant_id: string;
  twilio_call_sid: string;
  from_number?: string | null;
  to_number?: string | null;
  direction: string;
  started_at: string;
  ended_at?: string | null;
  duration_sec?: number | null;
  outcome?: string | null;
  recording_url?: string | null;
  cost_estimate_cents?: number | null;
}

export interface CallTurn {
  id: string;
  call_id: string;
  role: string;
  content: string;
  tool_name?: string | null;
  latency_ms?: number | null;
  created_at: string;
}

export interface AnalyticsSummary {
  total_calls: number;
  answered_calls: number;
  reservations_booked: number;
  transfers: number;
  voice_minutes: number;
  by_day: Array<Record<string, unknown>>;
}

export interface CheckoutSessionResponse {
  url: string;
}

export interface Membership {
  id: string;
  org_id: string;
  user_id: string;
  role: MembershipRole;
  created_at: string;
}
