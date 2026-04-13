# TODO — Social Media Automation Pipeline

## 🎯 Standardisation

### Templates
- [ ] Définir une structure standard pour les paramètres des templates :
  - `title`
  - `text`
  - `hook`
  - `story`
  - `punch`
  - `cta`
  - `tag`
  - `footer`
  - `bg` (image)
  - `logo`
  - `W`, `H`
- [ ] Créer un schéma commun (JSON) pour tous les types de contenu
- [ ] Harmoniser les noms entre les différents templates (cover, insight, story, etc.)

---

## 🖼️ Gestion des images

- [ ] Intégrer plusieurs APIs d’images libres de droits :
  - Pexels
  - Unsplash
  - Pixabay
- [ ] Créer un fallback automatique si une API échoue
- [ ] Ajouter une pondération / priorité des sources

### IA Images
- [ ] Ajouter génération d’images via IA
- [ ] Définir une stratégie :
  - quand utiliser stock vs IA
- [ ] Uniformiser le format de sortie (URL / local path)

---

## 🧠 Refactor texte

- [ ] Standardiser le format d’entrée/sortie des textes
- [ ] Créer une interface unique pour :
  - adaptation par plateforme
  - adaptation par taille (`short`, `medium`, `long`)
- [ ] Ajouter validation du format JSON retourné par le LLM

---

## 🧱 Architecture (Design Patterns)

### Strategy Pattern

- [ ] Implémenter un pattern Strategy pour :

#### 1. Image Providers
- [ ] `PexelsStrategy`
- [ ] `UnsplashStrategy`
- [ ] `AIImageStrategy`

#### 2. Text Refactoring
- [ ] `LLMRefactorStrategy`
- [ ] (optionnel) `RuleBasedRefactorStrategy`

#### 3. Template Rendering
- [ ] `InsightTemplateStrategy`
- [ ] `StoryTemplateStrategy`
- [ ] `HookTemplateStrategy`
- [ ] `EducationalTemplateStrategy`
- [ ] `ViralTemplateStrategy`

---

## 🔁 Pipeline

- [ ] Créer un orchestrateur central :
  - input → post JSON
  - select strategy (text / image / template)
  - render HTML
  - export image
- [ ] Ajouter gestion des erreurs globale
- [ ] Logger chaque étape du pipeline

---

## 🚀 Améliorations futures

- [ ] A/B testing automatique des contenus
- [ ] Scheduler de publication
- [ ] Cache des images / contenus
- [ ] Génération batch de posts
- [ ] Metrics / tracking performance