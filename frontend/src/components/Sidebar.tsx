import React from 'react';
import { Key, ShieldCheck, Terminal, X, Menu } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { cn } from '../lib/utils';

interface SidebarProps {
    apiKey: string;
    setApiKey: (key: string) => void;
    isOpen: boolean;
    onClose: () => void;
    className?: string;
}

export function Sidebar({ apiKey, setApiKey, isOpen, onClose, className }: SidebarProps) {
    return (
        <AnimatePresence mode="wait">
            {isOpen && (
                <>
                    {/* Mobile Overlay */}
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        onClick={onClose}
                        className="fixed inset-0 bg-black/60 backdrop-blur-sm z-40 md:hidden"
                    />

                    {/* Sidebar Content */}
                    <motion.aside
                        initial={{ x: -300, opacity: 0 }}
                        animate={{ x: 0, opacity: 1 }}
                        exit={{ x: -300, opacity: 0 }}
                        transition={{ type: "spring", damping: 25, stiffness: 200 }}
                        className={cn(
                            "fixed md:relative z-50 w-80 h-full border-r border-white/10 bg-neutral-900/80 backdrop-blur-xl flex flex-col shadow-2xl",
                            className
                        )}
                    >
                        <div className="p-6 flex flex-col h-full relative overflow-hidden">
                            {/* Decorative Background Elements */}
                            <div className="absolute top-0 left-0 w-full h-full overflow-hidden pointer-events-none z-[-1]">
                                <div className="absolute top-[-10%] left-[-10%] w-[50%] h-[30%] bg-indigo-500/10 rounded-full blur-[80px]" />
                                <div className="absolute bottom-[-10%] right-[-10%] w-[50%] h-[30%] bg-purple-500/10 rounded-full blur-[80px]" />
                            </div>

                            {/* Header */}
                            <div className="flex items-center gap-4 mb-10">
                                <div className="p-2.5 bg-gradient-to-br from-indigo-600 to-purple-600 rounded-xl shadow-lg shadow-indigo-500/20 ring-1 ring-white/20">
                                    <ShieldCheck className="w-6 h-6 text-white" />
                                </div>
                                <div>
                                    <h1 className="text-xl font-bold bg-gradient-to-r from-white to-neutral-400 bg-clip-text text-transparent">
                                        CryptoRAG
                                    </h1>
                                    <p className="text-xs text-neutral-500 font-medium tracking-wide uppercase">Secure Intelligence</p>
                                </div>
                                <button
                                    onClick={onClose}
                                    className="md:hidden ml-auto p-2 hover:bg-white/5 rounded-lg text-neutral-400 transition-colors"
                                >
                                    <X className="w-5 h-5" />
                                </button>
                            </div>

                            <div className="flex-1 space-y-8">
                                {/* Configuration Section */}
                                <div className="space-y-4">
                                    <h3 className="text-xs font-semibold text-neutral-500 uppercase tracking-wider flex items-center gap-2 px-1">
                                        <Key className="w-3.5 h-3.5" /> Authentication
                                    </h3>
                                    <div className="group relative">
                                        <div className="absolute -inset-0.5 bg-gradient-to-r from-indigo-500 to-purple-500 rounded-xl opacity-20 group-hover:opacity-40 transition duration-500 blur"></div>
                                        <div className="relative bg-neutral-900 rounded-xl p-1">
                                            <input
                                                type="password"
                                                value={apiKey}
                                                onChange={(e) => setApiKey(e.target.value)}
                                                placeholder="Cohere API Key"
                                                className="w-full bg-neutral-800/50 border border-white/5 rounded-lg px-4 py-3 text-sm text-neutral-200 focus:outline-none focus:ring-1 focus:ring-indigo-500/50 placeholder:text-neutral-600 transition-all font-mono"
                                            />
                                        </div>
                                    </div>
                                    <p className="text-[10px] text-neutral-500 px-1">
                                        Your API key is stored locally and never shared.
                                    </p>
                                </div>

                                {/* System Info */}
                                <div className="space-y-4">
                                    <h3 className="text-xs font-semibold text-neutral-500 uppercase tracking-wider flex items-center gap-2 px-1">
                                        <Terminal className="w-3.5 h-3.5" /> System Status
                                    </h3>
                                    <div className="p-4 rounded-xl border border-white/5 bg-white/5 hover:bg-white/10 transition-colors">
                                        <div className="flex items-center gap-2 mb-2">
                                            <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
                                            <span className="text-xs font-medium text-emerald-400">System Operational</span>
                                        </div>
                                        <p className="text-xs text-neutral-400 leading-relaxed">
                                            Powered by <strong>Command R+</strong> & <strong>Rerank v3.5</strong>.
                                            Indexing 3 sources.
                                        </p>
                                    </div>
                                </div>
                            </div>

                            {/* Footer */}
                            <div className="pt-6 border-t border-white/5">
                                <div className="flex items-center gap-3 group cursor-pointer hover:bg-white/5 p-2 rounded-xl transition-colors">
                                    <div className="w-9 h-9 rounded-full bg-gradient-to-tr from-indigo-500 to-purple-500 flex items-center justify-center ring-2 ring-neutral-900 group-hover:ring-indigo-500/50 transition-all">
                                        <span className="text-xs font-bold text-white">KD</span>
                                    </div>
                                    <div className="flex-1">
                                        <p className="text-sm font-medium text-neutral-200 group-hover:text-white transition-colors">Kish Dizon</p>
                                        <p className="text-xs text-neutral-500 group-hover:text-neutral-400 transition-colors">Administrator</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </motion.aside>
                </>
            )}
        </AnimatePresence>
    );
}
