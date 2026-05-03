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
  message: string;
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

      if (!response.ok || !response.body) {
        throw new Error(`HTTP ${response.status}`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      // Inner try/finally guarantees the reader is always released, regardless of
      // how the loop exits (break outer, reader exhausted, or thrown error).
      // Without this, the browser keeps the connection locked between queries —
      // on HTTP/1.1 backends this blocks the second request from ever starting.
      try {
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
              const accumulated =
                get().messages.find((m) => m.id === assistantId)?.content ?? "";

              // Try to extract JSON from anywhere in the response.
              // Claude sometimes outputs prose before the JSON block.
              let parsed: Record<string, unknown> | null = null;

              // First try: direct parse (clean JSON response)
              try {
                const clean = accumulated
                  .replace(/^```json\s*/i, "")
                  .replace(/```\s*$/, "")
                  .trim();
                const candidate = JSON.parse(clean) as Record<string, unknown>;
                if (candidate.text !== undefined) parsed = candidate;
              } catch {}

              // Second try: extract JSON block from mixed content
              if (!parsed) {
                const jsonMatch =
                  accumulated.match(/```json\s*([\s\S]*?)```/i) ??
                  accumulated.match(/(\{[\s\S]*"text"[\s\S]*"components"[\s\S]*\})/);
                if (jsonMatch) {
                  try {
                    const candidate = JSON.parse(jsonMatch[1]) as Record<string, unknown>;
                    if (candidate.text !== undefined) parsed = candidate;
                  } catch {}
                }
              }

              if (parsed) {
                // Normalize: if parsed.text is empty, fall back to the raw accumulated content
                const finalText =
                  typeof parsed.text === "string" && parsed.text.trim()
                    ? parsed.text
                    : accumulated;
                const finalComponents = Array.isArray(parsed.components)
                  ? (parsed.components as ChatComponent[])
                  : [];
                set((s) => ({
                  messages: s.messages.map((m) =>
                    m.id === assistantId
                      ? {
                          ...m,
                          isStreaming: false,
                          parsedContent: { text: finalText, components: finalComponents },
                        }
                      : m,
                  ),
                  isStreaming: false,
                }));
              } else {
                // JSON parsing failed — wrap the raw content so the bubble never renders blank
                set((s) => ({
                  messages: s.messages.map((m) =>
                    m.id === assistantId
                      ? {
                          ...m,
                          isStreaming: false,
                          ...(accumulated
                            ? { parsedContent: { text: accumulated, components: [] } }
                            : {}),
                        }
                      : m,
                  ),
                  isStreaming: false,
                }));
              }
              break outer;
            } else if (event.type === "error") {
              throw new Error(event.message ?? "Stream error");
            }
          }
        }

        // Safety net: if the stream closed without a done event, reset isStreaming.
        // Uses get() for fresh state — assistantId is from the current call's closure.
        const stillStreaming = get().messages.find((m) => m.id === assistantId)?.isStreaming;
        if (stillStreaming) {
          const fallbackContent =
            get().messages.find((m) => m.id === assistantId)?.content ?? "";
          set((s) => ({
            messages: s.messages.map((m) =>
              m.id === assistantId
                ? {
                    ...m,
                    isStreaming: false,
                    ...(fallbackContent
                      ? { parsedContent: { text: fallbackContent, components: [] } }
                      : {}),
                  }
                : m,
            ),
            isStreaming: false,
          }));
        }
      } finally {
        // Release the reader unconditionally so the browser can close/reuse
        // the connection before the next sendMessage call begins.
        void reader.cancel();
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
