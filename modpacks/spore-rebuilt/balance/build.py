from pathlib import Path
import zipfile,sys
R=Path(__file__).resolve().parent
out=Path(sys.argv[1]);out.mkdir(parents=True,exist_ok=True)
for scope in ['base','ragnarok']:
    if scope=='ragnarok' and '--ragnarok' not in sys.argv:continue
    name='spore_apotheosis_balance'+('_amr' if scope=='ragnarok' else '')+'-1.0.0.jar'
    with zipfile.ZipFile(out/name,'w',compression=zipfile.ZIP_DEFLATED) as z:
        for p in sorted((R/scope).rglob('*')):
            if p.is_file():z.write(p,p.relative_to(R/scope))
