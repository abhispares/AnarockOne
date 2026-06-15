import React, { useEffect, useRef, useState } from "react";
import { createRoot } from "react-dom/client";
import {
  ArrowUp,
  Bot,
  ChevronDown,
  Check,
  CircleAlert,
  Pencil,
  MessageSquarePlus,
  PanelLeftClose,
  PanelLeftOpen,
  Loader2,
  Mail,
  MessageSquareText,
  Search,
  UserRound,
  UsersRound,
  X,
  BriefcaseBusiness,
} from "lucide-react";
import "./styles.css";

const API_URL =
  import.meta.env.VITE_RELATIONSHIP_API_URL ||
  "/relationship-intelligence/invoke";

const sourceIcons = {
  "Microsoft Teams meeting": UsersRound,
  "Outlook email": Mail,
  "BD Tracker update": BriefcaseBusiness,
};

const TYPE_SPEED_MS = 12;
const TYPE_CHUNK_SIZE = 3;
const EMPTY_MESSAGES = [
  {
    id: "welcome",
    role: "assistant",
    content: "",
    sources: [],
  },
];

function createMessageId() {
  if (globalThis.crypto?.randomUUID) {
    return globalThis.crypto.randomUUID();
  }

  return `message-${Date.now().toString(36)}-${Math.random().toString(36).slice(2)}`;
}

function SourceIcon({ source }) {
  const Icon = sourceIcons[source] || MessageSquareText;
  return <Icon size={14} aria-hidden="true" />;
}

function renderInlineText(text, keyPrefix) {
  const parts = text.split(/(\*\*[^*]+\*\*)/g);

  return parts.map((part, partIndex) => {
    if (part.startsWith("**") && part.endsWith("**")) {
      return <strong key={`${keyPrefix}-${partIndex}`}>{part.slice(2, -2)}</strong>;
    }

    return <React.Fragment key={`${keyPrefix}-${partIndex}`}>{part}</React.Fragment>;
  });
}

function isTableLine(line) {
  return line.trim().startsWith("|") && line.trim().endsWith("|");
}

function isTableSeparator(line) {
  return /^\s*\|?[\s:-]+\|[\s|:-]*\|?\s*$/.test(line);
}

function parseTableLine(line) {
  return line
    .trim()
    .replace(/^\|/, "")
    .replace(/\|$/, "")
    .split("|")
    .map((cell) => cell.trim());
}

function MessageTable({ lines, tableIndex }) {
  const rows = lines.filter((line) => !isTableSeparator(line)).map(parseTableLine);
  const [header = [], ...bodyRows] = rows;

  if (!header.length || !bodyRows.length) {
    return (
      <div className="message-paragraph">
        {lines.map((line, lineIndex) => (
          <React.Fragment key={`fallback-${tableIndex}-${lineIndex}`}>
            {renderInlineText(line, `fallback-${tableIndex}-${lineIndex}`)}
            {lineIndex < lines.length - 1 ? <br /> : null}
          </React.Fragment>
        ))}
      </div>
    );
  }

  return (
    <div className="message-table-wrap">
      <table className="message-table">
        <thead>
          <tr>
            {header.map((cell, cellIndex) => (
              <th key={`table-${tableIndex}-head-${cellIndex}`}>
                {renderInlineText(cell, `table-${tableIndex}-head-${cellIndex}`)}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {bodyRows.map((row, rowIndex) => (
            <tr key={`table-${tableIndex}-row-${rowIndex}`}>
              {header.map((_, cellIndex) => (
                <td key={`table-${tableIndex}-row-${rowIndex}-${cellIndex}`}>
                  {renderInlineText(row[cellIndex] || "", `table-${tableIndex}-${rowIndex}-${cellIndex}`)}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function FormattedMessageText({ text }) {
  const lines = text.split("\n");
  const blocks = [];
  let cursor = 0;

  while (cursor < lines.length) {
    if (isTableLine(lines[cursor])) {
      const tableLines = [];
      while (cursor < lines.length && isTableLine(lines[cursor])) {
        tableLines.push(lines[cursor]);
        cursor += 1;
      }
      blocks.push({ type: "table", lines: tableLines });
      continue;
    }

    const paragraphLines = [];
    while (cursor < lines.length && !isTableLine(lines[cursor])) {
      paragraphLines.push(lines[cursor]);
      cursor += 1;
    }
    blocks.push({ type: "text", lines: paragraphLines });
  }

  return blocks.map((block, blockIndex) => {
    if (block.type === "table") {
      return <MessageTable key={`table-${blockIndex}`} lines={block.lines} tableIndex={blockIndex} />;
    }

    return block.lines.map((line, lineIndex) => {
      const headingMatch = line.match(/^(#{1,6})\s+(.+)$/);
      const content = headingMatch ? headingMatch[2] : line;
      const renderedParts = renderInlineText(content, `${blockIndex}-${lineIndex}`);

      if (headingMatch) {
        return (
          <React.Fragment key={`line-${blockIndex}-${lineIndex}`}>
            <span className="message-heading">{renderedParts}</span>
            {lineIndex < block.lines.length - 1 ? <br /> : null}
          </React.Fragment>
        );
      }

      return (
        <React.Fragment key={`line-${blockIndex}-${lineIndex}`}>
          {line ? renderInlineText(line, `${blockIndex}-${lineIndex}`) : <br />}
          {lineIndex < block.lines.length - 1 && line ? <br /> : null}
        </React.Fragment>
      );
    });
  });
}

function App() {
  const [messages, setMessages] = useState(EMPTY_MESSAGES);
  const [chatSessions, setChatSessions] = useState([]);
  const [activeChatId, setActiveChatId] = useState(null);
  const [isHistoryOpen, setIsHistoryOpen] = useState(true);
  const [input, setInput] = useState("");
  const [editingMessageId, setEditingMessageId] = useState(null);
  const [editDraft, setEditDraft] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const inputRef = useRef(null);
  const messagesEndRef = useRef(null);
  const hasStarted = messages.some((message) => message.role === "user");

  async function appendAssistantResponse(query) {
    try {
      const response = await fetch(API_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          input: {
            query,
          },
        }),
      });

      if (!response.ok) {
        throw new Error(`Request failed with ${response.status}`);
      }

      const payload = await response.json();
      const output = payload.output || {};
      const assistantMessageId = createMessageId();
      setMessages((current) => [
        ...current,
        {
          id: assistantMessageId,
          role: "assistant",
          content: "",
          fullContent: output.answer || "No answer returned.",
          isTyping: true,
          sources: output.sources || [],
          stakeholders: output.stakeholders || [],
          followUps: output.follow_up_questions || [],
        },
      ]);
    } catch (requestError) {
      setError(
        requestError instanceof Error
          ? requestError.message
          : "Unable to fetch account intelligence."
      );
      setMessages((current) => [
        ...current,
        {
          id: createMessageId(),
          role: "assistant",
          content: "",
          fullContent:
            "I couldn’t reach the account intelligence API. Check that the FastAPI backend is running on port 8000.",
          isTyping: true,
          sources: [],
        },
      ]);
    }
  }

  async function sendQuery(queryText = input) {
    const query = queryText.trim();
    if (!query || isLoading) return;
    const nextChatId = activeChatId || createMessageId();

    if (!activeChatId) {
      setActiveChatId(nextChatId);
      setChatSessions((current) => [
        {
          id: nextChatId,
          title: query,
          messages: EMPTY_MESSAGES,
          updatedAt: Date.now(),
        },
        ...current,
      ]);
    }

    setMessages((current) => [
      ...current.map((message) =>
        message.role === "assistant" && message.followUps?.length
          ? { ...message, followUps: [] }
          : message
      ),
      { id: createMessageId(), role: "user", content: query },
    ]);
    setInput("");
    setEditingMessageId(null);
    setEditDraft("");
    setError("");
    setIsLoading(true);

    try {
      await appendAssistantResponse(query);
    } finally {
      setIsLoading(false);
      inputRef.current?.focus();
    }
  }

  function handleSubmit(event) {
    event.preventDefault();
    sendQuery();
  }

  function startNewChat() {
    if (isLoading) return;
    setMessages(EMPTY_MESSAGES);
    setActiveChatId(null);
    setInput("");
    setEditingMessageId(null);
    setEditDraft("");
    setError("");
    inputRef.current?.focus();
  }

  function openChat(session) {
    if (isLoading) return;
    setActiveChatId(session.id);
    setMessages(session.messages);
    setInput("");
    setEditingMessageId(null);
    setEditDraft("");
    setError("");
  }

  function startEditingQuery(message) {
    if (isLoading) return;
    setEditingMessageId(message.id);
    setEditDraft(message.content);
  }

  function cancelEditingQuery() {
    if (isLoading) return;
    setEditingMessageId(null);
    setEditDraft("");
  }

  async function submitEditedQuery(messageId) {
    const query = editDraft.trim();
    if (!query || isLoading) return;
    const messageIndex = messages.findIndex((message) => message.id === messageId);

    if (messageIndex === -1) return;

    setMessages((current) =>
      current.slice(0, messageIndex + 1).map((message) => {
        if (message.id === messageId) {
          return { ...message, content: query };
        }

        if (message.role === "assistant" && message.followUps?.length) {
          return { ...message, followUps: [] };
        }

        return message;
      })
    );

    setEditingMessageId(null);
    setEditDraft("");
    setError("");
    setIsLoading(true);

    try {
      await appendAssistantResponse(query);
    } finally {
      setIsLoading(false);
      inputRef.current?.focus();
    }
  }

  useEffect(() => {
    const typingMessage = messages.find(
      (message) =>
        message.role === "assistant" &&
        message.isTyping &&
        message.fullContent &&
        message.content.length < message.fullContent.length
    );

    if (!typingMessage) {
      return undefined;
    }

    const timer = window.setTimeout(() => {
      setMessages((current) =>
        current.map((message) => {
          if (message.id !== typingMessage.id) {
            return message;
          }

          const nextContent = message.fullContent.slice(
            0,
            Math.min(message.content.length + TYPE_CHUNK_SIZE, message.fullContent.length)
          );

          return {
            ...message,
            content: nextContent,
            isTyping: nextContent.length < message.fullContent.length,
          };
        })
      );
    }, TYPE_SPEED_MS);

    return () => window.clearTimeout(timer);
  }, [messages]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [messages, isLoading]);

  useEffect(() => {
    if (!activeChatId || !hasStarted) {
      return;
    }

    setChatSessions((current) =>
      current.map((session) =>
        session.id === activeChatId
          ? {
              ...session,
              messages,
              updatedAt: Date.now(),
            }
          : session
      )
    );
  }, [activeChatId, hasStarted, messages]);

  return (
    <main className="page">
      <header className="topbar">
        <div className="brand">
          <img src="/assets/anarock-logo.png" alt="Anarock" />
          <div>
            <strong>Anarock ONE</strong>
            <span>Executive Account Intelligence</span>
          </div>
        </div>
        <div className="ap-card" aria-label="AP contact">
          <div className="ap-avatar">AP</div>
          <div>
            <strong>Anuj Puri</strong>
            <span>Chairman, ANAROCK</span>
          </div>
        </div>
      </header>

      <div className={`workspace ${isHistoryOpen ? "" : "history-collapsed"}`}>
        <aside className="history-panel" aria-label="Search history">
          <div className="history-header">
            <button className="new-chat-button" type="button" onClick={startNewChat} disabled={isLoading}>
              <MessageSquarePlus size={16} aria-hidden="true" />
              <span>New chat</span>
            </button>
            <button
              type="button"
              className="history-toggle"
              onClick={() => setIsHistoryOpen((value) => !value)}
              aria-label={isHistoryOpen ? "Collapse history" : "Expand history"}
            >
              {isHistoryOpen ? <PanelLeftClose size={17} /> : <PanelLeftOpen size={17} />}
            </button>
          </div>
          <div className="history-title">Recent</div>
          <div className="history-list">
            {chatSessions.length ? (
              chatSessions.map((session) => (
                <button
                  type="button"
                  className={session.id === activeChatId ? "active-history" : ""}
                  key={session.id}
                  onClick={() => openChat(session)}
                  title={session.title}
                >
                  <Search size={14} aria-hidden="true" />
                  <span>{session.title}</span>
                </button>
              ))
            ) : (
              <div className="empty-history">No searches yet</div>
            )}
          </div>
        </aside>

        <section className={`chat ${hasStarted ? "chat-active" : ""}`}>
          <div className={`intro ${hasStarted ? "compact-intro" : ""}`}>
            {!hasStarted ? <h1>Anarock ONE</h1> : null}
          </div>

          <div className={`messages ${hasStarted ? "active" : ""}`}>
            {messages.map((message) => (
              message.content || message.isTyping ? (
                <article className={`message ${message.role}`} key={message.id}>
                <div className="avatar" aria-hidden="true">
                  {message.role === "assistant" ? <Bot size={17} /> : <UserRound size={17} />}
                </div>
                <div className="message-body">
                  {message.role === "user" ? (
                    editingMessageId === message.id ? (
                      <form
                        className="inline-edit"
                        onSubmit={(event) => {
                          event.preventDefault();
                          submitEditedQuery(message.id);
                        }}
                      >
                        <textarea
                          value={editDraft}
                          onChange={(event) => setEditDraft(event.target.value)}
                          rows="2"
                          autoFocus
                          onKeyDown={(event) => {
                            if (event.key === "Enter" && !event.shiftKey) {
                              event.preventDefault();
                              submitEditedQuery(message.id);
                            }

                            if (event.key === "Escape") {
                              cancelEditingQuery();
                            }
                          }}
                        />
                        <div className="inline-edit-actions">
                          <button
                            type="button"
                            onClick={cancelEditingQuery}
                            aria-label="Cancel edit"
                            title="Cancel"
                          >
                            <X size={14} aria-hidden="true" />
                          </button>
                          <button
                            type="submit"
                            disabled={!editDraft.trim()}
                            aria-label="Save edited query"
                            title="Save"
                          >
                            <Check size={14} aria-hidden="true" />
                          </button>
                        </div>
                      </form>
                    ) : (
                      <button
                        type="button"
                        className="edit-query"
                        onClick={() => startEditingQuery(message)}
                        aria-label="Edit query"
                        title="Edit query"
                      >
                        <Pencil size={13} aria-hidden="true" />
                      </button>
                    )
                  ) : null}
                  {editingMessageId !== message.id ? (
                    <div className="formatted-message">
                      <FormattedMessageText text={message.content} />
                      {message.isTyping ? <span className="typing-cursor" /> : null}
                    </div>
                  ) : null}
                  {!message.isTyping && message.followUps?.length ? (
                    <FollowUps
                      questions={message.followUps}
                      isLoading={isLoading}
                      onSelect={(question) => sendQuery(question)}
                    />
                  ) : null}
                  {!message.isTyping && message.sources?.length ? (
                    <Sources sources={message.sources} />
                  ) : null}
                </div>
                </article>
              ) : null
            ))}

            {isLoading ? (
              <article className="message assistant">
                <div className="avatar" aria-hidden="true">
                  <Bot size={17} />
                </div>
                <div className="message-body">
                  <div className="thinking-state" aria-live="polite">
                    <span className="thinking-copy" />
                    <span />
                  </div>
                </div>
              </article>
            ) : null}
            <div className="scroll-anchor" ref={messagesEndRef} aria-hidden="true" />
          </div>

          {error ? (
            <div className="error" role="alert">
              <CircleAlert size={16} aria-hidden="true" />
              {error}
            </div>
          ) : null}
        </section>
      </div>

      <div className={`composer-dock ${hasStarted ? "composer-dock-active" : "composer-dock-home"}`}>
        <Composer hasStarted={hasStarted} input={input} setInput={setInput} isLoading={isLoading} inputRef={inputRef} handleSubmit={handleSubmit} />
      </div>
    </main>
  );
}

function Composer({
  hasStarted,
  input,
  setInput,
  isLoading,
  inputRef,
  handleSubmit,
}) {
  return (
    <form className={`composer ${hasStarted ? "composer-bottom" : "composer-center"}`} onSubmit={handleSubmit}>
      <textarea
        ref={inputRef}
        value={input}
        onChange={(event) => setInput(event.target.value)}
        placeholder={hasStarted ? "Ask anything" : "Hi Anuj, how can I help you?"}
        rows="1"
        onKeyDown={(event) => {
          if (event.key === "Enter" && !event.shiftKey) {
            event.preventDefault();
            handleSubmit(event);
          }
        }}
      />
      <button type="submit" disabled={!input.trim() || isLoading} aria-label="Send">
        {isLoading ? <Loader2 className="spin" size={18} /> : <ArrowUp size={18} />}
      </button>
    </form>
  );
}

function FollowUps({ questions, isLoading, onSelect }) {
  return (
    <div className="follow-ups">
      {questions.map((question) => (
        <button
          type="button"
          key={question}
          disabled={isLoading}
          onClick={() => onSelect(question)}
        >
          {question}
        </button>
      ))}
    </div>
  );
}

function Sources({ sources }) {
  const [open, setOpen] = useState(false);

  return (
    <div className="sources">
      <button type="button" onClick={() => setOpen((value) => !value)}>
        <MessageSquareText size={15} aria-hidden="true" />
        {sources.length} source records
        <ChevronDown className={open ? "rotate" : ""} size={15} aria-hidden="true" />
      </button>
      {open ? (
        <div className="source-list">
          {sources.map((source) => (
            <article
              className="source"
              key={`${source.stakeholder}-${source.date}-${source.colleague}`}
            >
              <span>
                <SourceIcon source={source.source} />
                {source.source} · {source.date}
              </span>
              <strong>{source.colleague}</strong>
              <p>{source.summary}</p>
            </article>
          ))}
        </div>
      ) : null}
    </div>
  );
}

createRoot(document.getElementById("root")).render(<App />);
