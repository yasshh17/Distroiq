"use client";

import {
  useRef,
  useEffect,
  useState,
  type KeyboardEvent,
  type FormEvent,
} from "react";
import { Send } from "lucide-react";

import { useChatStore } from "@/stores/chat";
import { WelcomeScreen } from "@/components/features/chat/WelcomeScreen";
import { MessageRow } from "@/components/features/chat/MessageRow";
import { UserBubble } from "@/components/features/chat/UserBubble";
import { AIBubble } from "@/components/features/chat/AIBubble";
import { TypingBubble } from "@/components/features/chat/TypingIndicator";
import { DataTable } from "@/components/features/chat/DataTable";
import { AlertBanner } from "@/components/features/chat/AlertBanner";
import { EmailCard } from "@/components/features/chat/EmailCard";
import { SourceCitation } from "@/components/features/chat/SourceCitation";
import type { ChatComponent, FilterTab } from "@/types";

const TABS: FilterTab[] = [
  "All",
  "Inventory",
  "Orders",
  "Customers",
  "Suppliers",
  "Actions",
];

// ── Component renderer ────────────────────────────────────────────────

function renderComponent(c: ChatComponent, i: number) {
  if (c.type === "table") {
    return (
      <DataTable
        key={i}
        headers={c.headers}
        rows={c.rows}
        statusCol={c.statusCol}
      />
    );
  }
  if (c.type === "alert") {
    return (
      <AlertBanner key={i} type={c.alertType} title={c.title} message={c.message} />
    );
  }
  if (c.type === "email") {
    return (
      <EmailCard key={i} to={c.to} cc={c.cc} subject={c.subject} body={c.body} />
    );
  }
  if (c.type === "citation") {
    return <SourceCitation key={i} sources={c.sources} />;
  }
  return null;
}

// ── Session timer ─────────────────────────────────────────────────────

function useSessionTimer(sessionStart: number | null) {
  const [elapsed, setElapsed] = useState("00:00:00");

  useEffect(() => {
    if (sessionStart === null) {
      setElapsed("00:00:00");
      return;
    }

    const tick = () => {
      const s = Math.floor((Date.now() - sessionStart) / 1000);
      const hh = String(Math.floor(s / 3600)).padStart(2, "0");
      const mm = String(Math.floor((s % 3600) / 60)).padStart(2, "0");
      const ss = String(s % 60).padStart(2, "0");
      setElapsed(`${hh}:${mm}:${ss}`);
    };

    tick();
    const id = setInterval(tick, 1000);
    return () => clearInterval(id);
  }, [sessionStart]);

  return elapsed;
}

// ── Page ──────────────────────────────────────────────────────────────

export default function DashboardPage() {
  const messages = useChatStore((s) => s.messages);
  const activeTab = useChatStore((s) => s.activeTab);
  const isStreaming = useChatStore((s) => s.isStreaming);
  const sessionStart = useChatStore((s) => s.sessionStart);
  const setActiveTab = useChatStore((s) => s.setActiveTab);
  const sendMessage = useChatStore((s) => s.sendMessage);

  const [draft, setDraft] = useState("");
  const bottomRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const elapsed = useSessionTimer(sessionStart);

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Auto-resize textarea
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
      {/* ── Toolbar ──────────────────────────────────────────────── */}
      <div className="flex h-[50px] shrink-0 items-center justify-between border-b border-slate-200 bg-white px-4">
        <div className="flex items-center gap-0.5">
          {TABS.map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`rounded-md px-3 py-1.5 text-[12.5px] font-medium transition-colors ${
                tab === activeTab
                  ? "bg-slate-900 text-white"
                  : "text-slate-500 hover:bg-slate-100 hover:text-slate-700"
              }`}
            >
              {tab}
            </button>
          ))}
        </div>
        <div className="flex items-center gap-2">
          <span
            className={`h-1.5 w-1.5 rounded-full transition-colors ${
              isStreaming ? "bg-blue-400 animate-pulse" : "bg-emerald-400"
            }`}
          />
          <span className="font-mono text-[11px] text-slate-400">
            Session · {elapsed}
          </span>
        </div>
      </div>

      {/* ── Message area ─────────────────────────────────────────── */}
      <div className="flex flex-1 flex-col overflow-y-auto">
        <div className="mx-auto w-full max-w-3xl flex-1 px-6">
          {!hasMessages ? (
            <WelcomeScreen />
          ) : (
            <div className="space-y-5 py-6">
              {messages.map((msg) => {
                if (msg.role === "user") {
                  return (
                    <MessageRow
                      key={msg.id}
                      role="user"
                      timestamp={new Date(msg.timestamp).toLocaleTimeString(
                        [],
                        { hour: "2-digit", minute: "2-digit" },
                      )}
                    >
                      <UserBubble>{msg.content}</UserBubble>
                    </MessageRow>
                  );
                }

                // Streaming placeholder
                if (msg.isStreaming && !msg.content) {
                  return (
                    <TypingBubble key={msg.id} />
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
                        // While streaming: show dots, not raw JSON
                        <div className="flex items-center gap-1 py-1">
                          <div className="h-2 w-2 rounded-full bg-slate-300 animate-bounce [animation-delay:-0.3s]" />
                          <div className="h-2 w-2 rounded-full bg-slate-300 animate-bounce [animation-delay:-0.15s]" />
                          <div className="h-2 w-2 rounded-full bg-slate-300 animate-bounce" />
                        </div>
                      ) : msg.parsedContent ? (
                        // Streaming done + JSON parsed: render rich components
                        <>
                          {msg.parsedContent.text && (
                            <p className="whitespace-pre-wrap">
                              {msg.parsedContent.text}
                            </p>
                          )}
                          {msg.parsedContent.components.map((c, i) =>
                            renderComponent(c, i),
                          )}
                        </>
                      ) : (
                        // Streaming done + plain text: render as-is
                        <p className="whitespace-pre-wrap">{msg.content}</p>
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
      <div className="shrink-0 bg-white px-4 pb-4 pt-3 shadow-[0_-1px_0_0_rgb(226,232,240)]">
        <div className="mx-auto max-w-3xl">
          <form
            onSubmit={handleSubmit}
            className="flex items-end gap-3 rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 transition-all focus-within:border-blue-400 focus-within:ring-2 focus-within:ring-blue-100"
          >
            <textarea
              ref={textareaRef}
              rows={1}
              value={draft}
              onChange={(e) => setDraft(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask about inventory, orders, suppliers, customers…"
              className="flex-1 resize-none bg-transparent text-[13.5px] leading-relaxed text-slate-700 placeholder:text-slate-400 focus:outline-none"
              disabled={isStreaming}
            />
            <button
              type="submit"
              disabled={!draft.trim() || isStreaming}
              className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-blue-600 shadow-sm transition-colors hover:bg-blue-700 active:bg-blue-800 disabled:cursor-not-allowed disabled:opacity-40"
            >
              <Send className="h-3.5 w-3.5 text-white" />
            </button>
          </form>
          <p className="mt-2 text-center font-mono text-[10px] text-slate-300">
            RAG-powered · Responses grounded in live operational data
          </p>
        </div>
      </div>
    </>
  );
}
