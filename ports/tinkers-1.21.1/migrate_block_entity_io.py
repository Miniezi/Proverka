"""Thread world registry lookup through block entity persistence lifecycle methods.

Only lifecycle bodies are edited; fluid/item helper APIs remain explicit follow-up work.
"""
import re


def migrate(root):
    changed = []
    methods = 0
    pattern = re.compile(r'(public|protected) (void|CompoundTag) (load|saveAdditional|saveSynced|getUpdateTag)\((?:CompoundTag (\w+))?\)\s*\{')
    for p in (root / 'src/main/java/slimeknights/tconstruct').rglob('*BlockEntity.java'):
        s = p.read_text()
        edits = []
        for m in pattern.finditer(s):
            depth = 1
            end = m.end()
            while depth:
                if s[end] == '{': depth += 1
                elif s[end] == '}': depth -= 1
                end += 1
            name = 'loadAdditional' if m[3] == 'load' else m[3]
            args = (f'CompoundTag {m[4]}, ' if m[4] else '') + 'net.minecraft.core.HolderLookup.Provider registries'
            header = f'{m[1]} {m[2]} {name}({args}) {{'
            body = s[m.end():end]
            body = re.sub(r'super\.load\((\w+)\)', r'super.loadAdditional(\1, registries)', body)
            body = re.sub(r'super\.(saveAdditional|saveSynced)\((\w+)\)', r'super.\1(\2, registries)', body)
            body = body.replace('super.getUpdateTag()', 'super.getUpdateTag(registries)')
            body = re.sub(r'\b(writeInventoryToNBT|readInventoryFromNBT)\((\w+)\)', r'\1(\2, registries)', body)
            edits.append((m.start(), end, header + body))
        if edits:
            for start, end, replacement in reversed(edits): s = s[:start] + replacement + s[end:]
            p.write_text(s)
            changed.append(str(p.relative_to(root)))
            methods += len(edits)
    return {'files': changed, 'lifecycle_methods': methods, 'nested_serializers_complete': False}
