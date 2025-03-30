# archivo: parser/yal_parser.py

# Estructura inicial del parser de YALex
def parse_yal_file(filepath):
    """
    Parsea un archivo .yal, extrayendo:
    - encabezado
    - definiciones con let
    - reglas (entrypoint)
    - trailer (opcional)
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    header, lets, rules, trailer = [], {}, [], []
    mode = 'header'
    for line_num, line in enumerate(lines, start=1):
        original_line = line.rstrip('\n')
        line = line.strip()
        print(f"[L{line_num:03}] Modo: {mode:<8} | Línea: {original_line}")

        if not line or line.startswith("(*"):
            continue  # ignorar líneas vacías o comentarios

        if line.startswith('let'):
            mode = 'lets'
        elif line.startswith('rule'):
            mode = 'rules'
        elif line.startswith('{') and not header:
            mode = 'header'
        elif line.startswith('{') and rules:
            mode = 'trailer'

        if mode == 'header' and line.startswith('{'):
            continue
        elif mode == 'header' and line.endswith('}'):
            mode = 'lets'
            continue
        elif mode == 'trailer' and line.startswith('{'):
            continue
        elif mode == 'trailer' and line.endswith('}'):
            break

        if mode == 'header':
            header.append(line)
        elif mode == 'lets' and line.startswith('let'):
            parts = line[4:].split('=')
            if len(parts) == 2:
                ident = parts[0].strip()
                regex = parts[1].strip()
                lets[ident] = regex
                print(f"🔧 LET '{ident}' = {regex}")

        elif mode == 'rules':
            if '{' in line and '}' in line:
                parts = line.split('{')
                raw_regex = parts[0].strip()
                action = parts[1].replace('}', '').strip()

                if raw_regex.startswith('|'):
                    raw_regex = raw_regex[1:].strip()

                # 🛠️ Preservar comillas para el RegexExpander
                regex = raw_regex
                print(f"⚙️  RULE raw='{regex}' | action='{{{action}}}'")
                if regex.startswith("'") and regex.endswith("'"):
                    print(f"📌 Literal detectado en regla: {regex.strip("'")}")
                elif regex.isidentifier():
                    print(f"📌 Regla compuesta o identificador: {regex}")
                rules.append((regex, action))

        elif mode == 'trailer':
            trailer.append(line)

    return {
        'header': header,
        'lets': lets,
        'rules': rules,
        'trailer': trailer
    }
