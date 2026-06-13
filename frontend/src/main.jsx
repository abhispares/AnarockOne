import React, { useEffect, useRef, useState } from "react";
import { createRoot } from "react-dom/client";
import {
  ArrowUp,
  Bot,
  ChevronDown,
  CircleAlert,
  Loader2,
  Mail,
  MessageSquareText,
  UserRound,
  UsersRound,
  BriefcaseBusiness,
} from "lucide-react";
import "./styles.css";

const API_URL =
  import.meta.env.VITE_RELATIONSHIP_API_URL ||
  "/relationship-intelligence/invoke";

const stakeholders = [
  "Abhishek",
  "Nidhi",
  "Jiwesh",
  "Radhika",
  "Manav",
  "Sneha",
  "Arjun",
  "Kavya",
  "Rahul",
  "Pooja",
  "Dev",
  "Meera",
  "Samar",
  "Tanya",
  "Vikrant",
];

function stakeholderPrompt(name) {
  return `Who has recently interacted with ${name} and what should I know before outreach?`;
}

const sourceIcons = {
  "Microsoft Teams meeting": UsersRound,
  "Outlook email": Mail,
  "BD Tracker update": BriefcaseBusiness,
};

const TYPE_SPEED_MS = 12;
const TYPE_CHUNK_SIZE = 3;

function SourceIcon({ source }) {
  const Icon = sourceIcons[source] || MessageSquareText;
  return <Icon size={14} aria-hidden="true" />;
}

function App() {
  const [messages, setMessages] = useState([
    {
      id: "welcome",
      role: "assistant",
      content: "",
      sources: [],
    },
  ]);
  const [input, setInput] = useState("");
  const [stakeholder, setStakeholder] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const inputRef = useRef(null);
  const messagesEndRef = useRef(null);
  const hasStarted = messages.some((message) => message.role === "user");

  async function sendQuery(queryText = input, stakeholderName = stakeholder) {
    const query = queryText.trim();
    if (!query || isLoading) return;

    setMessages((current) => [
      ...current,
      { id: crypto.randomUUID(), role: "user", content: query },
    ]);
    setInput("");
    setError("");
    setIsLoading(true);

    try {
      const response = await fetch(API_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          input: {
            query,
            stakeholder_name: stakeholderName || undefined,
          },
        }),
      });

      if (!response.ok) {
        throw new Error(`Request failed with ${response.status}`);
      }

      const payload = await response.json();
      const output = payload.output || {};
      const assistantMessageId = crypto.randomUUID();
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
        },
      ]);
    } catch (requestError) {
      setError(
        requestError instanceof Error
          ? requestError.message
          : "Unable to fetch relationship intelligence."
      );
      setMessages((current) => [
        ...current,
        {
          id: crypto.randomUUID(),
          role: "assistant",
          content: "",
          fullContent:
            "I couldn’t reach the relationship intelligence API. Check that the FastAPI backend is running on port 8000.",
          isTyping: true,
          sources: [],
        },
      ]);
    } finally {
      setIsLoading(false);
      inputRef.current?.focus();
    }
  }

  function handleSubmit(event) {
    event.preventDefault();
    sendQuery();
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

  return (
    <main className="page">
      <header className="topbar">
        <div className="brand">
          <img src="/assets/anarock-logo.png" alt="Anarock" />
          <div>
            <strong>AnarockOne</strong>
            <span>Relationship Intelligence</span>
          </div>
        </div>
        <div className="status">POC data</div>
      </header>

      <section className="chat">
        <div className={`intro ${hasStarted ? "compact-intro" : ""}`}>
          {!hasStarted ? <h1>AnarockOne</h1> : null}
        </div>

        {!hasStarted ? <Composer hasStarted={hasStarted} input={input} setInput={setInput} stakeholder={stakeholder} setStakeholder={setStakeholder} isLoading={isLoading} inputRef={inputRef} handleSubmit={handleSubmit} /> : null}

        <div className={`messages ${hasStarted ? "active" : ""}`}>
          {messages.map((message) => (
            message.content || message.isTyping ? (
              <article className={`message ${message.role}`} key={message.id}>
              <div className="avatar" aria-hidden="true">
                {message.role === "assistant" ? <Bot size={17} /> : <UserRound size={17} />}
              </div>
              <div className="message-body">
                <p>
                  {message.content}
                  {message.isTyping ? <span className="typing-cursor" /> : null}
                </p>
                {!message.isTyping && message.stakeholders?.length ? (
                  <div className="stakeholder-tags">
                    {message.stakeholders.map((name) => (
                      <span key={name}>{name}</span>
                    ))}
                  </div>
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
                <Loader2 className="spin" size={17} />
              </div>
              <div className="message-body">
                <p>Reading relationship history...</p>
              </div>
            </article>
          ) : null}
          <div ref={messagesEndRef} />
        </div>

        {error ? (
          <div className="error" role="alert">
            <CircleAlert size={16} aria-hidden="true" />
            {error}
          </div>
        ) : null}
      </section>

      {hasStarted ? <Composer hasStarted={hasStarted} input={input} setInput={setInput} stakeholder={stakeholder} setStakeholder={setStakeholder} isLoading={isLoading} inputRef={inputRef} handleSubmit={handleSubmit} /> : null}
    </main>
  );
}

function Composer({
  hasStarted,
  input,
  setInput,
  stakeholder,
  setStakeholder,
  isLoading,
  inputRef,
  handleSubmit,
}) {
  return (
    <form className={`composer ${hasStarted ? "composer-bottom" : "composer-center"}`} onSubmit={handleSubmit}>
      <div className="stakeholder-search">
        <input
          aria-label="Stakeholder filter"
          list="stakeholder-options"
          value={stakeholder}
          onChange={(event) => {
            const nextStakeholder = event.target.value;
            setStakeholder(nextStakeholder);
            if (!input.trim() && stakeholders.includes(nextStakeholder)) {
              setInput(stakeholderPrompt(nextStakeholder));
            }
          }}
          placeholder="Stakeholder"
        />
        <datalist id="stakeholder-options">
          {stakeholders.map((name) => (
            <option key={name} value={name} />
          ))}
        </datalist>
      </div>
      <textarea
        ref={inputRef}
        value={input}
        onChange={(event) => setInput(event.target.value)}
        placeholder="Ask about warm intros, commitments, concerns, or missed opportunities..."
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
