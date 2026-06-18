import { create } from "zustand";

import { createClient } from "@/lib/supabase/client";
import type { ChatMessage, ChatComponent, FilterTab, ParsedContent } from "@/types";

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
  messages: [],
  activeTab: "All",
  isStreaming: false,
  sessionStart: null,

  setActiveTab: (tab) => set({ activeTab: tab }),

  clearMessages: () => set({ messages: [], sessionStart: null }),

  sendMessage: async (text: string) => {
    const { isStreaming } = get();
    if (isStreaming || !text.trim()) return;

    const userId = crypto.randomUUID();
    const assistantId = crypto.randomUUID();
    const now = new Date().toISOString();

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

              // Claude sometimes outputs prose before the JSON block
              let parsed: Record<string, unknown> | null = null;

              // Trim first so regex anchors work even with leading newlines
              const trimmed = accumulated.trim();
              const clean = trimmed
                .replace(/^```json\s*/i, "")
                .replace(/```\s*$/, "")
                .trim();

              try {
                const candidate = JSON.parse(clean) as Record<string, unknown>;
                if (candidate.text !== undefined) parsed = candidate;
              } catch {}

              // Fallback: extract from first { to last }
              if (!parsed) {
                const first = accumulated.indexOf("{");
                const last = accumulated.lastIndexOf("}");
                if (first !== -1 && last > first) {
                  try {
                    const candidate = JSON.parse(accumulated.slice(first, last + 1)) as Record<string, unknown>;
                    if (candidate.text !== undefined) parsed = candidate;
                  } catch {}
                }
              }

              if (parsed) {
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
