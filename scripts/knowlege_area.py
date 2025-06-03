import os
import json
import re
from slugify import slugify

INPUT_DIR = "public/biografias_json"
OUTPUT_DIR = "biografias_com_areas"
LOG_PATH = os.path.join(OUTPUT_DIR, "log.txt")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Palavras-chave em inglês mapeadas para áreas matemáticas
KEYWORDS_MAP = {
    # Algebra
    " algebra ": "Algebra",
    " linear algebra ": "Algebra",
    " abstract algebra ": "Algebra",
    " group theory ": "Algebra",
    " groups ": "Algebra",
    " rings ": "Algebra",
    " ring ": "Algebra",
    " vector space ": "Algebra",
    " matrices ": "Algebra",
    " matrix theory ": "Algebra",

    # Geometry
    " geometry ": "Geometry",
    " differential geometry ": "Geometry",
    " euclidean geometry ": "Geometry",
    " non-euclidean geometry ": "Geometry",
    " analytic geometry ": "Geometry",
    " projective geometry ": "Geometry",
    " geometric structures ": "Geometry",
    " geodesic ": "Geometry",
    " curvature ": "Geometry",

    # Calculus
    " calculus ": "Calculus",
    " integral ": "Calculus",
    " integrals ": "Calculus",
    " integration ": "Calculus",
    " derivatives ": "Calculus",
    " derivative ": "Calculus",
    " differential equations ": "Calculus",
    " rate of change ": "Calculus",
    " infinitesimal ": "Calculus",
    " limits ": "Calculus",
    " limit ": "Calculus",

    # Statistics
    " statistics ": "Statistics",
    " statistical ": "Statistics",
    " probability ": "Statistics",
    " probabilistic ": "Statistics",
    " random variable ": "Statistics",
    " stochastic ": "Statistics",
    " data analysis ": "Statistics",
    " hypothesis testing ": "Statistics",

    # Analysis
    " analysis ": "Analysis",
    " real analysis ": "Analysis",
    " complex analysis ": "Analysis",
    " functional analysis ": "Analysis",
    " sequence ": "Analysis",
    " series ": "Analysis",
    " convergence ": "Analysis",
    " continuity ": "Analysis",
    " function ": "Analysis",
    " functions ": "Analysis",

    # Number Theory
    " number theory ": "Number Theory",
    " prime number ": "Number Theory",
    " primes ": "Number Theory",
    " modular arithmetic ": "Number Theory",
    " congruences ": "Number Theory",
    " diophantine equation ": "Number Theory",
    " integers ": "Number Theory",
    " arithmetic ": "Number Theory",

    # Topology
    " topology ": "Topology",
    " topological ": "Topology",
    " manifold ": "Topology",
    " manifolds ": "Topology",
    " homeomorphism ": "Topology",
    " open sets ": "Topology",
    " continuity ": "Topology",
    " compactness ": "Topology",

    # Logic
    " logic ": "Logic",
    " logical ": "Logic",
    " formal logic ": "Logic",
    " proof ": "Logic",
    " proofs ": "Logic",
    " theorem ": "Logic",
    " theorems ": "Logic",
    " propositional logic ": "Logic",
    " predicate logic ": "Logic",
    " set theory ": "Logic",
    " axioms ": "Logic",

    # Combinatorics
    " combinatorics ": "Combinatorics",
    " combinatorial ": "Combinatorics",
    " enumeration ": "Combinatorics",
    " permutations ": "Combinatorics",
    " combinations ": "Combinatorics",
    " graph theory ": "Combinatorics",
    " coloring ": "Combinatorics",
    " discrete math ": "Combinatorics",

    # Applied Mathematics
    " applied mathematics ": "Applied Mathematics",
    " applied math ": "Applied Mathematics",
    " mathematical physics ": "Applied Mathematics",
    " modelling ": "Applied Mathematics",
    " modeling ": "Applied Mathematics",
    " numerical methods ": "Applied Mathematics",
    " fluid dynamics ": "Applied Mathematics",
    " mechanics ": "Applied Mathematics",
    " simulations ": "Applied Mathematics",
    " optimization ": "Applied Mathematics",
    " engineering mathematics ": "Applied Mathematics",
}

def detect_math_areas(text, keyword_map):
    if not text:
        return [], []

    text_clean = text.replace("\n", " ").strip()
    sentences = re.split(r'(?<=[.?!])\s+', text_clean)

    detected_areas = set()
    log_entries = []

    for sentence in sentences:
        sentence_lower = sentence.lower()
        for keyword, area in keyword_map.items():
            if keyword in sentence_lower:
                detected_areas.add(area)
                log_entries.append((keyword, area, sentence.strip()))

    return sorted(detected_areas), log_entries

# Limpa log antigo se houver
if os.path.exists(LOG_PATH):
    os.remove(LOG_PATH)

with open(LOG_PATH, 'w', encoding='utf-8') as log_file:
    for filename in os.listdir(INPUT_DIR):
        if not filename.endswith(".json"):
            continue
        
        if filename == 'index.json':
            continue

        input_path = os.path.join(INPUT_DIR, filename)
        output_path = os.path.join(OUTPUT_DIR, filename)

        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        print(f"📄 Processando: {filename} - Nome: {data.get('nome_completo', 'N/A')}")  # <- Linha adicionada

        biography = data.get("biografia", "")
        math_areas, log_entries = detect_math_areas(biography, KEYWORDS_MAP)
        data["math_areas"] = math_areas

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        if log_entries:
            log_file.write(f"\n📄 {filename}\n")
            for keyword, area, sentence in log_entries:
                log_file.write(f"- Palavra-chave: '{keyword}' ➝ Área: '{area}'\n")
                log_file.write(f"  Frase: {sentence}\n")

print(f"✅ Biografias processadas. Verifique o log em: {LOG_PATH}")