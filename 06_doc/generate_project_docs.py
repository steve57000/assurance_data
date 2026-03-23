import csv
import sqlite3
import textwrap
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
DOC_DIR = BASE / '06_doc'
DATA_DIR = BASE / '01_donnees'
SQL_DIR = BASE / '03_sql'
DB_PATH = DOC_DIR / 'analysis_snapshot.sqlite'
RESULTS_PATH = DOC_DIR / 'annexes_chiffrees.txt'


def load_db():
    if DB_PATH.exists():
        DB_PATH.unlink()
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.executescript(
        '''
        CREATE TABLE GEO_SOURCE (
            Code_dep_code_commune TEXT,
            reg_code TEXT,
            reg_nom TEXT,
            aca_nom TEXT,
            dep_nom TEXT,
            com_nom_maj_court TEXT,
            dep_code TEXT,
            dep_nom_num TEXT
        );
        CREATE TABLE REGION (
            reg_code TEXT PRIMARY KEY,
            reg_nom TEXT NOT NULL,
            aca_nom TEXT
        );
        CREATE TABLE DEPARTEMENT (
            dep_code TEXT PRIMARY KEY,
            dep_nom TEXT NOT NULL,
            dep_nom_num TEXT,
            reg_code TEXT NOT NULL REFERENCES REGION(reg_code)
        );
        CREATE TABLE COMMUNE (
            Code_dep_code_commune TEXT PRIMARY KEY,
            com_nom_maj_court TEXT NOT NULL,
            dep_code TEXT NOT NULL REFERENCES DEPARTEMENT(dep_code)
        );
        CREATE TABLE CONTRAT_SOURCE (
            Contrat_ID INTEGER,
            No_voie TEXT,
            B_T_Q TEXT,
            Type_de_voie TEXT,
            Voie TEXT,
            Code_dep_code_commune TEXT,
            Code_postal TEXT,
            Surface INTEGER,
            Type_local TEXT,
            Occupation TEXT,
            Type_contrat TEXT,
            Formule TEXT,
            Valeur_declaree_biens TEXT,
            Prix_cotisation_mensuel INTEGER
        );
        CREATE TABLE CONTRAT (
            Contrat_ID INTEGER PRIMARY KEY,
            No_voie TEXT,
            B_T_Q TEXT,
            Type_de_voie TEXT,
            Voie TEXT,
            Code_dep_code_commune TEXT NOT NULL REFERENCES COMMUNE(Code_dep_code_commune),
            Code_postal TEXT,
            Surface INTEGER NOT NULL,
            Type_local TEXT,
            Occupation TEXT,
            Type_contrat TEXT,
            Formule TEXT,
            Valeur_declaree_biens TEXT,
            Prix_cotisation_mensuel INTEGER
        );
        '''
    )

    for rel_path, table in [('01_donnees/Region+.csv', 'GEO_SOURCE'), ('01_donnees/Contrat+.csv', 'CONTRAT_SOURCE')]:
        with open(BASE / rel_path, newline='', encoding='utf-8-sig') as fh:
            reader = csv.DictReader(fh, delimiter=';')
            cols = reader.fieldnames
            placeholders = ','.join('?' for _ in cols)
            cur.executemany(
                f"INSERT INTO {table} ({','.join(cols)}) VALUES ({placeholders})",
                ([row[c] if row[c] != '' else None for c in cols] for row in reader),
            )

    cur.executescript(
        '''
        INSERT INTO REGION (reg_code, reg_nom, aca_nom)
        SELECT TRIM(reg_code), MIN(TRIM(reg_nom)), MIN(NULLIF(TRIM(aca_nom), ''))
        FROM GEO_SOURCE
        WHERE reg_code IS NOT NULL AND TRIM(reg_code)<>'' AND reg_nom IS NOT NULL AND TRIM(reg_nom)<>''
        GROUP BY TRIM(reg_code);

        INSERT INTO DEPARTEMENT (dep_code, dep_nom, dep_nom_num, reg_code)
        SELECT TRIM(dep_code), MIN(TRIM(dep_nom)), MIN(NULLIF(TRIM(dep_nom_num), '')), MIN(TRIM(reg_code))
        FROM GEO_SOURCE
        WHERE dep_code IS NOT NULL AND TRIM(dep_code)<>'' AND dep_nom IS NOT NULL AND TRIM(dep_nom)<>''
          AND reg_code IS NOT NULL AND TRIM(reg_code)<>''
        GROUP BY TRIM(dep_code);

        INSERT INTO COMMUNE (Code_dep_code_commune, com_nom_maj_court, dep_code)
        SELECT TRIM(Code_dep_code_commune), MIN(TRIM(com_nom_maj_court)), MIN(TRIM(dep_code))
        FROM GEO_SOURCE
        WHERE Code_dep_code_commune IS NOT NULL AND TRIM(Code_dep_code_commune)<>''
          AND com_nom_maj_court IS NOT NULL AND TRIM(com_nom_maj_court)<>''
          AND dep_code IS NOT NULL AND TRIM(dep_code)<>''
        GROUP BY TRIM(Code_dep_code_commune);

        INSERT INTO COMMUNE (Code_dep_code_commune, com_nom_maj_court, dep_code)
        SELECT src.Code_dep_code_commune,
               'COMMUNE A COMPLETER - ' || src.Code_dep_code_commune,
               src.dep_code_calcule
        FROM (
            SELECT DISTINCT TRIM(Code_dep_code_commune) AS Code_dep_code_commune,
                   CASE
                       WHEN TRIM(Code_dep_code_commune) GLOB '97*' OR TRIM(Code_dep_code_commune) GLOB '98*'
                           THEN SUBSTR(TRIM(Code_dep_code_commune),1,3)
                       ELSE SUBSTR(TRIM(Code_dep_code_commune),1,2)
                   END AS dep_code_calcule
            FROM CONTRAT_SOURCE
            WHERE Code_dep_code_commune IS NOT NULL AND TRIM(Code_dep_code_commune)<>''
        ) src
        JOIN DEPARTEMENT d ON d.dep_code = src.dep_code_calcule
        LEFT JOIN COMMUNE c ON c.Code_dep_code_commune = src.Code_dep_code_commune
        WHERE c.Code_dep_code_commune IS NULL;

        INSERT INTO CONTRAT (
            Contrat_ID, No_voie, B_T_Q, Type_de_voie, Voie, Code_dep_code_commune,
            Code_postal, Surface, Type_local, Occupation, Type_contrat, Formule,
            Valeur_declaree_biens, Prix_cotisation_mensuel
        )
        SELECT Contrat_ID, No_voie, B_T_Q, Type_de_voie, Voie, TRIM(Code_dep_code_commune),
               Code_postal, Surface, Type_local, Occupation, Type_contrat, Formule,
               Valeur_declaree_biens, Prix_cotisation_mensuel
        FROM CONTRAT_SOURCE;
        '''
    )
    con.commit()
    return con


def fetch_all(cur, query):
    return cur.execute(query).fetchall()


def profile(cur):
    def one(q):
        return cur.execute(q).fetchone()[0]

    stats = {
        'volumes': cur.execute(
            "SELECT (SELECT COUNT(*) FROM REGION), (SELECT COUNT(*) FROM DEPARTEMENT), (SELECT COUNT(*) FROM COMMUNE), (SELECT COUNT(*) FROM CONTRAT), (SELECT COUNT(*) FROM CONTRAT_SOURCE)"
        ).fetchone(),
        'q1': fetch_all(cur, "SELECT Contrat_ID, Surface FROM CONTRAT WHERE Surface IS NOT NULL ORDER BY Surface DESC LIMIT 5"),
        'q2': one("SELECT ROUND(AVG(Prix_cotisation_mensuel),2) FROM CONTRAT"),
        'q3': fetch_all(cur, "SELECT COALESCE(Valeur_declaree_biens,'Non renseigné'), COUNT(*) AS n FROM CONTRAT GROUP BY Valeur_declaree_biens ORDER BY n DESC"),
        'q4': one("SELECT COUNT(*) FROM CONTRAT c JOIN COMMUNE co ON c.Code_dep_code_commune=co.Code_dep_code_commune JOIN DEPARTEMENT d ON co.dep_code=d.dep_code JOIN REGION r ON d.reg_code=r.reg_code WHERE c.Formule='Integral' AND r.reg_nom='Pays de la Loire'"),
        'q5': fetch_all(cur, "SELECT c.Contrat_ID, c.Type_contrat, c.Formule FROM CONTRAT c JOIN COMMUNE co ON c.Code_dep_code_commune=co.Code_dep_code_commune JOIN DEPARTEMENT d ON co.dep_code=d.dep_code WHERE c.Type_local='Maison' AND d.dep_code='71' ORDER BY c.Contrat_ID"),
        'q6': one("SELECT ROUND(AVG(c.Surface),2) FROM CONTRAT c JOIN COMMUNE co ON c.Code_dep_code_commune=co.Code_dep_code_commune WHERE co.dep_code='75' AND co.com_nom_maj_court LIKE 'PARIS%'"),
        'q7': fetch_all(cur, "SELECT d.dep_code, d.dep_nom, ROUND(AVG(c.Prix_cotisation_mensuel),2) AS avgp FROM CONTRAT c JOIN COMMUNE co ON c.Code_dep_code_commune=co.Code_dep_code_commune JOIN DEPARTEMENT d ON co.dep_code=d.dep_code GROUP BY d.dep_code, d.dep_nom ORDER BY avgp DESC LIMIT 10"),
        'q8': fetch_all(cur, "SELECT co.Code_dep_code_commune, co.com_nom_maj_court, COUNT(*) AS n FROM CONTRAT c JOIN COMMUNE co ON c.Code_dep_code_commune=co.Code_dep_code_commune GROUP BY co.Code_dep_code_commune, co.com_nom_maj_court HAVING COUNT(*)>=150 ORDER BY n DESC"),
        'q9': fetch_all(cur, "SELECT r.reg_code, r.reg_nom, COUNT(*) AS n FROM CONTRAT c JOIN COMMUNE co ON c.Code_dep_code_commune=co.Code_dep_code_commune JOIN DEPARTEMENT d ON co.dep_code=d.dep_code JOIN REGION r ON d.reg_code=r.reg_code GROUP BY r.reg_code, r.reg_nom ORDER BY n DESC"),
        'missing_codes': fetch_all(cur, "SELECT DISTINCT cs.Code_dep_code_commune FROM CONTRAT_SOURCE cs LEFT JOIN GEO_SOURCE g ON g.Code_dep_code_commune = TRIM(cs.Code_dep_code_commune) WHERE cs.Code_dep_code_commune IS NOT NULL AND TRIM(cs.Code_dep_code_commune)<>'' AND g.Code_dep_code_commune IS NULL ORDER BY 1"),
        'type_local': fetch_all(cur, "SELECT Type_local, COUNT(*) FROM CONTRAT GROUP BY Type_local ORDER BY 2 DESC"),
        'occupation': fetch_all(cur, "SELECT Occupation, COUNT(*) FROM CONTRAT GROUP BY Occupation ORDER BY 2 DESC"),
        'formule': fetch_all(cur, "SELECT Formule, COUNT(*) FROM CONTRAT GROUP BY Formule ORDER BY 2 DESC"),
        'type_contrat': fetch_all(cur, "SELECT Type_contrat, COUNT(*) FROM CONTRAT GROUP BY Type_contrat ORDER BY 2 DESC"),
    }
    return stats


class PDFWriter:
    def __init__(self, path, title):
        self.path = Path(path)
        self.title = title
        self.pages = []
        self.current = []
        self.page_no = 0
        self.width = 595
        self.height = 842
        self.margin = 48
        self.y = self.height - self.margin
        self.fonts = {'regular': 'F1', 'bold': 'F2', 'mono': 'F3'}
        self.add_page()

    def esc(self, text):
        return text.replace('\\', '\\\\').replace('(', '\\(').replace(')', '\\)')

    def add_page(self):
        if self.current:
            self.pages.append('\n'.join(self.current))
        self.current = []
        self.page_no += 1
        self.y = self.height - self.margin
        self.current.append('0.95 0.97 1 rg 0 0 595 842 re f')
        self.current.append('0.15 0.24 0.43 RG 0.15 0.24 0.43 rg 36 792 523 18 re f')
        self.text(48, 805, self.title, 10, 'bold', color=(1, 1, 1))
        self.text(520, 805, str(self.page_no), 10, 'bold', color=(1, 1, 1), align='right')
        self.y = 770

    def ensure(self, needed):
        if self.y - needed < 50:
            self.add_page()

    def text(self, x, y, text, size=11, font='regular', color=(0.1, 0.1, 0.1), align='left'):
        safe = self.esc(text)
        r, g, b = color
        cmd = [f'BT /{self.fonts[font]} {size} Tf {r:.3f} {g:.3f} {b:.3f} rg']
        if align == 'right':
            approx = len(text) * size * 0.5
            x = x - approx
        cmd.append(f'1 0 0 1 {x:.1f} {y:.1f} Tm ({safe}) Tj ET')
        self.current.append(' '.join(cmd))

    def paragraph(self, text, size=11, leading=15, font='regular', color=(0.12, 0.12, 0.12), bullet=None):
        width = 92 if size <= 11 else 80
        wrapper = textwrap.TextWrapper(width=width, break_long_words=False, replace_whitespace=False)
        lines = wrapper.wrap(text)
        if not lines:
            lines = ['']
        self.ensure(len(lines) * leading + 6)
        x = self.margin
        for idx, line in enumerate(lines):
            prefix = ''
            if bullet and idx == 0:
                prefix = bullet + ' '
            elif bullet:
                prefix = '  '
            self.text(x, self.y, prefix + line, size, font, color)
            self.y -= leading
        self.y -= 4

    def heading(self, text, level=1):
        size = 20 if level == 1 else 15 if level == 2 else 12
        leading = 24 if level == 1 else 18 if level == 2 else 15
        color = (0.12, 0.24, 0.45) if level <= 2 else (0.18, 0.18, 0.18)
        self.ensure(leading + 10)
        self.text(self.margin, self.y, text, size, 'bold', color)
        self.y -= leading

    def codeblock(self, code, size=8, leading=11):
        lines = code.splitlines()
        height = len(lines) * leading + 16
        self.ensure(height)
        top = self.y + 4
        self.current.append(f'0.93 0.95 0.98 rg 44 {self.y - height + 8:.1f} 507 {height:.1f} re f')
        self.current.append(f'0.72 0.78 0.88 RG 44 {self.y - height + 8:.1f} 507 {height:.1f} re S')
        y = self.y - 10
        for line in lines:
            self.text(56, y, line[:110], size, 'mono', color=(0.12, 0.12, 0.12))
            y -= leading
        self.y -= height + 8

    def table(self, headers, rows, col_widths=None, size=9, leading=12):
        if col_widths is None:
            col_widths = [80] * len(headers)
        total_h = (len(rows) + 1) * leading + 12
        self.ensure(total_h)
        x = 44
        y_top = self.y
        self.current.append(f'0.84 0.90 0.98 rg {x} {y_top - total_h + 6:.1f} 507 {total_h:.1f} re f')
        self.current.append(f'0.30 0.44 0.67 RG {x} {y_top - total_h + 6:.1f} 507 {total_h:.1f} re S')
        x_pos = x
        for i, h in enumerate(headers):
            self.text(x_pos + 6, y_top - 12, h, size, 'bold', color=(0.08, 0.18, 0.35))
            x_pos += col_widths[i]
        self.current.append(f'0.30 0.44 0.67 RG {x} {y_top - 18:.1f} 507 0 re S')
        y = y_top - 24
        for row in rows:
            x_pos = x
            for i, cell in enumerate(row):
                txt = str(cell)
                self.text(x_pos + 6, y, txt[:max(8, int(col_widths[i] / 5.5))], size, 'regular')
                x_pos += col_widths[i]
            y -= leading
        self.y -= total_h + 8

    def placeholder(self, title, subtitle='Capture à intégrer dans la version finale du rendu', height=120):
        self.ensure(height + 24)
        y0 = self.y - height
        self.current.append(f'0.98 0.98 0.98 rg 44 {y0:.1f} 507 {height:.1f} re f')
        self.current.append(f'0.55 0.55 0.55 RG 44 {y0:.1f} 507 {height:.1f} re S')
        self.current.append(f'0.70 0.70 0.70 RG 44 {y0:.1f} 507 {height:.1f} re S')
        self.current.append(f'0.70 0.70 0.70 RG 44 {y0:.1f} 507 {height:.1f} re S')
        self.current.append(f'0.75 0.75 0.75 RG 44 {y0:.1f} m 551 {self.y:.1f} l S')
        self.current.append(f'0.75 0.75 0.75 RG 44 {self.y:.1f} m 551 {y0:.1f} l S')
        self.text(64, self.y - 24, title, 14, 'bold', color=(0.25, 0.25, 0.25))
        self.text(64, self.y - 44, subtitle, 10, 'regular', color=(0.35, 0.35, 0.35))
        self.y = y0 - 18

    def save(self):
        if self.current:
            self.pages.append('\n'.join(self.current))
            self.current = []
        objects = []
        objects.append('<< /Type /Catalog /Pages 2 0 R >>')
        kids = ' '.join(f'{3 + i*2} 0 R' for i in range(len(self.pages)))
        objects.append(f'<< /Type /Pages /Count {len(self.pages)} /Kids [{kids}] >>')
        font_obj_start = 3 + len(self.pages) * 2
        for i, content in enumerate(self.pages):
            page_id = 3 + i * 2
            content_id = page_id + 1
            page = f'<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Resources << /Font << /F1 {font_obj_start} 0 R /F2 {font_obj_start+1} 0 R /F3 {font_obj_start+2} 0 R >> >> /Contents {content_id} 0 R >>'
            objects.append(page)
            encoded = content.encode('cp1252', errors='replace')
            objects.append(f'<< /Length {len(encoded)} >>\nstream\n'.encode('ascii') + encoded + b'\nendstream')
        objects.append('<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>')
        objects.append('<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >>')
        objects.append('<< /Type /Font /Subtype /Type1 /BaseFont /Courier >>')

        out = bytearray(b'%PDF-1.4\n%\xe2\xe3\xcf\xd3\n')
        xref = [0]
        for idx, obj in enumerate(objects, start=1):
            xref.append(len(out))
            out.extend(f'{idx} 0 obj\n'.encode('ascii'))
            if isinstance(obj, bytes):
                out.extend(obj)
                out.extend(b'\n')
            else:
                out.extend(obj.encode('cp1252', errors='replace'))
                out.extend(b'\n')
            out.extend(b'endobj\n')
        startxref = len(out)
        out.extend(f'xref\n0 {len(xref)}\n'.encode('ascii'))
        out.extend(b'0000000000 65535 f \n')
        for pos in xref[1:]:
            out.extend(f'{pos:010d} 00000 n \n'.encode('ascii'))
        out.extend(f'trailer\n<< /Size {len(xref)} /Root 1 0 R >>\nstartxref\n{startxref}\n%%EOF'.encode('ascii'))
        self.path.write_bytes(out)


def schema_lines():
    return [
        'REGION (reg_code PK, reg_nom, aca_nom)',
        '    1 ---- n DEPARTEMENT (dep_code PK, dep_nom, dep_nom_num, reg_code FK)',
        '    1 ---- n COMMUNE (Code_dep_code_commune PK, com_nom_maj_court, dep_code FK)',
        '    1 ---- n CONTRAT (Contrat_ID PK, adresse, surface, type_local, occupation,',
        '                      type_contrat, formule, valeur_declaree_biens, prix_cotisation_mensuel,',
        '                      Code_dep_code_commune FK)',
        '',
        'Table tampon d''import : GEO_SOURCE puis CONTRAT_SOURCE pour sécuriser l''intégration CSV.',
    ]


def write_results_text(stats):
    lines = []
    lines.append('ANNEXES CHIFFREES - PROJET SQL ASSURANCE\n')
    lines.append('Volumes :')
    lines.append(f"- REGION={stats['volumes'][0]}, DEPARTEMENT={stats['volumes'][1]}, COMMUNE={stats['volumes'][2]}, CONTRAT={stats['volumes'][3]}, CONTRAT_SOURCE={stats['volumes'][4]}")
    for key in ['q1','q3','q5','q7','q8','q9','missing_codes','type_local','occupation','formule','type_contrat']:
        lines.append(f'\n{key}:')
        for row in stats[key]:
            lines.append(f'- {row}')
    lines.append(f"\nq2 moyenne cotisation: {stats['q2']}")
    lines.append(f"q4 Integral Pays de la Loire: {stats['q4']}")
    lines.append(f"q6 surface moyenne Paris: {stats['q6']}")
    RESULTS_PATH.write_text('\n'.join(lines), encoding='utf-8')


def sql_excerpt(path, start=1, end=999):
    lines = Path(path).read_text(encoding='utf-8').splitlines()
    return '\n'.join(lines[start-1:end])


def build_markdown_sources(stats):
    volumes = stats['volumes']
    top_regions = '\n'.join([f"| {code} | {name} | {n} |" for code, name, n in stats['q9'][:8]])
    top_deps = '\n'.join([f"| {code} | {name} | {avg} |" for code, name, avg in stats['q7']])
    top_communes = '\n'.join([f"| {code} | {name} | {n} |" for code, name, n in stats['q8'][:10]])
    q1_table = '\n'.join([f"| {cid} | {surf} |" for cid, surf in stats['q1']])
    q5_table = '\n'.join([f"| {cid} | {tc} | {form} |" for cid, tc, form in stats['q5']])

    projet = f"""# Projet SQL - document technique

## 1. Contexte et objectif
Ce document synthétise le projet SQL d'analyse de contrats d'assurance habitation à partir de deux sources CSV : un fichier contrat et un référentiel géographique. L'objectif est de construire une base normalisée, charger les données et répondre à des questions métier simples.

## 2. Exploration des données
- Source 1 : `Contrat+.csv` avec {volumes[4]} lignes chargées dans `CONTRAT_SOURCE`.
- Source 2 : `Region+.csv` transformée en {volumes[0]} régions, {volumes[1]} départements et {volumes[2]} communes.
- Points d'attention : codes INSEE texte, valeurs catégorielles, 3 codes de communes absents du référentiel (`97434`, `97460`, `97470`).

### Zone capture 1
> Insérer ici une capture du dictionnaire des données Excel complété.

## 3. Schéma relationnel modifié
Le modèle final suit la chaîne `REGION -> DEPARTEMENT -> COMMUNE -> CONTRAT` et s'appuie sur une table tampon `GEO_SOURCE` ainsi qu'une table technique `CONTRAT_SOURCE` pour sécuriser l'import.

### Zone capture 2
> Insérer ici la capture du schéma relationnel modifié dans SQL Power Architect.

## 4. Code SQL générant les tables
Le script principal est `03_sql/01_create_tables.sql`. Les tables tampon et les scripts d'alimentation complètent la création.

```sql
{sql_excerpt(SQL_DIR / '01_create_tables.sql', 1, 70)}
```

## 5. Base chargée
Les volumes chargés sont les suivants.

| Table | Volume |
|---|---:|
| REGION | {volumes[0]} |
| DEPARTEMENT | {volumes[1]} |
| COMMUNE | {volumes[2]} |
| CONTRAT | {volumes[3]} |
| CONTRAT_SOURCE | {volumes[4]} |

### Zone capture 3
> Insérer ici une capture de la base de données chargée (vue tables + extrait de données).

## 6. Liste complète des analyses et résultats associés

### Requête 1 - Top 5 des plus grandes surfaces
| Contrat_ID | Surface |
|---|---:|
{q1_table}

### Requête 2 - Prix moyen de la cotisation mensuelle
Résultat : **{stats['q2']} EUR/mois**.

### Requête 3 - Contrats par valeur déclarée des biens
{chr(10).join([f"- {label} : {n}" for label, n in stats['q3']])}

### Requête 4 - Nombre de formules Integral en Pays de la Loire
Résultat : **{stats['q4']} contrats**.

### Requête 5 - Maisons du département 71
| Contrat_ID | Type_contrat | Formule |
|---|---|---|
{q5_table}

### Requête 6 - Surface moyenne à Paris
Résultat : **{stats['q6']} m2**.

### Requête 7 - Top 10 des départements au prix moyen le plus élevé
| Dep | Nom | Prix moyen |
|---|---|---:|
{top_deps}

### Requête 8 - Communes avec au moins 150 contrats
| Code commune | Commune | Contrats |
|---|---|---:|
{top_communes}

### Requête 9 - Nombre de contrats par région
| Reg | Région | Contrats |
|---|---|---:|
{top_regions}

## 7. Méthodologie suivie
1. Lecture des fichiers CSV et exploration des colonnes.
2. Construction du dictionnaire des données.
3. Normalisation en 4 tables métier + tables tampon d'import.
4. Création des scripts SQL, import et contrôle qualité.
5. Exécution des requêtes d'analyse et interprétation des résultats.

## 8. Conclusion
Le projet aboutit à une base relationnelle propre, exploitable et cohérente avec les besoins d'analyse métier. La concentration des contrats en Ile-de-France et la surreprésentation des appartements ressortent nettement.
"""
    (DOC_DIR / 'projet_sql_source.md').write_text(projet, encoding='utf-8')

    presentation = f"""# Présentation projet SQL

## Slide 1 - Contexte
- Analyse de contrats d'assurance habitation.
- Objectif : passer de fichiers CSV à une base relationnelle exploitable.

## Slide 2 - Sources
- Contrats : {volumes[4]} lignes.
- Référentiel géographique : {volumes[2]} communes après normalisation.
- Un dictionnaire de données a été préparé pour typer les colonnes.

## Slide 3 - Modèle de données
- REGION
- DEPARTEMENT
- COMMUNE
- CONTRAT
- Tables tampon : GEO_SOURCE et CONTRAT_SOURCE

## Slide 4 - Import et qualité
- Normalisation du référentiel.
- Ajout automatique de communes techniques pour 3 codes manquants.
- Contrôle des volumes et des valeurs distinctes.

## Slide 5 - Résultats clés
- Cotisation moyenne : {stats['q2']} EUR.
- Surface moyenne des contrats parisiens : {stats['q6']} m2.
- Formules Integral en Pays de la Loire : {stats['q4']}.

## Slide 6 - Faits marquants
- Ile-de-France : {stats['q9'][0][2]} contrats.
- Paris (75) = département au prix moyen le plus élevé : {stats['q7'][0][2]} EUR.
- 20 communes dépassent 150 contrats.

## Slide 7 - Conclusion
- Base propre.
- Requêtes métier validées.
- Livrables prêts avec emplacements pour captures d'écran.
"""
    (DOC_DIR / 'presentation_projet_sql_source.md').write_text(presentation, encoding='utf-8')

    oral = f"""# Script oral complet

Bonjour, je vais vous présenter notre projet SQL consacré à l'analyse de contrats d'assurance habitation.

Dans un premier temps, nous avons étudié les deux fichiers sources. Le fichier `Contrat+.csv` contient {volumes[4]} contrats avec des informations d'adresse, de surface, de formule et de cotisation. Le fichier `Region+.csv` joue le rôle de référentiel géographique et nous a permis de relier chaque contrat à une commune, un département et une région.

Ensuite, nous avons construit le dictionnaire des données. Cette étape nous a permis de qualifier chaque colonne, de distinguer les types numériques des variables catégorielles et de repérer les contraintes utiles. Par exemple, `Surface` devient un entier, les codes géographiques restent en texte pour conserver les zéros éventuels, et `Valeur_declaree_biens` est gardée comme une catégorie exploitable en regroupement.

Après cette phase, nous avons modifié le schéma relationnel. Au lieu de conserver toutes les informations dans une seule table, nous avons retenu un modèle normalisé autour de quatre tables principales : `REGION`, `DEPARTEMENT`, `COMMUNE` et `CONTRAT`. Nous avons aussi utilisé `GEO_SOURCE` et `CONTRAT_SOURCE` comme tables tampon d'import. Cette organisation réduit les redondances et rend les jointures plus claires.

Pour le chargement, nous avons créé les tables puis injecté les données du référentiel géographique. Un point important est apparu pendant les contrôles : trois codes de communes du fichier contrat étaient absents du référentiel, à savoir 97434, 97460 et 97470. Pour ne pas bloquer la clé étrangère, nous avons créé des communes techniques rattachées à leur département. Cela permet d'importer l'ensemble des {volumes[3]} contrats sans perdre de données.

Nous avons ensuite réalisé les analyses SQL demandées. Les cinq plus grandes surfaces montent jusqu'à {stats['q1'][0][1]} m2. La cotisation mensuelle moyenne ressort à {stats['q2']} euros. La plupart des contrats appartiennent à la tranche de valeur déclarée `0-25000`, ce qui montre un portefeuille plutôt orienté vers des biens de valeur modérée.

Sur le plan géographique, nous avons compté {stats['q4']} contrats en formule Integral dans la région Pays de la Loire. La surface moyenne des contrats situés à Paris atteint {stats['q6']} m2. Le département où la cotisation moyenne est la plus élevée est Paris, avec {stats['q7'][0][2]} euros. Enfin, la région Ile-de-France concentre {stats['q9'][0][2]} contrats, ce qui en fait de loin la zone la plus représentée dans le jeu de données.

En conclusion, ce projet nous a permis de dérouler une démarche complète : comprendre les données, modéliser la base, charger les fichiers, contrôler la qualité et produire des analyses métier. Les livrables fournis comprennent le document technique, la présentation synthétique et ce script oral, avec les zones clairement identifiées pour insérer les captures d'écran demandées.
"""
    (DOC_DIR / 'script_oral_complet_source.md').write_text(oral, encoding='utf-8')


def build_pdf_documents(stats):
    # projet_sql.pdf
    pdf = PDFWriter(DOC_DIR / 'projet_sql.pdf', 'Projet SQL - document technique')
    pdf.heading('Projet SQL - Assurance habitation', 1)
    pdf.paragraph('Document technique synthétique, structuré pour un rendu professionnel, simple à relire et directement exploitable dans le dossier final. Les zones de capture sont identifiées pour faciliter la finalisation du PDF remis.', 11)
    pdf.paragraph('Périmètre : exploration des données, schéma relationnel modifié, code SQL de création, base chargée, analyses complètes et méthodologie suivie.', 11)

    pdf.heading('1. Exploration des types de données', 2)
    pdf.paragraph('Le projet s''appuie sur deux fichiers sources : le fichier Contrat, orienté métier, et le fichier Région, utilisé comme référentiel géographique. La lecture croisée des colonnes a permis d''établir un dictionnaire des données et de fixer les types SQL adaptés.', 10.5)
    pdf.table(['Jeu de données', 'Colonnes', 'Usage'], [
        ['Contrat+.csv', '14', 'faits métier : logement, client, contrat, prix'],
        ['Region+.csv', '8', 'référentiel géographique pour la normalisation'],
    ], [120, 80, 307])
    pdf.paragraph('Choix de typage : les identifiants et codes géographiques sont conservés en texte, les surfaces et cotisations sont converties en entiers, les modalités comme Formule ou Type_local restent en VARCHAR pour l''analyse.', 10.5)
    pdf.placeholder('Zone capture 1 - Dictionnaire des données', 'Insérer une capture de l''Excel : noms de colonnes, types, tailles et descriptions.', 126)

    pdf.heading('2. Schéma relationnel modifié', 2)
    pdf.paragraph('Le schéma initial a été ajusté afin de respecter une structure normalisée et d''éviter les redondances. La chaîne géographique REGION -> DEPARTEMENT -> COMMUNE porte les dimensions, tandis que CONTRAT contient les faits métier.', 10.5)
    pdf.codeblock('\n'.join(schema_lines()), size=9)
    pdf.paragraph('Deux tables tampon sécurisent l''intégration : GEO_SOURCE pour le référentiel brut et CONTRAT_SOURCE pour l''import des contrats avant contrôle des clés étrangères.', 10.5)
    pdf.placeholder('Zone capture 2 - Schéma relationnel modifié', 'Insérer ici la capture exportée depuis SQL Power Architect.', 132)

    pdf.heading('3. Code SQL générant les tables', 2)
    pdf.paragraph('Le cœur du modèle est créé par le script 01_create_tables.sql. Les clés primaires, clés étrangères et index d''analyse y sont déclarés.', 10.5)
    code = sql_excerpt(SQL_DIR / '01_create_tables.sql', 1, 67)
    pdf.codeblock(code, size=7.7, leading=9.4)

    pdf.heading('4. Chargement de la base et contrôles', 2)
    v = stats['volumes']
    pdf.table(['Table', 'Volume', 'Commentaire'], [
        ['REGION', v[0], 'dimensions régionales normalisées'],
        ['DEPARTEMENT', v[1], 'rattachés à une région'],
        ['COMMUNE', v[2], 'référentiel complet après correction'],
        ['CONTRAT', v[3], 'base finale des contrats'],
        ['CONTRAT_SOURCE', v[4], 'tampon d''import'],
    ], [130, 90, 287])
    missing = ', '.join(c for (c,) in stats['missing_codes'])
    pdf.paragraph(f'Point de qualité identifié : trois codes de communes étaient absents du référentiel d''origine ({missing}). Le script d''import crée des communes techniques pour préserver l''intégrité référentielle sans perdre de contrats.', 10.5)
    pdf.placeholder('Zone capture 3 - Base de données chargée', 'Insérer une capture de la base : tables visibles + extrait de données dans le SGBD.', 126)

    pdf.heading('5. Liste complète des analyses et résultats', 2)
    pdf.paragraph(f'R1. Top 5 des surfaces : {", ".join([f"contrat {cid} = {surf} m2" for cid, surf in stats["q1"]])}.', 10.4)
    pdf.paragraph(f'R2. Prix moyen de la cotisation mensuelle : {stats["q2"]} EUR.', 10.4)
    pdf.paragraph('R3. Répartition par valeur déclarée des biens : ' + '; '.join([f'{label} = {n}' for label, n in stats['q3']]) + '.', 10.4)
    pdf.paragraph(f'R4. Nombre de formules Integral en Pays de la Loire : {stats["q4"]}.', 10.4)
    pdf.paragraph('R5. Maisons du département 71 : ' + '; '.join([f'{cid} / {tc} / {form}' for cid, tc, form in stats['q5']]) + '.', 10.4)
    pdf.paragraph(f'R6. Surface moyenne à Paris : {stats["q6"]} m2.', 10.4)
    pdf.paragraph('R7. Départements au prix moyen le plus élevé : ' + '; '.join([f'{dep} {name} = {avg} EUR' for dep, name, avg in stats['q7'][:6]]) + '.', 10.4)
    pdf.paragraph(f'R8. {len(stats["q8"])} communes ont au moins 150 contrats. Les plus fortes sont ' + '; '.join([f'{name} ({n})' for _, name, n in stats['q8'][:6]]) + '.', 10.4)
    pdf.paragraph('R9. Contrats par région : ' + '; '.join([f'{name} = {n}' for _, name, n in stats['q9'][:8]]) + '.', 10.4)
    pdf.table(['Fait marquant', 'Résultat'], [
        ['Région la plus représentée', f"{stats['q9'][0][1]} ({stats['q9'][0][2]} contrats)"],
        ['Département le plus cher', f"{stats['q7'][0][1]} ({stats['q7'][0][2]} EUR)"],
        ['Surface moyenne Paris', f"{stats['q6']} m2"],
        ['Formule Integral en Pays de la Loire', stats['q4']],
    ], [220, 287])

    pdf.heading('6. Méthodologie suivie', 2)
    for item in [
        'Explorer les CSV et vérifier les valeurs distinctes pour comprendre les variables métier.',
        'Renseigner le dictionnaire des données avec type, taille et description.',
        'Normaliser le modèle relationnel en séparant dimensions géographiques et faits contrat.',
        'Créer les tables, charger les données, puis gérer les écarts de référentiel.',
        'Exécuter les requêtes, interpréter les résultats et préparer les supports de soutenance.',
    ]:
        pdf.paragraph(item, 10.4, bullet='-')
    pdf.paragraph('Cette démarche rend le projet lisible à la fois pour un correcteur technique et pour un public métier, tout en restant compatible avec un oral court.', 10.4)
    pdf.save()

    # presentation
    pres = PDFWriter(DOC_DIR / 'presentation_projet_sql.pdf', 'Présentation projet SQL')
    slides = [
        ('Contexte', ['Analyser des contrats habitation pour produire des indicateurs métier.', 'Passer de fichiers CSV à une base relationnelle propre.', 'Préparer un support simple, carré et pro.']),
        ('Données sources', [f'Contrat+.csv : {v[4]} lignes métier.', f'Region+.csv : référentiel géographique transformé en {v[2]} communes.', 'Dictionnaire des données utilisé comme base de typage.']),
        ('Modélisation', ['4 tables métier : REGION, DEPARTEMENT, COMMUNE, CONTRAT.', '2 tables tampon : GEO_SOURCE, CONTRAT_SOURCE.', 'Modèle conçu pour les jointures et l’analyse géographique.']),
        ('Qualité et import', [f'3 codes de communes manquants corrigés : {missing}.', f'{v[3]} contrats intégrés dans la base finale.', 'Contrôles sur les volumes et les valeurs distinctes.']),
        ('Résultats clés', [f'Cotisation moyenne : {stats["q2"]} EUR.', f'Surface moyenne à Paris : {stats["q6"]} m2.', f'Formules Integral en Pays de la Loire : {stats["q4"]}.']),
        ('Faits marquants', [f'Ile-de-France : {stats["q9"][0][2]} contrats.', f'Paris : département au prix moyen le plus élevé ({stats["q7"][0][2]} EUR).', f'{len(stats["q8"])} communes dépassent 150 contrats.']),
        ('Conclusion', ['Base normalisée et exploitable.', 'Analyses SQL complètes et cohérentes.', 'Support prêt pour l’écrit et l’oral, avec zones de captures.']),
    ]
    for i, (title, bullets) in enumerate(slides):
        if i > 0:
            pres.add_page()
        pres.heading(title, 1)
        for b in bullets:
            pres.paragraph(b, 14, leading=20, bullet='-')
        if i in (1, 2, 3):
            pres.placeholder(f'Emplacement visuel recommandé - slide {i+1}', 'Insérer ici la capture adaptée : dictionnaire, schéma ou base chargée.', 220)
    pres.save()

    oral_pdf = PDFWriter(DOC_DIR / 'script oral complet.pdf', 'Script oral complet')
    oral_pdf.heading('Script oral complet', 1)
    text = (DOC_DIR / 'script_oral_complet_source.md').read_text(encoding='utf-8').splitlines()
    for line in text[2:]:
        if not line.strip():
            oral_pdf.y -= 8
            continue
        oral_pdf.paragraph(line.strip(), 11, leading=16)
    oral_pdf.save()


def main():
    con = load_db()
    stats = profile(con.cursor())
    write_results_text(stats)
    build_markdown_sources(stats)
    build_pdf_documents(stats)
    print('Documents generated in', DOC_DIR)


if __name__ == '__main__':
    main()
