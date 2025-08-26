import React, { useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Menu, Settings } from 'lucide-react';
import Sidebar from './Sidebar';
import ChatPanel from './ChatPanel';
import SettingsSheet from './SettingsSheet';
import ParticlesBackground from './ParticlesBackground';
import GridIsometricCanvas from './GridIsometricCanvas';
import useJarvisStore from '../lib/store';
import { Button } from './ui/button';

const ChatLayout = () => {
  const {
    sidebarOpen,
    setSidebarOpen,
    showSettings,
    toggleSettings,
    settings,
    currentThreadId,
    createNewThread
  } = useJarvisStore();

  // Create initial thread if none exists
  useEffect(() => {
    if (!currentThreadId) {
      createNewThread();
    }
  }, [currentThreadId, createNewThread]);

  const { performanceMode, reducedMotion } = settings;

  return (
    <div className="relative h-screen bg-jarvis-bg overflow-hidden">
      {/* Background Effects */}
      {!performanceMode && !reducedMotion && (
        <>
          <ParticlesBackground />
          <GridIsometricCanvas />
        </>
      )}
      
      {/* Scanlines overlay */}
      <div className="scanlines absolute inset-0 pointer-events-none z-10" />
      
      {/* Main Layout */}
      <div className="relative z-20 h-full flex">
        {/* Sidebar */}
        <AnimatePresence mode="wait">
          {sidebarOpen && (
            <motion.div
              initial={{ x: -320, opacity: 0 }}
              animate={{ x: 0, opacity: 1 }}
              exit={{ x: -320, opacity: 0 }}
              transition={{ duration: 0.3, ease: "easeOut" }}
              className="w-80 h-full flex-shrink-0 relative z-30"
            >
              <Sidebar />
            </motion.div>
          )}
        </AnimatePresence>

        {/* Main Chat Area */}
        <div className="flex-1 flex flex-col relative">
          {/* Top Bar */}
          <motion.div 
            className="glass-surface h-16 flex items-center justify-between px-4 border-b border-jarvis-border"
            initial={{ y: -64, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ duration: 0.5, delay: 0.2 }}
          >
            <div className="flex items-center gap-4">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setSidebarOpen(!sidebarOpen)}
                className="text-jarvis-primary hover:bg-jarvis-surface/50 hover:text-jarvis-info"
              >
                <Menu className="h-5 w-5" />
              </Button>
              
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 bg-jarvis-success rounded-full animate-pulse-slow" />
                <span className="text-jarvis-text font-medium">Jarvis AI</span>
                <span className="text-jarvis-text-muted text-sm">• Système opérationnel</span>
              </div>
            </div>

            <Button
              variant="ghost"
              size="sm"
              onClick={toggleSettings}
              className="text-jarvis-primary hover:bg-jarvis-surface/50 hover:text-jarvis-info"
            >
              <Settings className="h-5 w-5" />
            </Button>
          </motion.div>

          {/* Chat Panel */}
          <div className="flex-1 relative">
            <ChatPanel />
          </div>
        </div>
      </div>

      {/* Settings Sheet */}
      <SettingsSheet />

      {/* Mobile Overlay */}
      {sidebarOpen && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          onClick={() => setSidebarOpen(false)}
          className="lg:hidden fixed inset-0 bg-black/50 backdrop-blur-sm z-25"
        />
      )}
    </div>
  );
};

export default ChatLayout;