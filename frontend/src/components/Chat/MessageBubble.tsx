import React from 'react';
import { User, Bot, Copy, Check } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import { motion } from 'framer-motion';
import { cn } from '../../lib/utils';

interface MessageBubbleProps {
    role: 'user' | 'assistant';
    content: string;
}

export function MessageBubble({ role, content }: MessageBubbleProps) {
    const isUser = role === 'user';
    const [copied, setCopied] = React.useState(false);

    const handleCopy = () => {
        navigator.clipboard.writeText(content);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    };

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            layout
            className={cn(
                "flex gap-4 max-w-4xl w-full",
                isUser ? "ml-auto flex-row-reverse" : "mr-auto"
            )}
        >
            {/* Avatar */}
            <div className={cn(
                "w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 shadow-lg ring-1",
                isUser
                    ? "bg-gradient-to-br from-indigo-500 to-purple-600 ring-indigo-400/30"
                    : "bg-neutral-800 ring-white/10"
            )}>
                {isUser ? <User className="w-4 h-4 text-white" /> : <Bot className="w-4 h-4 text-indigo-400" />}
            </div>

            {/* Message Content */}
            <div className={cn(
                "group relative px-6 py-4 rounded-3xl text-sm leading-relaxed shadow-sm max-w-[85%] md:max-w-[75%]",
                isUser
                    ? "bg-indigo-600 text-white rounded-tr-sm"
                    : "bg-neutral-800/80 backdrop-blur-md text-neutral-200 rounded-tl-sm border border-white/5"
            )}>
                {isUser ? (
                    <p className="whitespace-pre-wrap font-medium">{content}</p>
                ) : (
                    <div className="prose prose-invert prose-sm max-w-none prose-p:leading-relaxed prose-pre:bg-black/30 prose-pre:border prose-pre:border-white/10 prose-pre:rounded-xl">
                        <ReactMarkdown>{content}</ReactMarkdown>
                    </div>
                )}

                {/* Copy Button (Only for assistant) */}
                {!isUser && (
                    <button
                        onClick={handleCopy}
                        className="absolute top-2 right-2 p-1.5 bg-black/20 hover:bg-black/40 rounded-lg opacity-0 group-hover:opacity-100 transition-all text-neutral-400 hover:text-white"
                        title="Copy response"
                    >
                        {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                    </button>
                )}
            </div>
        </motion.div>
    );
}
