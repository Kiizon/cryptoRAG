import React, { useState, useRef, useEffect } from 'react';
import { Send, Sparkles } from 'lucide-react';
import { motion } from 'framer-motion';
import { cn } from '../../lib/utils';

interface ChatInputProps {
    onSend: (message: string) => void;
    isLoading: boolean;
    disabled: boolean;
    placeholder?: string;
}

export function ChatInput({ onSend, isLoading, disabled, placeholder }: ChatInputProps) {
    const [input, setInput] = useState('');
    const textareaRef = useRef<HTMLTextAreaElement>(null);

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (!input.trim() || disabled || isLoading) return;
        onSend(input);
        setInput('');
        if (textareaRef.current) {
            textareaRef.current.style.height = 'auto';
        }
    };

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSubmit(e);
        }
    };

    // Auto-resize textarea
    useEffect(() => {
        if (textareaRef.current) {
            textareaRef.current.style.height = 'auto';
            textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 200)}px`;
        }
    }, [input]);

    return (
        <div className="relative max-w-4xl mx-auto w-full">
            <form onSubmit={handleSubmit} className="relative group">
                {/* Glowing border effect */}
                <div className="absolute -inset-0.5 bg-gradient-to-r from-indigo-500 via-purple-500 to-indigo-500 rounded-2xl opacity-20 group-hover:opacity-60 transition duration-500 blur group-focus-within:opacity-100 animate-gradient-xy"></div>

                <div className="relative flex items-end bg-neutral-900 rounded-2xl border border-white/10 shadow-2xl overflow-hidden">
                    <textarea
                        ref={textareaRef}
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyDown={handleKeyDown}
                        placeholder={placeholder}
                        disabled={disabled}
                        rows={1}
                        className="w-full bg-transparent border-0 px-5 py-4 text-base text-neutral-200 placeholder:text-neutral-600 focus:ring-0 resize-none max-h-[200px] disabled:cursor-not-allowed"
                        style={{ minHeight: '60px' }}
                    />

                    <div className="p-2 pb-3 pr-3">
                        <button
                            type="submit"
                            disabled={disabled || !input.trim() || isLoading}
                            className={cn(
                                "p-2.5 rounded-xl transition-all duration-200 flex items-center justify-center shadow-lg",
                                input.trim() && !disabled && !isLoading
                                    ? "bg-indigo-600 hover:bg-indigo-500 text-white translate-y-0"
                                    : "bg-neutral-800 text-neutral-600 cursor-not-allowed"
                            )}
                        >
                            {isLoading ? (
                                <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                            ) : (
                                <Send className="w-5 h-5" />
                            )}
                        </button>
                    </div>
                </div>
            </form>
            <div className="flex justify-center mt-3 items-center gap-2">
                <Sparkles className="w-3 h-3 text-indigo-400" />
                <p className="text-[10px] text-neutral-500 uppercase tracking-widest font-semibold">
                    Powered by RAG & Cohere
                </p>
            </div>
        </div>
    );
}
