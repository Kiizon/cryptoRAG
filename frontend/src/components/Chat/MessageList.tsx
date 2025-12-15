import React, { useRef, useEffect } from 'react';
import { MessageBubble } from './MessageBubble';
import { Bot } from 'lucide-react';

interface Message {
    role: 'user' | 'assistant';
    content: string;
}

interface MessageListProps {
    messages: Message[];
    isLoading: boolean;
}

export function MessageList({ messages, isLoading }: MessageListProps) {
    const bottomRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages, isLoading]);

    return (
        <div className="flex-1 overflow-y-auto px-4 py-6 md:px-8 space-y-6 scroll-smooth custom-scrollbar">
            {messages.length === 0 ? (
                <div className="flex flex-col items-center justify-center h-full text-center p-8 opacity-0 animate-in fade-in zoom-in duration-700 slide-in-from-bottom-5">
                    <div className="relative mb-8 group cursor-default">
                        <div className="absolute inset-0 bg-indigo-500/20 blur-3xl rounded-full group-hover:bg-indigo-500/30 transition-all duration-700" />
                        <div className="relative w-24 h-24 bg-neutral-900 rounded-3xl border border-white/10 flex items-center justify-center shadow-2xl ring-1 ring-white/5 rotate-3 transition-transform duration-500 group-hover:rotate-6 group-hover:scale-105">
                            <Bot className="w-10 h-10 text-indigo-400" />
                        </div>
                    </div>

                    <h2 className="text-3xl font-bold bg-gradient-to-br from-white via-neutral-200 to-neutral-500 bg-clip-text text-transparent mb-4 tracking-tight">
                        Encrypted Knowledge Base
                    </h2>
                    <p className="max-w-md text-neutral-500 leading-relaxed text-sm">
                        Ask me anything about cryptography, AES, RSA, or secure protocols.
                        I extract insights directly from verified technical documentation.
                    </p>
                </div>
            ) : (
                <div className="max-w-4xl mx-auto space-y-6">
                    {messages.map((msg, idx) => (
                        <MessageBubble key={idx} role={msg.role} content={msg.content} />
                    ))}

                    {/* Loading Indicator */}
                    {isLoading && messages[messages.length - 1]?.role === 'user' && (
                        <div className="flex gap-4 mr-auto max-w-4xl w-full animate-pulse">
                            <div className="w-8 h-8 rounded-full bg-neutral-800 flex items-center justify-center flex-shrink-0 ring-1 ring-white/10">
                                <Bot className="w-4 h-4 text-indigo-400" />
                            </div>
                            <div className="px-6 py-4 rounded-3xl rounded-tl-sm bg-neutral-800/50 border border-white/5 flex items-center gap-2">
                                <span className="w-1.5 h-1.5 bg-indigo-400 rounded-full animate-bounce [animation-delay:-0.3s]"></span>
                                <span className="w-1.5 h-1.5 bg-indigo-400 rounded-full animate-bounce [animation-delay:-0.15s]"></span>
                                <span className="w-1.5 h-1.5 bg-indigo-400 rounded-full animate-bounce"></span>
                            </div>
                        </div>
                    )}
                </div>
            )}
            <div ref={bottomRef} className="h-4" />
        </div>
    );
}
