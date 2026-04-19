"use client";

import {
  useRef,
  useEffect,
  useState,
  type KeyboardEvent,
  type FormEvent,
} from "react";
import { Zap, ArrowUp } from "lucide-react";

import { useChatStore } from "@/stores/chat";
import { WelcomeScreen } from "@/components/features/chat/WelcomeScreen";
import { MessageRow } from "@/components/features/chat/MessageRow";
import { UserBubble } from "@/components/features/chat/UserBubble";
import { AIBubble } from "@/components/features/chat/AIBubble";
import { DataTable } from "@/components/features/chat/DataTable";
import { AlertBanner } from "@/components/features/chat/AlertBanner";
import { EmailCard } from "@/components/features/chat/EmailCard";
import { SourceCitation } from "@/components/features/chat/SourceCitation";
import type { ChatComponent } from "@/types";

function renderComponent(c: ChatComponent, i: number) {
  if (c.type === "table") {
    return <DataTable key={i} headers={c.headers} rows={c.rows} statusCol={c.statusCol} />;
  }
  if (c.type === "alert") {
    return <AlertBanner key={i} type={c.alertType} title={c.title} message={c.message} />;
  }
  if (c.type === "email") {
    return <EmailCard key={i} to={c.to} cc={c.cc} subject={c.subject} body={c.body} />;
  }
  if (c.type === "citation") {
    return <SourceCitation key={i} sources={c.sources} />;
  }
  return null;
}

export default function DashboardPage() {
  const messages = useChatStore((s) => s.messages);
  const isStreaming = useChatStore((s) => s.isStreaming);
  const sendMessage = useChatStore((s) => s.sendMessage);

  const [draft, setDraft] = useState("");
  const bottomRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  useEffect(() => {
    const el = textareaRef.current;
    if (!el) return;
    el.style.height = "auto";
    el.style.height = `${Math.min(el.scrollHeight, 160)}px`;
  }, [draft]);

  function handleSend() {
    const text = draft.trim();
    if (!text || isStreaming) return;
    setDraft("");
    sendMessage(text);
  }

  function handleKeyDown(e: KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  }

  function handleSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    handleSend();
  }

  const hasMessages = messages.length > 0;

  return (
    <>
      {/* ── Message area ─────────────────────────────────────────── */}
      <div className="flex flex-1 flex-col overflow-y-auto">
        <div className="mx-auto w-full max-w-3xl flex-1 px-4 sm:px-6">
          {!hasMessages ? (
            <WelcomeScreen />
          ) : (
            <div className="space-y-6 py-6">
              {messages.map((msg) => {
                if (msg.role === "user") {
                  return (
                    <MessageRow
                      key={msg.id}
                      role="user"
                      timestamp={new Date(msg.timestamp).toLocaleTimeString([], {
                        hour: "2-digit",
                        minute: "2-digit",
                      })}
                    >
                      <UserBubble>{msg.content}</UserBubble>
                    </MessageRow>
                  );
                }

                /* Skeleton while waiting for first token */
                if (msg.isStreaming && !msg.content) {
                  return (
                    <MessageRow key={msg.id} role="ai">
                      <AIBubble>
                        <div className="space-y-2.5 py-0.5">
                          <div className="h-2.5 w-[85%] animate-pulse rounded-full bg-white/[0.08]" />
                          <div className="h-2.5 w-[65%] animate-pulse rounded-full bg-white/[0.08]" />
                          <div className="h-2.5 w-[75%] animate-pulse rounded-full bg-white/[0.08]" />
                        </div>
                      </AIBubble>
                    </MessageRow>
                  );
                }

                /* Error state */
                if (msg.isError) {
                  const lastUserMsg = messages
                    .slice(0, messages.indexOf(msg))
                    .findLast((m) => m.role === "user");

                  return (
                    <MessageRow key={msg.id} role="ai">
                      <div className="flex flex-col gap-2">
                        <AlertBanner
                          type="danger"
                          title="Couldn't reach the server"
                          message="The request failed. Check your connection or try again."
                        />
                        {lastUserMsg && (
                          <button
                            onClick={() => sendMessage(lastUserMsg.content)}
                            className="font-grotesk self-start rounded-[8px] border border-white/[0.08] bg-[#1f2a3d] px-3 py-1.5 text-[11px] font-medium uppercase tracking-wide text-white/50 transition-colors hover:border-[#2563eb]/40 hover:text-[#2563eb]"
                          >
                            Retry
                          </button>
                        )}
                      </div>
                    </MessageRow>
                  );
                }

                return (
                  <MessageRow
                    key={msg.id}
                    role="ai"
                    timestamp={new Date(msg.timestamp).toLocaleTimeString([], {
                      hour: "2-digit",
                      minute: "2-digit",
                    })}
                  >
                    <AIBubble>
                      {msg.isStreaming ? (
                        <div className="flex items-center gap-1.5 py-1">
                          <div className="h-2 w-2 rounded-full bg-[#2563eb]/60" style={{ animation: "bounce-dot 1.3s ease-in-out infinite 0s" }} />
                          <div className="h-2 w-2 rounded-full bg-[#2563eb]/60" style={{ animation: "bounce-dot 1.3s ease-in-out infinite 0.15s" }} />
                          <div className="h-2 w-2 rounded-full bg-[#2563eb]/60" style={{ animation: "bounce-dot 1.3s ease-in-out infinite 0.3s" }} />
                        </div>
                      ) : msg.parsedContent ? (
                        <>
                          {msg.parsedContent.text && (
                            <p className="whitespace-pre-wrap leading-relaxed text-white/90">
                              {msg.parsedContent.text}
                            </p>
                          )}
                          {msg.parsedContent.components?.map((c, i) =>
                            renderComponent(c, i),
                          )}
                        </>
                      ) : (
                        <p className="whitespace-pre-wrap text-white/90">{msg.content}</p>
                      )}
                    </AIBubble>
                  </MessageRow>
                );
              })}
              <div ref={bottomRef} />
            </div>
          )}
        </div>
      </div>

      {/* ── Input bar ────────────────────────────────────────────── */}
      <div
        className="shrink-0 border-t border-white/[0.08] bg-[#101c2e] px-5 py-3"
        style={{ boxShadow: "0 -4px 24px rgba(37,99,235,0.04)" }}
      >
        <div className="mx-auto max-w-3xl">
          <form onSubmit={handleSubmit}>
            {/* Input field wrapper */}
            <div
              className="input-glow-wrapper flex items-center gap-3 rounded-[12px] border border-white/[0.08] bg-[#1f2a3d] px-4 py-3 transition-all duration-150"
              style={
                {
                  "--glow-border": "var(--kp-accent)",
                  "--glow-shadow": "var(--kp-accent-glow)",
                } as React.CSSProperties
              }
            >
              <Zap className="h-4 w-4 shrink-0 text-[#2563eb]" />
              <textarea
                ref={textareaRef}
                rows={1}
                value={draft}
                onChange={(e) => setDraft(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Ask DistroIQ..."
                disabled={isStreaming}
                className="font-grotesk flex-1 resize-none bg-transparent text-[14px] leading-relaxed text-white/95 placeholder:text-white/30 focus:outline-none disabled:cursor-not-allowed"
              />
              <div className="flex shrink-0 items-center gap-2.5">
                <span className="font-grotesk hidden rounded border border-white/[0.08] bg-[#2a3548] px-2 py-[3px] text-[10px] uppercase tracking-wide text-white/30 sm:inline">
                  CMD+K
                </span>
                <button
                  type="submit"
                  disabled={!draft.trim() || isStreaming}
                  className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-[#2563eb] transition-colors hover:bg-[#1d4ed8] disabled:cursor-not-allowed disabled:opacity-40"
                >
                  <ArrowUp className="h-4 w-4 text-white" />
                </button>
              </div>
            </div>
          </form>
          <p className="font-grotesk mt-1.5 text-center text-[10px] uppercase tracking-widest text-white/20">
            RAG-powered · Responses grounded in live operational data
          </p>
        </div>
      </div>
    </>
  );
}
