"use client";

import React, { useState } from 'react';
import { Menu } from 'lucide-react';
import { Sidebar } from '../components/Sidebar';
import { ChatInput } from '../components/Chat/ChatInput';
import { MessageList } from '../components/Chat/MessageList';

type Message = {
  role: 'user' | 'assistant';
  content: string;
};

export default function Home() {
  const [apiKey, setApiKey] = useState('');
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);

  const handleSubmit = async (userMessage: string) => {
    if (!apiKey) {
      alert("Please enter your Cohere API Key first.");
      setIsSidebarOpen(true);
      return;
    }

    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    setIsLoading(true);

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: userMessage, api_key: apiKey }),
      });

      if (!response.ok) {
        throw new Error('Failed to fetch response');
      }

      const reader = response.body?.getReader();
      if (!reader) throw new Error('No reader available');

      // Create a placeholder for the assistant response
      setMessages(prev => [...prev, { role: 'assistant', content: '' }]);

      let accumulatedResponse = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = new TextDecoder().decode(value);
        accumulatedResponse += chunk;

        setMessages(prev => {
          const newMessages = [...prev];
          const lastMsg = newMessages[newMessages.length - 1];
          if (lastMsg.role === 'assistant') {
            lastMsg.content = accumulatedResponse;
          }
          return newMessages;
        });
      }

    } catch (error) {
      console.error(error);
      setMessages(prev => [...prev, { role: 'assistant', content: "Error: Failed to connect to the RAG server. Make sure the API key is correct and the backend is running." }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex h-screen bg-black text-white font-sans overflow-hidden selection:bg-indigo-500/30 selection:text-indigo-200">

      {/* Dynamic Background */}
      <div className="fixed inset-0 z-0 pointer-events-none">
        <div className="absolute top-[-20%] right-[-10%] w-[60%] h-[60%] bg-indigo-900/20 rounded-full blur-[120px] mix-blend-screen animate-pulse" style={{ animationDuration: '4s' }} />
        <div className="absolute bottom-[-20%] left-[-10%] w-[60%] h-[60%] bg-purple-900/20 rounded-full blur-[120px] mix-blend-screen animate-pulse" style={{ animationDuration: '7s' }} />
      </div>

      <Sidebar
        apiKey={apiKey}
        setApiKey={setApiKey}
        isOpen={isSidebarOpen}
        onClose={() => setIsSidebarOpen(false)}
      />

      <main className="flex-1 flex flex-col h-full relative z-10">
        {/* Mobile Header */}
        {!isSidebarOpen && (
          <header className="absolute top-4 left-4 z-20 md:hidden">
            <button
              onClick={() => setIsSidebarOpen(true)}
              className="p-2 bg-neutral-900/80 backdrop-blur-md rounded-lg border border-white/10 shadow-lg"
            >
              <Menu className="w-5 h-5 text-neutral-400" />
            </button>
          </header>
        )}

        {/* Chat Area */}
        <div className="flex-1 flex flex-col max-w-5xl w-full mx-auto h-full">
          <MessageList messages={messages} isLoading={isLoading} />

          <div className="p-4 md:p-6 pb-6 md:pb-8">
            <ChatInput
              onSend={handleSubmit}
              isLoading={isLoading}
              disabled={!apiKey}
              placeholder={apiKey ? "Ask about AES, RSA, or hashing..." : "Enter API Key in sidebar to start..."}
            />
          </div>
        </div>
      </main>
    </div>
  );
}
