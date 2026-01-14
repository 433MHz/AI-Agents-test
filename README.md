# 🎯 Projekt CrewAI + Perplexity: System Inteligentnego Dopasowania CV

## SPIS TREŚCI
1. [Architektura Systemu](#architektura)
2. [Setup i Instalacja](#setup)
3. [Agenci i Zadania](#agenci)
4. [Kod Python](#kod-python)
5. [Instrukcja Wdrożenia](#wdrożenie)

---

## ARCHITEKTURA

### Przepływ Danych
```
PDF Oferty Pracy
    ↓
[Agent 1: Analityk Oferty] → Ekstrakcja wymagań
    ↓
[Agent 2: Badacz Firmy] + Perplexity API → Badania
    ↓
Plik TXT Profile Użytkownika
    ↓
[Agent 3: Validator Profilu] → Walidacja autentyczności
    ↓
[Agent 4: Matcher Profilu] → Dopasowanie
    ↓
[Agent 5: Generator CV] → CV Zoptymalizowane
    ↓
Wyjście: PDF/DOCX CV + Raport Walidacji
```

### Komponenty Systemu

| Komponent | Opis | Wejście | Wyjście |
|-----------|------|--------|--------|
| **Agent 1** | Analityk Oferty | PDF ogłoszenia | JSON wymagań, słowa kluczowe |
| **Agent 2** | Badacz Firmy | Nazwa firmy, stanowisko | Raport firmy + technologie |
| **Agent 3** | Validator Profilu | Wymagania + Profil użytkownika | Raport autentyczności |
| **Agent 4** | Matcher Profilu | Wymagania + Walidacja | Mapowanie dopasowań |
| **Agent 5** | Generator CV | Mapowanie + Instrukcje | CV zoptymalizowane |

---

## SETUP

### Wymagania
```
Python 3.9+
pip
```

### Instalacja Pakietów
```bash
pip install crewai crewai-tools python-dotenv
pip install perplexityai openai
pip install pypdf python-pptx python-docx
```

### Zmienne Środowiskowe (.env)
```env
PERPLEXITY_API_KEY=your_api_key_here
OPENAI_API_KEY=your_openai_key_here
```

**Gdzie zdobyć klucze:**
- **Perplexity:** https://www.perplexity.ai/api
- **OpenAI:** https://platform.openai.com/api-keys (jako backup dla lokalnego LLM)

---

## AGENCI

### Agent 1: Analityk Oferty Pracy

**Rola:** Senior Job Market Analyst

**Zadania:**
- Ekstrakcja tekstu z PDF
- Identyfikacja wymagań (must-have vs nice-to-have)
- Ekstrakcja słów kluczowych dla ATS
- Określenie poziomu seniority
- Mapowanie kompetencji do kategorii

**Expected Output:**
```json
{
  "job_title": "...",
  "company": "...",
  "experience_required": "...",
  "requirements": {
    "core_skills": ["Python", "AWS"],
    "nice_to_have": ["Kubernetes"],
    "soft_skills": ["Leadership", "Communication"],
    "ats_keywords": ["REST API", "Microservices"],
    "seniority_level": "Mid-Level"
  },
  "priority_skills": {
    "critical": [...],
    "important": [...],
    "secondary": [...]
  }
}
```

---

### Agent 2: Badacz Firmy

**Rola:** Corporate Research Specialist

**Tools:** Perplexity API (wyszukiwanie w internecie)

**Zadania:**
- Wyszukanie informacji o firmie
- Analiza kultury organizacyjnej
- Identyfikacja technologii używanych
- Znalezienie preferencji technologicznych
- Powiązanie umiejętności

**Expected Output:**
```json
{
  "company_info": {
    "industry": "...",
    "size": "...",
    "culture_keywords": ["Agile", "Innovation", "Collaboration"]
  },
  "tech_stack": ["Python", "Docker", "PostgreSQL"],
  "soft_requirements": [...],
  "similar_skills": {
    "MikroTik": ["Network Infrastructure", "SDN"],
    "Python": ["Data Processing", "Automation"]
  }
}
```

---

### Agent 3: Validator Profilu (KRYTYCZNY)

**Rola:** Profile Authenticity & Skills Validator

**Zadania (Surowa Logika):**

1. **Umiejętności Bezpośrednie (✅)**
   ```
   Masz: Python, SQL, Linux
   Oferta wymaga: Python, SQL, Linux
   → Pokazuj bez zmian
   ```

2. **Umiejętności Pośrednie (⚠️)**
   ```
   Masz: MikroTik, networking
   Oferta wymaga: SDN, Network Architecture
   Mapa: MikroTik = Network Infrastructure Foundation
   → Możesz pokazać jako powiązaną kompetencję
   ```

3. **Umiejętności Blisko Powiązane (🔗)**
   ```
   Masz: C++, Java
   Oferta wymaga: Python
   Analiza: Jeśli znasz OOP i zarządzanie pamięcią → nauczenie się Python jest szybkie
   → Wskaż jako "transferable skills" w Programing Fundamentals
   ```

4. **Brak Umiejętności (❌)**
   ```
   Masz: 0
   Oferta wymaga: AWS certifications
   → NIE pokazuj tego w CV
   ```

**Expected Output:**
```json
{
  "validation_report": {
    "direct_skills": {
      "present": ["Python", "SQL"],
      "match_percentage": 70
    },
    "related_skills": {
      "can_map": ["Infrastructure" → "Cloud Architecture"],
      "confidence": 0.8
    },
    "missing_skills": {
      "reject": ["AWS Certification", "Kubernetes"],
      "reason": "No experience"
    },
    "authenticity_score": 0.92
  }
}
```

---

### Agent 4: Matcher Profilu

**Rola:** Skills-to-Requirements Matcher

**Zadania:**
- Porównanie profilu z wymaganiami
- Identyfikacja luk
- Wskazanie silnych stron
- Mapowanie do preferencji firmy
- Wygenerowanie strategii

**Expected Output:**
```json
{
  "matching_analysis": {
    "core_match_score": 0.78,
    "aligned_skills": [...],
    "skill_gaps": [...],
    "strengths": [...],
    "recommendations": [...]
  }
}
```

---

### Agent 5: Generator CV Zoptymalizowanego

**Rola:** ATS-Optimized Resume Architect

**Zadania:**
- Generowanie CV w formacie ATS
- Integracja słów kluczowych
- Formatowanie bez tabel/grafik
- Wymienienie tylko autentycznych umiejętności
- Opisanie doświadczenia w kontekście oferty

**Expected Output:**
- Plik: `CV_Zoptymalizowane.txt` (ATS-friendly)
- Plik: `CV_Zoptymalizowane.docx` (do przeglądania)
- Plik: `Keywords_Used.txt` (lista słów kluczowych)

---

## KOD PYTHON

Struktury katalogów:

```
cv-ai-system/
├── .env
├── src/
│   ├── main.py              # Główny orchestrator
│   ├── agents.py            # Definicje agentów
│   ├── tasks.py             # Definicje zadań
│   ├── tools.py             # Narzędzia i integracje
│   └── config.py            # Konfiguracja
├── input/
│   ├── job_posting.pdf      # Ogłoszenie pracy
│   └── user_profile.txt     # Profil użytkownika
└── output/
    ├── cv_optimized.txt
    ├── cv_optimized.docx
    ├── validation_report.json
    └── keywords_used.txt
```

---

## WDROŻENIE

### Krok 1: Przygotuj Profil
Utwórz `input/user_profile.txt`:
```
=== DOŚWIADCZENIE ZAWODOWE ===
[Lata, stanowiska, osiągnięcia]

=== UMIEJĘTNOŚCI TECHNICZNE ===
[Język programowania, narzędzia, platformy]

=== UMIEJĘTNOŚCI MIĘKKIE ===
[Leadership, komunikacja, itp.]

=== INSTRUKCJE DLA AGENTÓW ===
- Priorytetyzuj: Python, Linux, Infrastructure
- Unikaj: Przesady w "ekspercie"
- Akcentuj: Praktyczne doświadczenie
```

### Krok 2: Dodaj PDF Oferty
Umieść ogłoszenie w: `input/job_posting.pdf`

### Krok 3: Uruchom System
```bash
python src/main.py
```

### Krok 4: Sprawdź Wyniki
Pliki w `output/` zawierają:
- CV zoptymalizowane
- Raport walidacji
- Listę słów kluczowych

---

## ZASADY AUTENTYCZNOŚCI (Implementacja w Kodzie)

### Do Implementacji w Agent 3:

```python
# WOLNO robić:
✅ Zmienić sformułowanie
   "Linux admin" → "Infrastructure Management"
   
✅ Podkreślić umiejętności pośrednie
   Jeśli: MikroTik + networking
   To: "Network Infrastructure" (bez kłamstwa)
   
✅ Opisać szerzej, jeśli masz podstawy
   Masz: Python + SQL
   Oferta: Data Engineering
   Możesz: "Experience with data processing and SQL optimization"
   
✅ Wskazać transferable skills
   Masz: C++ (OOP, Pointers, Memory Management)
   Oferta: Python
   Możesz: "Strong foundation in programming fundamentals, quick learner"

# NIE wolno robić:
❌ Wymyślać technologie
   NIE: Kubernetes (jeśli 0 doświadczenia)
   
❌ Fałszować lata doświadczenia
   Masz: 6 m-cy Pythona
   NIE pisz: "5 years Python"
   
❌ Dodawać certyfikaty, których nie masz
❌ Opisywać projektów, które nie istnieją
❌ Twierdzić opanowanie, jeśli nie znasz podstaw
```

---

## OPTYMALIZACJA ATS (Algorytmiczna)

System będzie:
1. **Używać słów kluczowych** z ogłoszenia (jeśli się odnoszą)
2. **Zachować prostą strukturę** (bez tabel, kolumn, symboli Unicode)
3. **Numerować metryki** gdzie możliwe
4. **Zmapować terminy** (np. "sysadmin" → "infrastructure management")
5. **Priorytetyzować** na podstawie profilu użytkownika
6. **Walidować każde stwierdzenie** przed umieszczeniem w CV

---

## OUTPUTY

### Output 1: CV Zoptymalizowane (TXT)
```
[Formatowanie ATS-friendly]
[Słowa kluczowe z mapy]
[Tylko autentyczne umiejętności]
[Strukturalna jasność]
```

### Output 2: CV Zoptymalizowane (DOCX)
Ładniej sformatowany, do przeglądania

### Output 3: Raport Walidacji
```json
{
  "validation_summary": {
    "authentic_skills_shown": 18,
    "related_skills_mapped": 5,
    "skills_rejected": 3,
    "authenticity_score": 0.92,
    "ats_optimization_score": 0.88
  },
  "details": {
    "direct_matches": [...],
    "related_mappings": [...],
    "rejections_with_reasons": [...]
  },
  "recommendations": [...]
}
```

### Output 4: Keywords List
```
TOP 20 ATS KEYWORDS:
1. Python (12 matches)
2. Linux (8 matches)
3. Infrastructure (7 matches)
...
```

---

## SCHEMAT WDROŻENIA

### Faza 1: Setup (5 minut)
- Instalacja pakietów
- Konfiguracja klucze API
- Przygotowanie struktury katalogów

### Faza 2: Przygotowanie Danych (10 minut)
- Wklejenie profilu użytkownika
- Upload PDF ogłoszenia

### Faza 3: Kalibracja (opcjonalne)
- Modyfikacja instrukcji w `user_profile.txt`
- Testowanie na jednym CV

### Faza 4: Produkcja
- Uruchomienie dla kolejnych ofert
- Monitorowanie wyników
- Iteracyjne ulepszenia

---

## TROUBLESHOOTING

| Problem | Rozwiązanie |
|---------|-------------|
| `PERPLEXITY_API_KEY not found` | Sprawdź `.env` i ustaw zmienną |
| Brak wyniku z Agent 2 | Perplexity API niedostępny - fallback do googla |
| PDF nie parsuje się | Konwertuj na TXT lub zmień format |
| Agent 3 odmawia map | Zmień instrukcje - zbyt rygorystyczne |
| CV zbyt krótkie | Rozważ mapowanie więcej relacionowanych umiejętności |

---

## NOTES (WAŻNE)

1. **Perplexity API** - jeśli niedostępny, system fallback do lokalnego LLM
2. **Autentyczność** - priorytet #1, lepiej CV krótsze niż przyłapane na kłamstwie
3. **Iteracja** - system jest przygotowany do continuous improvement
4. **Prywatność** - wszystko dzieje się lokalnie poza Perplexity badaniami

---

Przejdź do sekcji **KOD PYTHON** aby zobaczyć implementację! ⬇️
