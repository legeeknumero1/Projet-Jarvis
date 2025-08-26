import React, { useState, useMemo } from 'react';
import { motion } from 'framer-motion';
import { 
  Plus, 
  Search, 
  MessageSquare, 
  Trash2, 
  Edit3,
  Download,
  Upload,
  RotateCcw
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
      title: "Nouvelle conversation",
      description: "Une nouvelle conversation a été créée.",
    });
  };

  const handleDeleteThread = (threadId, threadTitle) => {
    deleteThread(threadId);
    toast({
      title: "Conversation supprimée",
      description: `"${threadTitle}" a été supprimée.`,
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
        title: "Titre mis à jour",
        description: "Le titre de la conversation a été modifié.",
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
      title: "Export réussi",
      description: "Vos données ont été exportées avec succès.",
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
          title: "Import réussi",
          description: "Vos données ont été importées avec succès.",
        });
      } catch (error) {
        toast({
          title: "Erreur d'import",
          description: "Le fichier sélectionné n'est pas valide.",
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
    if (diffDays <= 7) return `Il y a ${diffDays - 1} jours`;
    return date.toLocaleDateString('fr-FR', { 
      day: 'numeric', 
      month: 'short' 
    });
  };

  return (
    <motion.div 
      className="h-full glass border-r border-jarvis-border flex flex-col"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.3 }}
    >
      {/* Header */}
      <div className="p-4 border-b border-jarvis-border">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-jarvis-text">Conversations</h2>
          <Button
            onClick={handleNewChat}
            size="sm"
            className="bg-jarvis-primary/10 text-jarvis-primary hover:bg-jarvis-primary/20 border border-jarvis-primary/30"
          >
            <Plus className="h-4 w-4" />
          </Button>
        </div>

        {/* Search */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-jarvis-text-muted" />
          <Input
            placeholder="Rechercher dans les conversations..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-10 bg-jarvis-surface/50 border-jarvis-border text-jarvis-text placeholder:text-jarvis-text-muted focus:border-jarvis-primary"
          />
        </div>
      </div>

      {/* Threads List */}
      <ScrollArea className="flex-1 px-2">
        <div className="space-y-1 py-2">
          {filteredThreads.map((thread) => (
            <motion.div
              key={thread.id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              className={`group relative rounded-lg p-3 cursor-pointer transition-all duration-200 ${
                currentThreadId === thread.id
                  ? 'bg-jarvis-primary/10 border border-jarvis-primary/30 glow-primary'
                  : 'hover:bg-jarvis-surface/50 border border-transparent'
              }`}
              onClick={() => setCurrentThread(thread.id)}
            >
              <div className="flex items-start gap-3">
                <MessageSquare className="h-4 w-4 text-jarvis-info mt-1 flex-shrink-0" />
                
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
                        className="h-6 text-sm bg-jarvis-surface border-jarvis-border"
                        autoFocus
                      />
                    </div>
                  ) : (
                    <>
                      <h4 className="text-sm font-medium text-jarvis-text truncate mb-1">
                        {thread.title}
                      </h4>
                      <div className="flex items-center gap-2 text-xs text-jarvis-text-muted">
                        <span>{thread.model}</span>
                        <span>•</span>
                        <span>{formatDate(thread.updatedAt)}</span>
                      </div>
                    </>
                  )}
                </div>

                {/* Actions */}
                {currentThreadId === thread.id && (
                  <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleEditTitle(thread);
                      }}
                      className="h-6 w-6 p-0 text-jarvis-text-muted hover:text-jarvis-primary"
                    >
                      <Edit3 className="h-3 w-3" />
                    </Button>
                    
                    <AlertDialog>
                      <AlertDialogTrigger asChild>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={(e) => e.stopPropagation()}
                          className="h-6 w-6 p-0 text-jarvis-text-muted hover:text-red-400"
                        >
                          <Trash2 className="h-3 w-3" />
                        </Button>
                      </AlertDialogTrigger>
                      <AlertDialogContent className="glass border-jarvis-border">
                        <AlertDialogHeader>
                          <AlertDialogTitle className="text-jarvis-text">
                            Supprimer la conversation
                          </AlertDialogTitle>
                          <AlertDialogDescription className="text-jarvis-text-muted">
                            Êtes-vous sûr de vouloir supprimer "{thread.title}" ? 
                            Cette action est irréversible.
                          </AlertDialogDescription>
                        </AlertDialogHeader>
                        <AlertDialogFooter>
                          <AlertDialogCancel className="text-jarvis-text border-jarvis-border">
                            Annuler
                          </AlertDialogCancel>
                          <AlertDialogAction 
                            onClick={() => handleDeleteThread(thread.id, thread.title)}
                            className="bg-red-500/20 text-red-400 hover:bg-red-500/30 border-red-500/30"
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

          {filteredThreads.length === 0 && (
            <div className="text-center py-8 text-jarvis-text-muted">
              <MessageSquare className="h-8 w-8 mx-auto mb-2 opacity-50" />
              <p className="text-sm">
                {searchQuery ? 'Aucun résultat trouvé' : 'Aucune conversation'}
              </p>
            </div>
          )}
        </div>
      </ScrollArea>

      {/* Footer Actions */}
      <div className="p-4 border-t border-jarvis-border space-y-2">
        <div className="flex gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={handleExport}
            className="flex-1 text-jarvis-text border-jarvis-border hover:bg-jarvis-surface/50"
          >
            <Download className="h-4 w-4 mr-2" />
            Export
          </Button>
          
          <label className="flex-1">
            <input
              type="file"
              accept=".json"
              onChange={handleImport}
              className="hidden"
            />
            <Button
              variant="outline"
              size="sm"
              className="w-full text-jarvis-text border-jarvis-border hover:bg-jarvis-surface/50"
              asChild
            >
              <span>
                <Upload className="h-4 w-4 mr-2" />
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
              className="w-full text-red-400 border-red-500/30 hover:bg-red-500/10"
            >
              <RotateCcw className="h-4 w-4 mr-2" />
              Tout effacer
            </Button>
          </AlertDialogTrigger>
          <AlertDialogContent className="glass border-jarvis-border">
            <AlertDialogHeader>
              <AlertDialogTitle className="text-jarvis-text">
                Effacer toutes les données
              </AlertDialogTitle>
              <AlertDialogDescription className="text-jarvis-text-muted">
                Cette action supprimera toutes vos conversations et paramètres. 
                Êtes-vous certain de vouloir continuer ?
              </AlertDialogDescription>
            </AlertDialogHeader>
            <AlertDialogFooter>
              <AlertDialogCancel className="text-jarvis-text border-jarvis-border">
                Annuler
              </AlertDialogCancel>
              <AlertDialogAction 
                onClick={() => {
                  clearAllData();
                  toast({
                    title: "Données effacées",
                    description: "Toutes vos données ont été supprimées.",
                  });
                }}
                className="bg-red-500/20 text-red-400 hover:bg-red-500/30 border-red-500/30"
              >
                Tout effacer
              </AlertDialogAction>
            </AlertDialogFooter>
          </AlertDialogContent>
        </AlertDialog>
      </div>
    </motion.div>
  );
};

export default Sidebar;