import type { Session } from "@supabase/supabase-js";

// ── User ─────────────────────────────────────────────────────────────

export interface User {
  id: string;
  email: string;
  full_name: string | null;
  created_at: string;
}

// ── Auth ─────────────────────────────────────────────────────────────

export interface AuthState {
  user: User | null;
  session: Session | null;
  isLoading: boolean;
}

// ── Chat ─────────────────────────────────────────────────────────────

export type MessageRole = "user" | "assistant";

export interface Message {
  id: string;
  conversation_id: string;
  role: MessageRole;
  content: string;
  created_at: string;
}

export interface Conversation {
  id: string;
  user_id: string;
  title: string | null;
  created_at: string;
}

// ── AI Response components ────────────────────────────────────────────

export interface TableComponent {
  type: "table";
  headers: string[];
  rows: string[][];
  statusCol?: number;
}

export interface AlertComponent {
  type: "alert";
  alertType: "danger" | "warn" | "ok" | "info";
  title: string;
  message: string;
}

export interface EmailComponent {
  type: "email";
  to: string;
  cc?: string;
  subject: string;
  body: string;
}

export interface CitationComponent {
  type: "citation";
  sources: string[];
}

export type ChatComponent =
  | TableComponent
  | AlertComponent
  | EmailComponent
  | CitationComponent;

export type FilterTab =
  | "All"
  | "Inventory"
  | "Orders"
  | "Customers"
  | "Suppliers"
  | "Actions";

export interface ParsedContent {
  text: string;
  components: ChatComponent[];
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  components: ChatComponent[];
  isStreaming: boolean;
  isError?: boolean;
  timestamp: string;
  parsedContent?: ParsedContent;
}
