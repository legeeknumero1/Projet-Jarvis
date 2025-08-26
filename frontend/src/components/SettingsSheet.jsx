import React from 'react';
import { motion } from 'framer-motion';
import { 
  X, 
  Volume2, 
  VolumeX, 
  Zap, 
  ZapOff,
  Monitor,
  Smartphone,
  Accessibility
} from 'lucide-react';
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
  SheetClose,
} from './ui/sheet';
import { Button } from './ui/button';
import { Label } from './ui/label';
import { Slider } from './ui/slider';
import { Switch } from './ui/switch';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from './ui/select';
import { Separator } from './ui/separator';
import useJarvisStore from '../lib/store';
import { useToast } from '../hooks/use-toast';

const SettingsSheet = () => {
  const {
    showSettings,
    toggleSettings,
    settings,
    updateSettings,
    exportData,
    clearAllData
  } = useJarvisStore();
  
  const { toast } = useToast();

  const handleExport = () => {
    const data = exportData();
    const blob = new Blob([JSON.stringify(data, null, 2)], {
      type: 'application/json',
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `jarvis-settings-${new Date().toISOString().split('T')[0]}.json`;
    a.click();
    URL.revokeObjectURL(url);
    
    toast({
      title: "Paramètres exportés",
      description: "Vos paramètres ont été sauvegardés avec succès.",
    });
  };

  const resetToDefaults = () => {
    updateSettings({
      temperature: 0.7,
      topP: 0.9,
      voiceEnabled: true,
      language: 'fr-FR',
      performanceMode: false,
      reducedMotion: false,
    });
    
    toast({
      title: "Paramètres réinitialisés",
      description: "Tous les paramètres ont été remis aux valeurs par défaut.",
    });
  };

  const languages = [
    { code: 'fr-FR', name: 'Français (France)' },
    { code: 'en-US', name: 'English (US)' },
    { code: 'en-GB', name: 'English (UK)' },
    { code: 'es-ES', name: 'Español' },
    { code: 'de-DE', name: 'Deutsch' },
    { code: 'it-IT', name: 'Italiano' },
    { code: 'pt-PT', name: 'Português' },
  ];

  return (
    <Sheet open={showSettings} onOpenChange={toggleSettings}>
      <SheetContent 
        className="glass border-jarvis-border bg-jarvis-surface/95 backdrop-blur-xl w-96"
        side="right"
      >
        <SheetHeader>
          <SheetTitle className="text-jarvis-text flex items-center gap-2">
            <Zap className="h-5 w-5 text-jarvis-primary" />
            Paramètres Jarvis
          </SheetTitle>
          <SheetDescription className="text-jarvis-text-muted">
            Configurez votre assistant IA selon vos préférences.
          </SheetDescription>
        </SheetHeader>

        <div className="space-y-6 mt-6">
          {/* AI Model Settings */}
          <div className="space-y-4">
            <h3 className="text-sm font-semibold text-jarvis-text flex items-center gap-2">
              <Monitor className="h-4 w-4" />
              Paramètres du modèle
            </h3>
            
            {/* Temperature */}
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <Label className="text-jarvis-text">Créativité</Label>
                <span className="text-xs text-jarvis-text-muted bg-jarvis-bg px-2 py-1 rounded">
                  {settings.temperature}
                </span>
              </div>
              <Slider
                value={[settings.temperature]}
                onValueChange={([value]) => updateSettings({ temperature: value })}
                max={1}
                min={0}
                step={0.1}
                className="w-full"
              />
              <div className="flex justify-between text-xs text-jarvis-text-muted">
                <span>Précis</span>
                <span>Créatif</span>
              </div>
            </div>

            {/* Top-P */}
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <Label className="text-jarvis-text">Focus</Label>
                <span className="text-xs text-jarvis-text-muted bg-jarvis-bg px-2 py-1 rounded">
                  {settings.topP}
                </span>
              </div>
              <Slider
                value={[settings.topP]}
                onValueChange={([value]) => updateSettings({ topP: value })}
                max={1}
                min={0}
                step={0.1}
                className="w-full"
              />
              <div className="flex justify-between text-xs text-jarvis-text-muted">
                <span>Concentré</span>
                <span>Exploratoire</span>
              </div>
            </div>
          </div>

          <Separator className="bg-jarvis-border" />

          {/* Voice Settings */}
          <div className="space-y-4">
            <h3 className="text-sm font-semibold text-jarvis-text flex items-center gap-2">
              {settings.voiceEnabled ? (
                <Volume2 className="h-4 w-4" />
              ) : (
                <VolumeX className="h-4 w-4" />
              )}
              Interface vocale
            </h3>

            {/* Voice Enabled */}
            <div className="flex items-center justify-between">
              <div>
                <Label className="text-jarvis-text">Activation vocale</Label>
                <p className="text-xs text-jarvis-text-muted mt-1">
                  Utiliser le micro pour la saisie vocale
                </p>
              </div>
              <Switch
                checked={settings.voiceEnabled}
                onCheckedChange={(enabled) => updateSettings({ voiceEnabled: enabled })}
              />
            </div>

            {/* Language Selection */}
            {settings.voiceEnabled && (
              <div className="space-y-2">
                <Label className="text-jarvis-text">Langue de reconnaissance</Label>
                <Select
                  value={settings.language}
                  onValueChange={(language) => updateSettings({ language })}
                >
                  <SelectTrigger className="bg-jarvis-bg border-jarvis-border text-jarvis-text">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent className="glass border-jarvis-border bg-jarvis-surface">
                    {languages.map((lang) => (
                      <SelectItem
                        key={lang.code}
                        value={lang.code}
                        className="text-jarvis-text hover:bg-jarvis-primary/10"
                      >
                        {lang.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            )}
          </div>

          <Separator className="bg-jarvis-border" />

          {/* Performance & Accessibility */}
          <div className="space-y-4">
            <h3 className="text-sm font-semibold text-jarvis-text flex items-center gap-2">
              <Accessibility className="h-4 w-4" />
              Performance & Accessibilité
            </h3>

            {/* Performance Mode */}
            <div className="flex items-center justify-between">
              <div>
                <Label className="text-jarvis-text">Mode performance</Label>
                <p className="text-xs text-jarvis-text-muted mt-1">
                  Désactiver les effets visuels pour améliorer les performances
                </p>
              </div>
              <Switch
                checked={settings.performanceMode}
                onCheckedChange={(enabled) => updateSettings({ performanceMode: enabled })}
              />
            </div>

            {/* Reduced Motion */}
            <div className="flex items-center justify-between">
              <div>
                <Label className="text-jarvis-text">Réduire les animations</Label>
                <p className="text-xs text-jarvis-text-muted mt-1">
                  Limiter les animations pour plus de confort
                </p>
              </div>
              <Switch
                checked={settings.reducedMotion}
                onCheckedChange={(enabled) => updateSettings({ reducedMotion: enabled })}
              />
            </div>

            {/* Device Detection */}
            <div className="p-3 bg-jarvis-bg/50 rounded-lg border border-jarvis-border/50">
              <div className="flex items-center gap-2 text-sm text-jarvis-text-muted">
                <Smartphone className="h-4 w-4" />
                <span>
                  Détection automatique: {window.innerWidth < 768 ? 'Mobile' : 'Desktop'}
                </span>
              </div>
            </div>
          </div>

          <Separator className="bg-jarvis-border" />

          {/* Actions */}
          <div className="space-y-3">
            <h3 className="text-sm font-semibold text-jarvis-text">Actions</h3>
            
            <div className="grid grid-cols-2 gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={handleExport}
                className="text-jarvis-text border-jarvis-border hover:bg-jarvis-surface/50"
              >
                Exporter
              </Button>
              
              <Button
                variant="outline"
                size="sm"
                onClick={resetToDefaults}
                className="text-jarvis-text border-jarvis-border hover:bg-jarvis-surface/50"
              >
                Défauts
              </Button>
            </div>

            <Button
              variant="outline"
              size="sm"
              onClick={() => {
                clearAllData();
                toast({
                  title: "Données effacées",
                  description: "Toutes vos données ont été supprimées.",
                });
              }}
              className="w-full text-red-400 border-red-500/30 hover:bg-red-500/10"
            >
              Effacer toutes les données
            </Button>
          </div>
        </div>

        {/* Footer */}
        <div className="absolute bottom-4 left-4 right-4 text-xs text-jarvis-text-muted text-center">
          Jarvis AI v2.0 - Interface cyberpunk
        </div>
      </SheetContent>
    </Sheet>
  );
};

export default SettingsSheet;