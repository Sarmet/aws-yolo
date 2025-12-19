# Ghid Complet: Markdown în VS Code

Acest document servește drept ghid de instalare pentru extensiile Markdown în VS Code și, simultan, ca o demonstrație a sintaxei Markdown.

## 1. Extensiile Esențiale

Pentru a transforma VS Code dintr-un editor simplu într-o unealtă perfectă pentru documentație, instalează aceste 3 extensii:

### A. **Markdown All in One**
> *Aceasta este obligatorie. Face cam tot ce lipsește din VS Code standard.*

*   **Scurtături:** Selectezi textul, apeși `Ctrl + B` pentru **Bold** sau `Ctrl + I` pentru *Italic*.
*   **Liste automate:** Continuă automat listele când apeși `Enter`.
*   **Cuprins (TOC):** Generează automat un cuprins actualizabil.
*   **Formatare Tabele:** Aliniază perfect coloanele la salvare (`Alt + Shift + F`).

### B. **Markdown Preview Enhanced**
> *Varianta "Pro" a previzualizării standard.*

*   **Estetică:** Arată mult mai bine decât preview-ul default.
*   **Științific:** Suportă formule matematice (LaTeX).
*   **Export:** Poți salva documentul ca PDF sau HTML elegant.
    *   **Cum faci asta:** Deschizi preview-ul extensiei, dai **Click Dreapta** oriunde în pagină, alegi **Chrome (Puppeteer)** și apoi **PDF**.

### C. **Paste Image** (de mushan)
> *inserări imagini cu copy+paste.*

*   **Clasic:** Faci screenshot -> `Ctrl + Alt + V` în VS Code -> Extensia salvează fișierul și pune link-ul automat.

---

## 2. Ghid de Instalare (Pas cu Pas)

1.  Deschide **VS Code**.
2.  Mergi la **Extensions** (bara din stânga, iconița cu 4 pătrățele) sau apasă `Ctrl + Shift + X`.
3.  Caută extensiile după nume (ex: `Markdown All in One`).
4.  Apasă butonul albastru **Install**.

---

## 3. Cheat Sheet & Demonstrație Sintaxă

Mai jos găsești un tabel cu scurtături și exemple vizuale ale elementelor Markdown.

### Tabel de Comenzi Rapide

| Acțiune | Scurtătură / Comandă | Descriere |
| :--- | :---: | :--- |
| **Previzualizare** | `Ctrl + K`, `V` | Deschide panoul de preview în dreapta |
| **Bold** | `Ctrl + B` | Îngroșare text |
| **Italic** | `Ctrl + I` | Înclinare text |
| **Formatare** | `Alt + Shift + F` | Aranjează tabelele și listele |
| **Imagine** | `Ctrl + Alt + V` | Lipește imaginea din clipboard |

### Elemente Avansate

#### 1. Blocuri de Cod (Syntax Highlighting)
Markdown suportă evidențierea sintaxei.
-de exemplu pentru Python, începi blocul cu ` ```python ` și îl termini cu ` ``` `:

```python
# Exemplu de cod Python
def salut(nume):
    return f"Salut, {nume}!"

print(salut("coae"))
```


#### 2. Task Lists (Liste de sarcini)
Foarte utile pentru TODO-uri:
- [x] Instalează VS Code
- [x] Instalează extensiile recomandate
- [ ] Scrie prima documentație
- [ ] Exportă în PDF

#### 3. Formule Matematice (LaTeX)
Dacă folosești *Markdown Preview Enhanced*, poți scrie formule complexe:

**Inline:** $E = mc^2$

**Block:**
$$
\sum_{i=1}^{n} i = \frac{n(n+1)}{2}
$$

#### 4. Citate și Callouts
> "Documentația este scrisoarea de dragoste pe care o scrii viitorului tău eu."
> — *Un programator înțelept*

#### 5. Link-uri și Imagini
Poți insera [link-uri către Google](https://google.com) sau imagini (dacă ai extensia *Paste Image*, e doar un shortcut distanță).

![Exemplu Imagine Placeholder](https://via.placeholder.com/468x60?text=Imagine+Demonstrativa+Markdown)

---

## 4. Meta-Documentație (Cum am scris acest fișier)

Pentru a crea acest fișier, am folosit următoarele elemente de sintaxă Markdown:

*   `#`, `##`, `###` pentru **Titluri** (ierarhie).
*   `**text**` pentru **Bold** și `*text*` pentru *Italic*.
*   `> text` pentru **Citate**.
*   `---` pentru **Linii orizontale** (delimitatori).
*   `| coloana 1 | coloana 2 |` pentru **Tabele**.
*   ` ```limbaj ` pentru **Blocuri de cod**.
*   `[Text](link)` pentru **Hyperlink-uri**.
*   `![Alt text](cale/imagine)` pentru **Imagini**.
*   `$$ formula $$` pentru **Matematică**.
