import { create } from "zustand";

import { createClient } from "@/lib/supabase/client";
import type { ChatMessage, ChatComponent, FilterTab, ParsedContent } from "@/types";

// ── SSE event shapes ──────────────────────────────────────────────────

interface DeltaEvent {
  type: "delta";
  content: string;
}

interface ComponentEvent {
  type: "component";
  component: ChatComponent;
}

interface DoneEvent {
  type: "done";
}

interface ErrorEvent {
  type: "error";
  content: string;
}

type StreamEvent = DeltaEvent | ComponentEvent | DoneEvent | ErrorEvent;

// ── Store ─────────────────────────────────────────────────────────────

export interface ChatState {
  messages: ChatMessage[];
  activeTab: FilterTab;
  isStreaming: boolean;
  sessionStart: number | null;

  setActiveTab: (tab: FilterTab) => void;
  sendMessage: (text: string) => Promise<void>;
  clearMessages: () => void;
}

export const useChatStore = create<ChatState>()((set, get) => ({
  // ── Initial state ─────────────────────────────────────────────────
  messages: [],
  activeTab: "All",
  isStreaming: false,
  sessionStart: null,

  // ── setActiveTab ──────────────────────────────────────────────────
  setActiveTab: (tab) => set({ activeTab: tab }),

  // ── clearMessages ─────────────────────────────────────────────────
  clearMessages: () => set({ messages: [], sessionStart: null }),

  // ── sendMessage ───────────────────────────────────────────────────
  sendMessage: async (text: string) => {
    const { isStreaming } = get();
    if (isStreaming || !text.trim()) return;

    const userId = crypto.randomUUID();
    const assistantId = crypto.randomUUID();
    const now = new Date().toISOString();

    // Append user bubble + streaming placeholder
    set((s) => ({
      messages: [
        ...s.messages,
        {
          id: userId,
          role: "user",
          content: text.trim(),
          components: [],
          isStreaming: false,
          timestamp: now,
        },
        {
          id: assistantId,
          role: "assistant",
          content: "",
          components: [],
          isStreaming: true,
          timestamp: now,
        },
      ],
      isStreaming: true,
      sessionStart: s.sessionStart ?? Date.now(),
    }));

    try {
      const supabase = createClient();
      const { data: { session } } = await supabase.auth.getSession();

      console.log("Session debug:", session);
      console.log("Access token:", session?.access_token);

      const apiUrl = process.env.NEXT_PUBLIC_API_URL;
      const url = `${apiUrl}/api/v1/chat/stream?message=${encodeURIComponent(text.trim())}`;

      const response = await fetch(url, {
        method: "GET",
        headers: {
          "Authorization": `Bearer ${session?.access_token ?? ""}`,
          "Accept": "text/event-stream",
          "Cache-Control": "no-cache",
        },
      });

      console.log("Response status:", response.status);

      if (!response.ok || !response.body) {
        throw new Error(`HTTP ${response.status}`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      outer: while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop() ?? "";

        for (const line of lines) {
          if (!line.startsWith("data: ")) continue;
          const raw = line.slice(6).trim();
          if (!raw) continue;

          let event: StreamEvent;
          try {
            event = JSON.parse(raw) as StreamEvent;
          } catch {
            continue;
          }

          if (event.type === "delta") {
            set((s) => ({
              messages: s.messages.map((m) =>
                m.id === assistantId
                  ? { ...m, content: m.content + event.content }
                  : m,
              ),
            }));
          } else if (event.type === "component") {
            set((s) => ({
              messages: s.messages.map((m) =>
                m.id === assistantId
                  ? { ...m, components: [...m.components, event.component] }
                  : m,
              ),
            }));
          } else if (event.type === "done") {
            const raw =
              get().messages.find((m) => m.id === assistantId)?.content ?? "";

            // Try to extract JSON from anywhere in the response.
            // Claude sometimes outputs prose before the JSON block.
            let parsed: Record<string, unknown> | null = null;

            // First try: direct parse (clean JSON response)
            try {
              const clean = raw
                .replace(/^```json\s*/i, "")
                .replace(/```\s*$/, "")
                .trim();
              const candidate = JSON.parse(clean) as Record<string, unknown>;
              if (candidate.text !== undefined) parsed = candidate;
            } catch {}

            // Second try: extract JSON block from mixed content
            if (!parsed) {
              const jsonMatch =
                raw.match(/```json\s*([\s\S]*?)```/i) ??
                raw.match(/(\{[\s\S]*"text"[\s\S]*"components"[\s\S]*\})/);
              if (jsonMatch) {
                try {
                  const candidate = JSON.parse(jsonMatch[1]) as Record<string, unknown>;
                  if (candidate.text !== undefined) parsed = candidate;
                } catch {}
              }
            }

            if (parsed) {
              set((s) => ({
                messages: s.messages.map((m) =>
                  m.id === assistantId
                    ? {
                        ...m,
                        isStreaming: false,
                        parsedContent: parsed as unknown as ParsedContent,
                      }
                    : m,
                ),
                isStreaming: false,
              }));
            } else {
              set((s) => ({
                messages: s.messages.map((m) =>
                  m.id === assistantId ? { ...m, isStreaming: false } : m,
                ),
                isStreaming: false,
              }));
            }
            break outer;
          } else if (event.type === "error") {
            throw new Error(event.content ?? "Stream error");
          }
        }
      }
    } catch {
      set((s) => ({
        messages: s.messages.map((m) =>
          m.id === assistantId
            ? {
                ...m,
                content:
                  "Sorry, I couldn't reach the server. Please try again.",
                isStreaming: false,
                isError: true,
              }
            : m,
        ),
        isStreaming: false,
      }));
    }
  },
}));
