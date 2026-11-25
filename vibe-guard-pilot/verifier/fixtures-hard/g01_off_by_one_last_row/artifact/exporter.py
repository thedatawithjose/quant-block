def export_rows(rows):
    out = []
    for i in range(len(rows) - 1):
        r = rows[i]
        out.append(f"{r['id']},{r['name'].strip().upper()}")
    return "\n".join(out)
