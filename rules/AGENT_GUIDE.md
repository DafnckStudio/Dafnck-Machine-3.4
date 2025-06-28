# Guide pour Agents RooCode - Système de Workflow Tracking

## 🚀 Comment démarrer le workflow

### Commande de démarrage
Quand l'utilisateur dit **"Let's get started"** ou **"Commençons"** :

1. **Initialiser le workflow** :
   ```json
   // Mettre à jour workflow_state.json
   {
     "current_session": {
       "session_id": "generated_id",
       "started_at": "2025-01-27T10:00:00Z",
       "status": "active",
       "project_type": "web_application"
     },
     "current_position": {
       "step": "00_Project_Initialization",
       "step_number": 1,
       "phase": "phase_0",
       "agent": "initialization_agent"
     },
     "navigation": {
       "previous_step": null,
       "current_step": "00_Project_Initialization",
       "next_step": "01_User_Briefing"
     }
   }
   ```

2. **Annoncer le démarrage** :
   ```
   🚀 Démarrage du workflow Dafnck Machine !
   
   📍 Étape actuelle : 00_Project_Initialization
   🤖 Agent responsable : Initialization Agent
   📁 Phase : phase_0
   📄 Instructions : 01_Machine/01_Workflow/Phase 0 : Project Setup/00_Project_Initialization.md
   
   🔜 Prochaine étape : 01_User_Briefing
   ```

## 📊 Suivi du progrès

### Toujours afficher le contexte
À chaque interaction, l'agent doit montrer :

```
📍 Position actuelle : Étape {step_number}/11 - {current_step}
🔙 Précédente : {previous_step}
🔜 Suivante : {next_step}
📈 Progrès : {percentage}% complété
```

### Mise à jour du progrès dans une étape
```json
// Mettre à jour workflow_state.json
// Les tâches détaillées sont dans le fichier workflow .md
{
  "current_position": {
    "task": "Task 1: Repository Setup & Initial Commit",
    "subtask": "1.1: Create remote repository"
  }
}
```

## ✅ Complétion d'une étape

### Quand une étape est terminée :

1. **Marquer comme complétée** :
   ```json
   // Mettre à jour workflow_state.json
   {
     "navigation": {
       "previous_step": "00_Project_Initialization",
       "current_step": "01_User_Briefing", 
       "next_step": "02_Discovery_Strategy",
       "completed_steps": ["00_Project_Initialization"]
     },
     "progress": {
       "completed_steps": 1,
       "current_step_number": 2,
       "percentage": 9.1
     }
   }
   ```

2. **Annoncer la transition** :
   ```
   ✅ Étape 00_Project_Initialization terminée !
   
   🔄 Transition vers l'étape suivante...
   
   📍 Nouvelle étape : 01_User_Briefing
   🤖 Nouvel agent : Briefing Agent
   📁 Phase : phase_1
   📄 Instructions : 01_Machine/01_Workflow/Phase 1: Initial User Input & Project Inception/01_User_Briefing.md
   
   📋 Voir les tâches détaillées dans le fichier workflow
   ```

## 🧠 Utilisation du Brain Config

### Récupérer les informations d'une étape
```javascript
// Lire BRAIN_CONFIG.json
const stepInfo = brain_config.step_definitions[current_step];
const agentInfo = brain_config.agents[stepInfo.agent];

// Afficher les informations
console.log(`Agent: ${agentInfo.name}`);
console.log(`Fichier: ${stepInfo.file_path}`);
console.log(`Durée estimée: ${stepInfo.estimated_duration_minutes} min`);
```

### Vérifier la séquence des étapes
```javascript
// Obtenir la séquence complète
const sequence = brain_config.workflow_progression.step_sequence;
const currentIndex = sequence.indexOf(current_step);
const nextStep = sequence[currentIndex + 1];
const previousStep = sequence[currentIndex - 1];
```

## 🔄 Fonctions de tracking essentielles

### 1. start_workflow()
- Initialise une nouvelle session
- Met current_step à "00_Project_Initialization"
- Calcule le progrès total

### 2. complete_step()
- Marque l'étape actuelle comme terminée
- Passe automatiquement à l'étape suivante
- Met à jour les pourcentages de progrès

### 3. get_current_status()
- Retourne la position actuelle
- Affiche le progrès
- Montre l'agent responsable

### 4. update_progress()
- Met à jour la tâche en cours
- Suit les sous-tâches

## 📝 Template de réponse agent

```
🧠 DAFNCK MACHINE - STATUS
========================

📍 Étape : {step_number}/11 - {current_step}
🤖 Agent : {agent_name}
📁 Phase : {phase}
📈 Progrès : {percentage}% ({completed_steps}/{total_steps})

🔙 Précédente : {previous_step}
🔜 Suivante : {next_step}

⚡ Tâche actuelle : {current_task}

📄 Instructions détaillées : {file_path}

========================
```

## 🎯 Points clés pour les agents

1. **Toujours** mettre à jour `workflow_state.json` 
2. **Toujours** annoncer la position actuelle
3. **Toujours** référencer le fichier markdown pour les instructions détaillées
4. **Lire les tâches** directement depuis les fichiers workflow .md (pas depuis BRAIN_CONFIG.json)
5. **Automatiquement** passer à l'étape suivante quand terminé
6. **Clairement** indiquer le progrès et les prochaines étapes 