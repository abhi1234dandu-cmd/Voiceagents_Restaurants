from datetime import datetime
from enum import Enum
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class MembershipRole(str, Enum):
    owner = "owner"
    admin = "admin"
    staff = "staff"
    viewer = "viewer"


class OrgStatus(str, Enum):
    active = "active"
    suspended = "suspended"
    past_due = "past_due"


class ReservationStatus(str, Enum):
    pending = "pending"
    confirmed = "confirmed"
    cancelled = "cancelled"
    no_show = "no_show"


class Organization(BaseModel):
    id: UUID
    name: str
    slug: str
    stripe_customer_id: Optional[str] = None
    plan: str = "free"
    status: OrgStatus = OrgStatus.active
    created_at: datetime


class OrganizationCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)


class Membership(BaseModel):
    id: UUID
    org_id: UUID
    user_id: UUID
    role: MembershipRole
    created_at: datetime


class Restaurant(BaseModel):
    id: UUID
    org_id: UUID
    name: str
    timezone: str = "America/Chicago"
    phone_e164: Optional[str] = None
    address_json: dict[str, Any] = Field(default_factory=dict)
    transfer_number_e164: Optional[str] = None
    sms_from_number: Optional[str] = None
    hours_json: dict[str, Any] = Field(default_factory=dict)
    status: str = "draft"
    created_at: datetime


class RestaurantCreate(BaseModel):
    name: str
    timezone: str = "America/Chicago"
    transfer_number_e164: Optional[str] = None
    address_json: dict[str, Any] = Field(default_factory=dict)
    hours_json: dict[str, Any] = Field(default_factory=dict)


class RestaurantUpdate(BaseModel):
    name: Optional[str] = None
    timezone: Optional[str] = None
    transfer_number_e164: Optional[str] = None
    address_json: Optional[dict[str, Any]] = None
    hours_json: Optional[dict[str, Any]] = None
    status: Optional[str] = None


class VoiceAgent(BaseModel):
    id: UUID
    restaurant_id: UUID
    twilio_number_sid: Optional[str] = None
    twilio_phone_e164: Optional[str] = None
    voice_id: str
    language: str = "en"
    system_prompt: str = ""
    greeting: str = "Thanks for calling. How can I help you today?"
    transfer_policy_json: dict[str, Any] = Field(default_factory=dict)
    active: bool = False
    created_at: datetime


class VoiceAgentUpdate(BaseModel):
    voice_id: Optional[str] = None  # ElevenLabs voice id
    language: Optional[str] = None
    system_prompt: Optional[str] = None
    greeting: Optional[str] = None
    transfer_policy_json: Optional[dict[str, Any]] = None
    active: Optional[bool] = None


class FAQ(BaseModel):
    id: UUID
    restaurant_id: UUID
    question: str
    answer: str
    tags: list[str] = Field(default_factory=list)
    active: bool = True
    embedding: Optional[list[float]] = None


class FAQCreate(BaseModel):
    question: str
    answer: str
    tags: list[str] = Field(default_factory=list)
    active: bool = True


class MenuItem(BaseModel):
    id: UUID
    menu_id: UUID
    name: str
    description: str = ""
    price_cents: int
    category: str = "general"
    allergens_json: list[str] = Field(default_factory=list)
    available: bool = True


class MenuItemCreate(BaseModel):
    name: str
    description: str = ""
    price_cents: int
    category: str = "general"
    allergens_json: list[str] = Field(default_factory=list)
    available: bool = True


class Reservation(BaseModel):
    id: UUID
    restaurant_id: UUID
    guest_name: str
    guest_phone: str
    party_size: int
    starts_at: datetime
    status: ReservationStatus
    source: str = "voice"
    notes: Optional[str] = None
    confirmation_code: str


class ReservationCreate(BaseModel):
    guest_name: str
    guest_phone: str
    party_size: int = Field(ge=1, le=20)
    starts_at: datetime
    notes: Optional[str] = None
    source: str = "dashboard"


class Call(BaseModel):
    id: UUID
    restaurant_id: UUID
    twilio_call_sid: str
    from_number: Optional[str] = None
    to_number: Optional[str] = None
    direction: str = "inbound"
    started_at: datetime
    ended_at: Optional[datetime] = None
    duration_sec: Optional[int] = None
    outcome: Optional[str] = None
    recording_url: Optional[str] = None
    recording_storage_path: Optional[str] = None
    cost_estimate_cents: Optional[int] = None


class CallTurn(BaseModel):
    id: UUID
    call_id: UUID
    role: str
    content: str
    tool_name: Optional[str] = None
    latency_ms: Optional[int] = None
    created_at: datetime


class AnalyticsSummary(BaseModel):
    total_calls: int
    answered_calls: int
    reservations_booked: int
    transfers: int
    voice_minutes: float
    by_day: list[dict[str, Any]]


class CheckoutSessionResponse(BaseModel):
    url: str


class ToolRequest(BaseModel):
    restaurant_id: UUID
    call_id: Optional[UUID] = None
    args: dict[str, Any] = Field(default_factory=dict)


class ToolResponse(BaseModel):
    ok: bool
    result: dict[str, Any] = Field(default_factory=dict)
    error: Optional[str] = None
