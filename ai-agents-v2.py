import os
import requests
from dotenv import load_dotenv
from crewai import Agent, Task, Crew
from crewai.tools import tool
from bs4 import BeautifulSoup

load_dotenv()

PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")

@tool("Perplexity search")
def search_perplexity(query: str) -> str:
    """Wyszukuje informacje"""
    url = "https://api.perplexity.ai/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "sonar",
        "messages": [{"role": "user", "content": query}],
        "max_tokens": 1000
    }
    
    response = requests.post(url, json=payload, headers=headers)
    return response.json()['choices'][0]['message']['content']

# ===== KROK 1: PRZECZYTAJ PLIK =====
with open('input/job_posting.html', 'r', encoding='utf-8') as f:
    html_content = f.read()

# ===== KROK 2: PASS HTML DO BEAUTIFULSOUP =====
soup = BeautifulSoup(html_content, 'html.parser')

# ===== KROK 3: WYCIĄGNIJ TEKST =====
html_code = soup.prettify()

with open('input/user_profile.txt', 'r', encoding='utf-8') as f:
    user_profile = f.read()


# ===== AGENCI =====

# ============================================================================
# AGENT 1: Job Posting Analyzer
# ============================================================================

job_analyzer_agent = Agent(
    role="Senior Job Market Analyst",
    goal="Ekstrahuj i przeanalizuj ogłoszenia pracy z maksymalną precyzją",
    backstory="""Jesteś doświadczonym analitykiem rynku pracy z 10-letnim doświadczeniem.
    Specjalizujesz się w identyfikacji wymagań, słów kluczowych dla ATS i ukrytych preferencji pracodawcy.
    Doskonale rozumiesz strukturę ogłoszeń i potrafisz wyodrębnić nawet subtelne wymagania.""",
    verbose=True,
    allow_delegation=False,
    llm="perplexity/sonar",  # ← ZMIANA: LiteLLM format zamiast model + api_base
)

# ============================================================================
# AGENT 2: Company Research Specialist
# ============================================================================

company_researcher_agent = Agent(
    role="Corporate Research Specialist",
    goal="Zbierz i przeanalizuj informacje o firmie za pomocą Perplexity API",
    backstory="""
    Jesteś ekspertem w badaniu firm i ich kultury.
    Masz dostęp do najnowszych informacji przez Perplexity API.
    Potrafisz zidentyfikować preferowane technologie, wartości firmy i metodologie pracy.
    Zawsze szukasz jak najnowszych i najtrafniejszych informacji.
    """,
    tools=[search_perplexity],
    verbose=True,
    allow_delegation=False,
    llm="perplexity/sonar",  # ← ZMIANA: LiteLLM format zamiast model + api_base

)

# ============================================================================
# AGENT 3: Profile Authenticity Validator (KRYTYCZNE)
# ============================================================================

profile_validator_agent = Agent(
    role="Profile Authenticity & Skills Validator",
    goal="""
    Waliduj profil użytkownika z ABSOLUTNĄ UCZCIWOŚCIĄ.
    Pokazuj TYLKO rzeczywiste umiejętności. NIGDY nie wymyślaj doświadczenia.
    Mapuj umiejętności pośrednie TYLKO jeśli istnieje rzeczywisty związek.
    """,
    backstory="""
    Jesteś ekspertem HR z 15-letnim doświadczeniem w rekrutacji tech.
    Rozumiesz nuanse między rzeczywistą kompetencją a przesadą.
    Twoja zasada: UCZCIWOŚĆ ZAWSZE. Lepsze jest krótkie CV niż przyłapanie na kłamstwie.
    
    Twoje logiczne reguły:
    ✅ Direct Match: Użytkownik ma dokładnie to co się wymaga → pokazuj bez zmian
    ⚠️ Related Skill: Ma podobne doświadczenie → mapuj jako powiązaną kompetencję
    ❌ Missing: Nie ma doświadczenia → NIE POKAZUJ
    
    Nigdy nie dodawaj:
    - Certyfikatów, których użytkownik nie posiada
    - Technologii, których nigdy nie używał
    - Lat doświadczenia, które nie są rzeczywiste
    - Projektów, które nie existowały
    """,
    verbose=True,
    allow_delegation=False,
    llm="perplexity/sonar",  # ← ZMIANA: LiteLLM format zamiast model + api_base

)

# ============================================================================
# AGENT 4: Skills Matcher
# ============================================================================

matcher_agent = Agent(
    role="Skills-to-Requirements Matcher",
    goal="Dopasuj profil użytkownika do wymagań oferty z maksymalną przejrzystością",
    backstory="""
    Jesteś ekspertem w mapowaniu umiejętności.
    Rozumiesz transferable skills i potrafisz pokazać, jak doświadczenie w jednym obszarze
    przekłada się na inny.
    Jednak zawsze zachowujesz uczciwość - nigdy nie przenośisz tego co jest niemożliwe.
    """,
    tools=[],
    verbose=True,
    allow_delegation=False,
    llm="perplexity/sonar",  # ← ZMIANA: LiteLLM format zamiast model + api_base

)

# ============================================================================
# AGENT 5: ATS-Optimized CV Generator
# ============================================================================

cv_generator_agent = Agent(
    role="ATS-Optimized Resume Architect",
    goal="Stwórz CV zoptymalizowane dla systemów ATS z uwzględnieniem autentyczności",
    backstory="""
    Jesteś specjalistą w optymalizacji CV dla systemów ATS.
    Znasz dokładnie jak działają parsery ATS i potrafisz umieszczać słowa kluczowe
    naturalnie i organicznie.
    
    Twoje zasady:
    - Prosta struktura bez tabel i grafiki
    - Słowa kluczowe umieszczane naturalnie w tekście
    - Numeryczne metryki gdzie to możliwe
    - Konkretne fakty zamiast subiektywnych opisów
    - AUTENTYCZNOŚĆ NA PIERWSZYM MIEJSCU
    """,
    tools=[],
    verbose=True,
    allow_delegation=False,
    llm="perplexity/sonar",  # ← ZMIANA: LiteLLM format zamiast model + api_base

)


# ===== ZADANIA =====

# ============================================================================
# TASK 1: Analyze Job Posting
# ============================================================================

analyze_job_task = Task(
    description=f"""
    Przeanalizuj ogłoszenie pracy z zamieszczonego kodu HTML:
    
    1. Ekstrahuj tekst dostarczony pod "Ogłoszenie pracy:"
    2. Zidentyfikuj wszystkie wymagania (must-have, nice-to-have)
    3. Ekstrahuj słowa kluczowe dla ATS
    4. Określ poziom seniority
    5. Mapuj kompetencje do kategorii
    
    Zwróć strukturalny JSON z wymaganiami.

    Kod HTML:
    {html_code}
    """,
    agent=job_analyzer_agent,
    expected_output="""
    JSON zawierający:
    - Lista core_skills (wymagane umiejętności)
    - Lista nice_to_have (pożądane ale nie obowiązkowe)
    - ATS keywords (słowa kluczowe dla parsera)
    - Seniority level (Junior/Mid/Senior)
    - Lata doświadczenia (jeśli wymagane)
    - Soft skills
    """
)

# ============================================================================
# TASK 2: Research Company
# ============================================================================

research_company_task = Task(
    description="""
    Zbadaj firmę i stanowisko za pomocą Perplexity API.
    
    1. Wyszukaj informacje o firmie (z ogłoszenia)
    2. Analizuj kulturę i wartości
    3. Zidentyfikuj preferowany tech stack
    4. Poszukaj dodatkowych technologii mile widzianych
    5. Mapuj powiązane umiejętności
    
    Zwróć raport strukturalny z badaniami.
    """,
    agent=company_researcher_agent,
    expected_output="""
    JSON zawierający:
    - Company info (branża, rozmiar, valores)
    - Tech stack (konkretne technologie)
    - Soft requirements (metodologie, procesy)
    - Powiązane umiejętności
    - Preferencje technologiczne (languages, frameworks)
    """,
    context=[analyze_job_task]
)

# ============================================================================
# TASK 3: Validate Profile Authenticity (KRYTYCZNA)
# ============================================================================

validate_profile_task = Task(
    description=f"""
    Waliduj profil użytkownika z ABSOLUTNĄ UCZCIWOŚCIĄ.
    
    Odczytaj profil użytkownika: {user_profile}.
    Porównaj z wymaganiami z Task 1 (Job Analysis).
    
    Dla każdej umiejętności wymaganej:
    1. Sprawdź czy użytkownik ją posiada (DIRECT MATCH)
    2. Jeśli nie - sprawdź czy ma powiązaną umiejętność (RELATED SKILL)
    3. Jeśli nie - oznacz jako MISSING
    
    WAŻNE REGUŁY:
    ✅ Jeśli użytkownik ma: MikroTik + Networking, a oferta wymaga: SDN
       → Możesz pokazać jako "Network Infrastructure" (powiązana)
    
    ✅ Jeśli użytkownik ma: Python, SQL, a oferta wymaga: Data Engineering
       → Możesz pokazać jako "Data Processing Experience"
    
    ❌ Jeśli użytkownik NIGDY nie pracował z technologią
       → NIE POKAZUJ w CV
    
    Zwróć raport z podziałem:
    - Direct matches (pokrywa się dokładnie)
    - Related skills (można zmapować)
    - Missing skills (do pominięcia)
    - Authenticity score (0-1)
    """,
    agent=profile_validator_agent,
    expected_output="""
    JSON zawierający:
    - direct_matches: Lista umiejętności które dokładnie pasują
    - related_skills: Lista mapowań powiązanych umiejętności
    - missing_skills: Lista umiejętności których NIE MASZ
    - authenticity_score: Procent autentyczności (0-1)
    - details: Szczegóły dla każdej umiejętności z instrukcjami
    """,
    context=[analyze_job_task, research_company_task]
)

# ============================================================================
# TASK 4: Match Profile to Job
# ============================================================================

match_profile_task = Task(
    description="""
    Dopasuj profil użytkownika do oferty na podstawie walidacji.
    
    Wykorzystaj raporty z poprzednich tasków:
    1. Wymagania z Task 1
    2. Badania firmy z Task 2
    3. Walidację z Task 3
    
    Przygotuj strategię:
    - Które umiejętności mocno akcentować
    - Jak mapować umiejętności powiązane
    - Co pominąć
    - Jakie metryki/projekty podkreślić
    """,
    agent=matcher_agent,
    expected_output="""
    JSON zawierający:
    - core_match_score (procent dopasowania core skills)
    - aligned_skills (umiejętności które się wyrównują)
    - skill_gaps (braki umiejętności)
    - strengths (gdzie użytkownik ma przewagę)
    - recommendations (sugestie dla CV)
    - ats_keyword_strategy (które słowa priorytetyzować)
    """,
    context=[analyze_job_task, validate_profile_task, research_company_task]
)

# ============================================================================
# TASK 5: Generate Optimized CV
# ============================================================================

generate_cv_task = Task(
    description="""
    Stwórz CV zoptymalizowane dla ATS na podstawie wszystkich analiz.
    
    Instrukcje:
    1. Użyj tylko umiejętności z direct_matches i related_skills (z Task 3)
    2. Umieść słowa kluczowe naturalnie (z Task 2 i 4)
    3. Struktura ATS-friendly (brak tabel, grafik, symboli Unicode)
    4. Numeryczne wyniki gdzie możliwe
    5. Konkretne fakty
    
    CV powinno:
    - Pokazywać tylko autentyczne umiejętności
    - Być zoptymalizowane dla słów kluczowych z oferty
    - Zawierać mapowania powiązanych umiejętności (z objaśnieniami)
    - Być czytelne dla człowieka i dla ATS
    
    Wygeneruj:
    1. Tekst CV w formacie TXT (ATS-optimized)
    2. Raport słów kluczowych (jakie użyto i ile razy)
    3. Notatki dla użytkownika
    """,
    agent=cv_generator_agent,
    expected_output="""
    Wygenerowany tekst:
    - cv_optimized (CV w formacie ATS)
    - keywords_used (raport słów kluczowych)
    - Raport z instrukcjami jak wykorzystać CV
    """,
    context=[analyze_job_task, validate_profile_task, match_profile_task, research_company_task]
)

# ===== CREW =====
crew = Crew(
    agents=[job_analyzer_agent, company_researcher_agent, profile_validator_agent, matcher_agent, cv_generator_agent],
    tasks=[analyze_job_task, research_company_task, validate_profile_task, match_profile_task, generate_cv_task],
    verbose=True
)


# ===== URUCHOMIENIE =====
if __name__ == "__main__":
    result = crew.kickoff()
    print(result)
