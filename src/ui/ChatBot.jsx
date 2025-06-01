import React, { useState, useRef, useEffect } from 'react';

function ChatBot() {
  const [query, setQuery] = useState('');
  const [messages, setMessages] = useState([]); // {type: 'user'|'bot', text: string}
  const [loading, setLoading] = useState(false);
  const [tools, setTools] = useState(null);
  const [toolsLoading, setToolsLoading] = useState(false);
  const chatEndRef = useRef(null);

  useEffect(() => {
    // Scroll to bottom on new message
    if (chatEndRef.current) {
      chatEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;
    setMessages((msgs) => [...msgs, { type: 'user', text: query }]);
    setLoading(true);
    try {
      const res = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
        body: JSON.stringify({ query }),
      });
      const data = await res.json();
      setMessages((msgs) => [
        ...msgs,
        { type: 'bot', text: data && data.response ? data.response : JSON.stringify(data, null, 2) },
      ]);
    } catch (err) {
      setMessages((msgs) => [
        ...msgs,
        { type: 'bot', text: 'Error: ' + err.message },
      ]);
    }
    setQuery('');
    setLoading(false);
  };

  const handleGetTools = async () => {
    setToolsLoading(true);
    setTools(null);
    try {
      const res = await fetch('http://localhost:8000/tools');
      const data = await res.json();
      setTools(data);
    } catch (err) {
      setTools({ error: err.message });
    }
    setToolsLoading(false);
  };

  return (
    <div style={{ maxWidth: 600, margin: '2rem auto', fontFamily: 'sans-serif', display: 'flex', flexDirection: 'column', height: '80vh', border: '1px solid #ddd', borderRadius: 8, background: '#fff' }}>
      <h2 style={{ textAlign: 'center', margin: '1rem 0 0.5rem 0' }}>Northwind Business Chat Bot</h2>
      <div style={{ display: 'flex', justifyContent: 'center', marginBottom: 8 }}>
        <button onClick={handleGetTools} style={{ padding: '0.5rem 1rem', borderRadius: 8, border: '1px solid #1976d2', background: '#e3f2fd', color: '#1976d2', fontWeight: 600, fontSize: 15, cursor: 'pointer' }} disabled={toolsLoading}>
          {toolsLoading ? 'Loading tools...' : 'Show Available Tools'}
        </button>
      </div>
      {tools && typeof tools === 'object' && Object.keys(tools).length > 0 && (
        <div style={{ background: '#f9fbe7', border: '1px solid #cddc39', borderRadius: 8, padding: '1rem', margin: '0 1rem 1rem 1rem', fontSize: 15 }}>
          <strong>Available Tools:</strong>
          {/* Debug output removed for clean UI */}
          <ul style={{ margin: '0.5rem 0 0 0.5rem', padding: 0 }}>
            {Object.keys(tools).map((key) => (
              <li key={key} style={{ marginBottom: 4, wordBreak: 'break-word' }}>
                <span style={{ fontWeight: 600 }}>{key}</span>:&nbsp;
                <span>{
                  tools[key] === null || tools[key] === undefined
                    ? String(tools[key])
                    : typeof tools[key] === 'object'
                      ? JSON.stringify(tools[key])
                      : String(tools[key])
                }</span>
              </li>
            ))}
          </ul>
        </div>
      )}
      <div style={{ flex: 1, overflowY: 'auto', padding: '1rem', display: 'flex', flexDirection: 'column', gap: 12, borderTop: '1px solid #eee', borderBottom: '1px solid #eee', background: '#fafbfc' }}>
        {messages.map((msg, idx) => (
          <React.Fragment key={idx}>
            <div style={{
              alignSelf: msg.type === 'user' ? 'flex-end' : 'flex-start',
              background: msg.type === 'user' ? '#e0f7fa' : '#f4f4f4',
              color: '#222',
              padding: '0.7rem 1rem',
              borderRadius: 16,
              maxWidth: '80%',
              boxShadow: '0 1px 2px #eee',
              marginBottom: 2
            }}>
              {msg.text}
            </div>
            {/* Separator */}
            {idx < messages.length - 1 && (
              <div style={{ textAlign: 'center', color: '#bbb', fontSize: 12, margin: '0.5rem 0' }}>────────────</div>
            )}
          </React.Fragment>
        ))}
        <div ref={chatEndRef} />
      </div>
      <form onSubmit={handleSubmit} style={{ display: 'flex', padding: '1rem', borderTop: '1px solid #eee', background: '#fff' }}>
        <input
          type="text"
          value={query}
          onChange={e => setQuery(e.target.value)}
          placeholder="Type your message..."
          style={{ flex: 1, padding: '0.7rem', borderRadius: 16, border: '1px solid #ccc', fontSize: 16 }}
          disabled={loading}
        />
        <button type="submit" style={{ padding: '0.7rem 1.5rem', marginLeft: 8, borderRadius: 16, border: 'none', background: '#1976d2', color: '#fff', fontWeight: 600, fontSize: 16 }} disabled={loading}>
          {loading ? '...' : 'Send'}
        </button>
      </form>
    </div>
  );
}

export default ChatBot;
