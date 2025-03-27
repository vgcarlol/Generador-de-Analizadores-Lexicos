class YALParser:
    def __init__(self, yal_code):
        self.yal_code = yal_code
        self.parsed = {
            "header": "",
            "trailer": "",
            "lets": {},
            "rules": [],
            "entrypoint": ""
        }
        self._parse()

    def _parse(self):
        from utils.expand_expression import expand_expression  # integración directa

        lines = self._remove_comments(self.yal_code).splitlines()
        lines = [line.strip() for line in lines if line.strip()]

        i = 0
        in_rule_section = False
        rule_body_lines = []

        while i < len(lines):
            line = lines[i]

            if line.startswith("{") and not self.parsed['header']:
                block, i = self._collect_brace_block(lines, i)
                self.parsed['header'] = "\n".join(block)
                continue

            elif line.startswith("let"):
                ident, expr = self._manual_let_parse(line)
                self.parsed['lets'][ident] = expr

            elif line.startswith("rule"):
                self.parsed['entrypoint'] = self._manual_entrypoint_parse(line)
                in_rule_section = True

            elif in_rule_section:
                if line.startswith("{"):
                    block, i = self._collect_brace_block(lines, i)
                    self.parsed['trailer'] = "\n".join(block)
                    break
                else:
                    rule_body_lines.append(line)

            i += 1

        rules_expanded = self._process_rule_body(rule_body_lines)

        for rule in rules_expanded:
            expanded_pattern = expand_expression(rule["pattern"], self.parsed['lets'])
            self.parsed['rules'].append({"pattern": expanded_pattern, "action": rule["action"]})

    def _remove_comments(self, code):
        result = ""
        in_comment = False
        i = 0
        while i < len(code):
            if not in_comment and code[i:i+2] == "(*":
                in_comment = True
                i += 2
            elif in_comment and code[i:i+2] == "*)":
                in_comment = False
                i += 2
            elif not in_comment:
                result += code[i]
                i += 1
            else:
                i += 1
        return result

    def _collect_brace_block(self, lines, start):
        content = []
        brace_count = 0
        i = start
        while i < len(lines):
            line = lines[i]
            brace_count += line.count("{")
            brace_count -= line.count("}")
            content.append(line)
            i += 1
            if brace_count <= 0:
                break
        return content, i

    def _manual_let_parse(self, line):
        parts = line.split('=', 1)
        ident = parts[0].replace('let', '').strip()
        expr = parts[1].strip()
        return ident, expr

    def _manual_entrypoint_parse(self, line):
        name = ""
        i = 5  # skip 'rule '
        while i < len(line) and (line[i].isalnum() or line[i] == '_'):
            name += line[i]
            i += 1
        return name

    def _process_rule_body(self, lines):
        rules = []
        current = ""
        brace_level = 0
        for line in lines:
            for char in line:
                if char == '{':
                    brace_level += 1
                elif char == '}':
                    brace_level -= 1
                if char == '|' and brace_level == 0:
                    rules.append(current.strip())
                    current = ""
                else:
                    current += char
            current += ' '
        if current.strip():
            rules.append(current.strip())

        parsed_rules = []
        for rule in rules:
            if '{' in rule and '}' in rule:
                pattern = rule.split('{')[0].strip()
                action = rule.split('{', 1)[1].rsplit('}', 1)[0].strip()
                parsed_rules.append({"pattern": pattern, "action": action})
            else:
                parsed_rules.append({"pattern": rule.strip(), "action": ""})

        return parsed_rules

    def get_parsed(self):
        return self.parsed


# Ejemplo de uso:
if __name__ == "__main__":
    with open("./yal/slr-4.yal", encoding="utf-8") as f:
        yal_code = f.read()

    parser = YALParser(yal_code)
    result = parser.get_parsed()

    from pprint import pprint
    pprint(result)
