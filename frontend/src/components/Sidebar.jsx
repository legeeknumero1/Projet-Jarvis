import React, { useState, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Plus, 
  Search, 
  MessageSquare, 
  Trash2, 
  Edit3,
  Download,
  Upload,
  RotateCcw,
  Zap
} from 'lucide-react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { ScrollArea } from './ui/scroll-area';
import { 
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from './ui/alert-dialog';
import useJarvisStore from '../lib/store';
import { useToast } from '../hooks/use-toast';

const Sidebar = () => {
  const {
    threads,
    currentThreadId,
    createNewThread,
    setCurrentThread,
    deleteThread,
    updateThreadTitle,
    exportData,
    importData,
    clearAllData
  } = useJarvisStore();

  const { toast } = useToast();
  const [searchQuery, setSearchQuery] = useState('');
  const [editingThread, setEditingThread] = useState(null);
  const [editTitle, setEditTitle] = useState('');

  // Filter threads based on search
  const filteredThreads = useMemo(() => {
    if (!searchQuery.trim()) return threads;
    return threads.filter(thread => 
      thread.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      thread.messages?.some(msg => 
        msg.content.toLowerCase().includes(searchQuery.toLowerCase())
      )
    );
  }, [threads, searchQuery]);

  const handleNewChat = () => {
    createNewThread();
    toast({
      title: "✨ Nouvelle conversation",
      description: "Interface Jarvis initialisée avec succès.",
    });
  };

  const handleDeleteThread = (threadId, threadTitle) => {
    deleteThread(threadId);
    toast({
      title: "🗑️ Conversation supprimée",
      description: `"${threadTitle}" a été effacée des archives.`,
    });
  };

  const handleEditTitle = (thread) => {
    setEditingThread(thread.id);
    setEditTitle(thread.title);
  };

  const handleSaveTitle = () => {
    if (editTitle.trim() && editingThread) {
      updateThreadTitle(editingThread, editTitle.trim());
      setEditingThread(null);
      setEditTitle('');
      toast({
        title: "📝 Titre mis à jour",
        description: "Référence conversation modifiée avec succès.",
      });
    }
  };

  const handleExport = () => {
    const data = exportData();
    const blob = new Blob([JSON.stringify(data, null, 2)], {
      type: 'application/json',
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `jarvis-export-${new Date().toISOString().split('T')[0]}.json`;
    a.click();
    URL.revokeObjectURL(url);
    
    toast({
      title: "💾 Export réussi",
      description: "Archives Jarvis sauvegardées avec succès.",
    });
  };

  const handleImport = (event) => {
    const file = event.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const data = JSON.parse(e.target.result);
        importData(data);
        toast({
          title: "📥 Import réussi",
          description: "Archives Jarvis restaurées avec succès.",
        });
      } catch (error) {
        toast({
          title: "❌ Erreur d'import",
          description: "Fichier de données non compatible.",
          variant: "destructive",
        });
      }
    };
    reader.readAsText(file);
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffTime = Math.abs(now - date);
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

    if (diffDays === 1) return 'Aujourd\'hui';
    if (diffDays === 2) return 'Hier';
    if (diffDays <= 7) return `Il y a ${diffDays - 1}j`;
    return date.toLocaleDateString('fr-FR', { 
      day: 'numeric', 
      month: 'short' 
    });
  };

  return (
    <motion.div 
      className="h-full glass-cyber border-r-2 border-jarvis-neon-cyan/30 flex flex-col relative overflow-hidden cyber-scanline"
      initial={{ opacity: 0, x: -50 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.5, ease: "easeOut" }}
    >
      {/* Cyber gradient overlay */}
      <div className="absolute inset-0 bg-gradient-to-b from-jarvis-neon-cyan/5 via-transparent to-jarvis-neon-purple/5 pointer-events-none" />
      
      {/* Header */}
      <div className="relative z-10 p-6 border-b-2 border-jarvis-neon-cyan/20">
        <motion.div 
          className="flex items-center justify-between mb-6"
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-gradient-to-br from-jarvis-neon-cyan to-jarvis-neon-purple rounded-lg flex items-center justify-center shadow-neon-cyan">
              <Zap className="h-5 w-5 text-jarvis-text-primary" />
            </div>
            <h2 className="text-xl font-bold text-jarvis-neon-cyan cyber-pulse">
              Conversations
            </h2>
          </div>
          <Button
            onClick={handleNewChat}
            className="cyber-button-primary h-10 w-10 p-0 rounded-xl"
          >
            <Plus className="h-5 w-5" />
          </Button>
        </motion.div>

        {/* Search */}
        <motion.div 
          className="relative"
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.3 }}
        >
          <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 h-4 w-4 text-jarvis-neon-cyan z-10" />
          <Input
            placeholder="Rechercher conversations..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="cyber-input pl-12 bg-jarvis-bg-surface/60 border-jarvis-neon-cyan/30 text-jarvis-text-primary placeholder:text-jarvis-text-muted focus:border-jarvis-neon-cyan focus:shadow-neon-cyan"
          />
        </motion.div>
      </div>

      {/* Threads List */}
      <ScrollArea className="flex-1 px-4 relative z-10">
        <div className="space-y-2 py-4">
          <AnimatePresence mode="popLayout">
            {filteredThreads.map((thread, index) => (
              <motion.div
                key={thread.id}
                initial={{ opacity: 0, x: -30 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -30 }}
                transition={{ duration: 0.3, delay: index * 0.05 }}
                className={`group relative rounded-xl p-4 cursor-pointer transition-all duration-300 border ${
                  currentThreadId === thread.id
                    ? 'bg-gradient-to-r from-jarvis-neon-cyan/15 to-jarvis-neon-purple/10 border-jarvis-neon-cyan/50 shadow-neon-cyan' 
                    : 'hover:bg-jarvis-bg-surface/40 border-jarvis-border-subtle hover:border-jarvis-neon-cyan/40 hover:shadow-glow-subtle-cyan'
                } backdrop-blur-sm`}
                onClick={() => setCurrentThread(thread.id)}
                whileHover={{ scale: 1.02, x: 4 }}
                whileTap={{ scale: 0.98 }}
              >
                {/* Glow effect for active thread */}
                {currentThreadId === thread.id && (
                  <div className="absolute inset-0 rounded-xl bg-gradient-to-r from-jarvis-neon-cyan/10 to-jarvis-neon-purple/5 animate-neon-pulse-cyan" />
                )}
                
                <div className="flex items-start gap-3 relative z-10">
                  <div className={`p-2 rounded-lg ${
                    currentThreadId === thread.id 
                      ? 'bg-jarvis-neon-cyan/20 text-jarvis-neon-cyan shadow-glow-subtle-cyan' 
                      : 'bg-jarvis-bg-surface/50 text-jarvis-neon-cyan/70'
                  } transition-all duration-300`}>
                    <MessageSquare className="h-4 w-4" />
                  </div>
                  
                  <div className="flex-1 min-w-0">
                    {editingThread === thread.id ? (
                      <div className="flex gap-2">
                        <Input
                          value={editTitle}
                          onChange={(e) => setEditTitle(e.target.value)}
                          onKeyDown={(e) => {
                            if (e.key === 'Enter') handleSaveTitle();
                            if (e.key === 'Escape') setEditingThread(null);
                          }}
                          className="cyber-input h-8 text-sm"
                          autoFocus
                        />
                      </div>
                    ) : (
                      <>
                        <h4 className="text-sm font-semibold text-jarvis-text-primary truncate mb-1 group-hover:text-jarvis-neon-cyan transition-colors">
                          {thread.title}
                        </h4>
                        <div className="flex items-center gap-2 text-xs">
                          <span className={`px-2 py-0.5 rounded-full border ${
                            currentThreadId === thread.id
                              ? 'bg-jarvis-neon-cyan/20 text-jarvis-neon-cyan border-jarvis-neon-cyan/40'
                              : 'bg-jarvis-bg-surface/50 text-jarvis-text-muted border-jarvis-border-subtle'
                          }`}>
                            {thread.model}
                          </span>
                          <span className="text-jarvis-neon-purple">•</span>
                          <span className="text-jarvis-text-muted">{formatDate(thread.updatedAt)}</span>
                        </div>
                      </>
                    )}
                  </div>

                  {/* Actions */}
                  {currentThreadId === thread.id && (
                    <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-all duration-300">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleEditTitle(thread);
                        }}
                        className="h-7 w-7 p-0 text-jarvis-text-muted hover:text-jarvis-neon-cyan hover:bg-jarvis-neon-cyan/10 border border-jarvis-neon-cyan/20 rounded-lg"
                      >
                        <Edit3 className="h-3 w-3" />
                      </Button>
                      
                      <AlertDialog>
                        <AlertDialogTrigger asChild>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={(e) => e.stopPropagation()}
                            className="h-7 w-7 p-0 text-jarvis-text-muted hover:text-jarvis-neon-pink hover:bg-jarvis-neon-pink/10 border border-jarvis-neon-pink/20 rounded-lg"
                          >
                            <Trash2 className="h-3 w-3" />
                          </Button>
                        </AlertDialogTrigger>
                        <AlertDialogContent className="glass-cyber border-jarvis-neon-cyan/30">
                          <AlertDialogHeader>
                            <AlertDialogTitle className="text-jarvis-neon-cyan">
                              Supprimer la conversation
                            </AlertDialogTitle>
                            <AlertDialogDescription className="text-jarvis-text-muted">
                              Êtes-vous sûr de vouloir supprimer "{thread.title}" ? 
                              Cette action est irréversible.
                            </AlertDialogDescription>
                          </AlertDialogHeader>
                          <AlertDialogFooter>
                            <AlertDialogCancel className="cyber-button-secondary">
                              Annuler
                            </AlertDialogCancel>
                            <AlertDialogAction 
                              onClick={() => handleDeleteThread(thread.id, thread.title)}
                              className="cyber-button-pink"
                            >
                              Supprimer
                            </AlertDialogAction>
                          </AlertDialogFooter>
                        </AlertDialogContent>
                      </AlertDialog>
                    </div>
                  )}
                </div>
              </motion.div>
            ))}
          </AnimatePresence>

          {filteredThreads.length === 0 && (
            <motion.div 
              className="text-center py-12 text-jarvis-text-muted"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.3 }}
            >
              <div className="w-16 h-16 mx-auto mb-4 bg-jarvis-bg-surface/50 rounded-full flex items-center justify-center border-2 border-jarvis-neon-cyan/20">
                <MessageSquare className="h-8 w-8 text-jarvis-neon-cyan/50" />
              </div>
              <p className="text-sm">
                {searchQuery ? 'Aucun résultat trouvé' : 'Aucune conversation'}
              </p>
            </motion.div>
          )}
        </div>
      </ScrollArea>

      {/* Footer Actions */}
      <div className="relative z-10 p-4 border-t-2 border-jarvis-neon-cyan/20 space-y-3">
        <div className="grid grid-cols-2 gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={handleExport}
            className="cyber-button-secondary text-xs"
          >
            <Download className="h-3 w-3 mr-1" />
            Export
          </Button>
          
          <label className="block">
            <input
              type="file"
              accept=".json"
              onChange={handleImport}
              className="hidden"
            />
            <Button
              variant="outline"
              size="sm"
              className="cyber-button-secondary text-xs w-full"
              asChild
            >
              <span>
                <Upload className="h-3 w-3 mr-1" />
                Import
              </span>
            </Button>
          </label>
        </div>

        <AlertDialog>
          <AlertDialogTrigger asChild>
            <Button
              variant="outline"
              size="sm"
              className="w-full text-jarvis-neon-orange border-jarvis-neon-orange/30 hover:bg-jarvis-neon-orange/10 hover:border-jarvis-neon-orange/50 text-xs"
            >
              <RotateCcw className="h-3 w-3 mr-2" />
              Effacer toutes les données
            </Button>
          </AlertDialogTrigger>
          <AlertDialogContent className="glass-cyber border-jarvis-neon-cyan/30">
            <AlertDialogHeader>
              <AlertDialogTitle className="text-jarvis-neon-orange">
                ⚠️ Effacer toutes les données
              </AlertDialogTitle>
              <AlertDialogDescription className="text-jarvis-text-muted">
                Cette action supprimera définitivement toutes vos conversations et paramètres. 
                Êtes-vous certain de vouloir continuer ?
              </AlertDialogDescription>
            </AlertDialogHeader>
            <AlertDialogFooter>
              <AlertDialogCancel className="cyber-button-secondary">
                Annuler
              </AlertDialogCancel>
              <AlertDialogAction 
                onClick={() => {
                  clearAllData();
                  toast({
                    title: "🗑️ Données effacées",
                    description: "Toutes les archives Jarvis ont été supprimées.",
                  });
                }}
                className="bg-jarvis-neon-orange/20 text-jarvis-neon-orange hover:bg-jarvis-neon-orange/30 border border-jarvis-neon-orange/50 shadow-neon-orange"
              >
                Confirmer l'effacement
              </AlertDialogAction>
            </AlertDialogFooter>
          </AlertDialogContent>
        </AlertDialog>
      </div>
    </motion.div>
  );
};

export default Sidebar;