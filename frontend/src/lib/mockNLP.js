// Mock responses for different types of queries
const mockResponses = {
  greeting: [
    "Bonjour ! Je suis Jarvis, votre assistant IA cyberpunk. Comment puis-je vous aider aujourd'hui ?",
    "Salut ! Système Jarvis opérationnel. Que puis-je faire pour vous ?",
    "Interface Jarvis activée. En quoi puis-je vous assister ?"
  ],
  
  technical: [
    "Analysing les données... Voici ce que j'ai trouvé : cette question nécessite une approche systémique. Permettez-moi de décomposer le problème en plusieurs étapes clés.\n\n**Étape 1:** Identification des paramètres critiques\n**Étape 2:** Analyse des contraintes système\n**Étape 3:** Proposition de solutions optimisées\n\nQuelle partie souhaitez-vous explorer en détail ?",
    "Traitement des requêtes en cours... Cette problématique implique plusieurs couches d'abstraction. Voici mon analyse :\n\n```python\n# Solution proposée\ndef analyze_problem(params):\n    # Logique d'analyse\n    return optimized_solution\n```\n\nVoulez-vous que je détaille l'implémentation ?",
    "Système expert en ligne. Votre question touche à un domaine complexe. Laissez-moi structurer ma réponse :\n\n1. **Context:** Définition du périmètre\n2. **Analysis:** Décomposition du problème  \n3. **Synthesis:** Solutions recommandées\n\nPar où commençons-nous ?"
  ],
  
  creative: [
    "Imagination augmentée activée... Voici quelques idées créatives qui pourraient vous intéresser :\n\n✨ **Concept A:** Une approche révolutionnaire\n✨ **Concept B:** Une solution hybride innovante\n✨ **Concept C:** Une perspective totalement différente\n\nQuelle direction vous inspire le plus ?",
    "Modules créatifs en fonctionnement... Je perçois plusieurs angles d'approche fascinants pour votre demande. Permettez-moi de vous proposer une exploration multidimensionnelle.\n\nChaque idée peut être développée selon vos préférences. Dites-moi ce qui résonne avec votre vision !",
    "Processeurs d'innovation en marche... Votre requête déclenche de nombreuses possibilités créatives. Je vais synthétiser quelques pistes prometteuses qui pourraient ouvrir de nouveaux horizons.\n\nQuel aspect souhaitez-vous approfondir ?"
  ],
  
  help: [
    "Guide d'utilisation Jarvis :\n\n**🎤 Commandes vocales:** Cliquez sur le micro pour parler\n**⚙️ Paramètres:** Accédez aux réglages via l'icône\n**💾 Export:** Sauvegardez vos conversations\n**🔄 Modèles:** Changez d'IA selon vos besoins\n\n**Commandes rapides:**\n`/model [nom]` - Changer de modèle\n`/temp [0.1-1.0]` - Ajuster la température\n`/clear` - Effacer la conversation\n`/export` - Exporter les données\n\nQue voulez-vous explorer ?",
    "Manuel d'interface Jarvis v2.0 :\n\n**Navigation:** Utilisez la sidebar pour gérer vos conversations\n**Personnalisation:** Adaptez l'interface à vos préférences\n**Performance:** Mode performance disponible pour les appareils limités\n**Accessibilité:** Interface optimisée pour tous les utilisateurs\n\nBesoin d'aide sur une fonctionnalité spécifique ?",
  ],
  
  default: [
    "Intéressant... Laissez-moi traiter cette information. Voici mon analyse basée sur mes algorithmes de compréhension avancés.\n\nCette question mérite une réponse structurée et détaillée. Permettez-moi de vous fournir une perspective éclairée sur le sujet.",
    "Analyse en cours... Votre requête active plusieurs modules de traitement. Je vais synthétiser une réponse complète qui adresse les différents aspects de votre question.\n\nVoici ce que je peux vous dire à ce sujet :",
    "Système cognitif engagé... Cette problématique nécessite une approche méthodique. Je vais vous proposer une réponse qui combine logique, créativité et expertise technique.\n\nCommençons par analyser les éléments clés :"
  ]
};

// Commands processor
const processCommand = (input) => {
  const command = input.toLowerCase().trim();
  
  if (command.startsWith('/model ')) {
    const modelName = command.replace('/model ', '');
    return `Modèle changé vers **${modelName}**. Les prochaines réponses utiliseront ce modèle.`;
  }
  
  if (command.startsWith('/temp ')) {
    const temp = command.replace('/temp ', '');
    return `Température ajustée à **${temp}**. La créativité des réponses sera adaptée en conséquence.`;
  }
  
  if (command === '/clear') {
    return `Conversation effacée. Une nouvelle session a été initialisée.`;
  }
  
  if (command === '/export') {
    return `Export des données en cours... Téléchargement du fichier JSON disponible.`;
  }
  
  if (command === '/help') {
    return mockResponses.help[0];
  }
  
  return null;
};

// Analyze input type
const analyzeInput = (input) => {
  const lowerInput = input.toLowerCase();
  
  // Check for commands first
  if (input.startsWith('/')) {
    return 'command';
  }
  
  // Greeting patterns
  if (/(salut|bonjour|hello|hi|hey)/i.test(lowerInput)) {
    return 'greeting';
  }
  
  // Technical patterns
  if (/(code|programming|développ|technique|algorithme|fonction|api|bug|erreur)/i.test(lowerInput)) {
    return 'technical';
  }
  
  // Creative patterns  
  if (/(créat|idée|imagination|innov|design|art|story|histoire)/i.test(lowerInput)) {
    return 'creative';
  }
  
  // Help patterns
  if (/(aide|help|comment|utilise|fonctionne)/i.test(lowerInput)) {
    return 'help';
  }
  
  return 'default';
};

// Generate mock response with streaming simulation
export const generateMockResponse = async (input, settings = {}) => {
  // Process commands
  const commandResult = processCommand(input);
  if (commandResult) {
    return commandResult;
  }
  
  // Analyze input type
  const inputType = analyzeInput(input);
  const responses = mockResponses[inputType] || mockResponses.default;
  
  // Select random response
  const baseResponse = responses[Math.floor(Math.random() * responses.length)];
  
  // Add model-specific touches
  let modelSignature = '';
  switch (settings.model) {
    case 'gpt-4':
      modelSignature = '\n\n*[GPT-4 Analysis Complete]*';
      break;
    case 'claude-3-opus':
      modelSignature = '\n\n*[Claude 3 Opus Processing]*';
      break;
    case 'gemini-pro':
      modelSignature = '\n\n*[Gemini Pro Synthesis]*';
      break;
    default:
      modelSignature = '\n\n*[Jarvis AI Response]*';
  }
  
  // Adjust response based on temperature
  const temp = settings.temperature || 0.7;
  if (temp > 0.8) {
    // Higher creativity - add more experimental language
    return baseResponse + '\n\nMode créatif activé ! 🚀' + modelSignature;
  } else if (temp < 0.3) {
    // Lower creativity - more structured
    return `**Analyse structurée:**\n\n${baseResponse}` + modelSignature;
  }
  
  return baseResponse + modelSignature;
};

// Mock STT result
export const generateMockTranscription = (duration = 1000) => {
  const samples = [
    "Bonjour Jarvis, comment allez-vous ?",
    "Pouvez-vous m'aider avec ce problème technique ?",
    "Créons quelque chose d'innovant ensemble",
    "Quelles sont les nouvelles fonctionnalités disponibles ?",
    "Analysez ce code et proposez des améliorations"
  ];
  
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve(samples[Math.floor(Math.random() * samples.length)]);
    }, duration);
  });
};