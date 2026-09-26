from pathlib import Path
import re,shutil,tempfile,zlib
from rubymarshal.reader import loads
here=Path(__file__).resolve().parent
out=here/'engine_reference'
# Decode everything before replacing the previous extraction. Reusing the old
# directory can leave two scripts at the same numeric index after an insertion.
with tempfile.TemporaryDirectory(prefix='engine-reference-',dir=here) as temp:
    stage=Path(temp)
    for i,entry in enumerate(loads((here.parent.parent/'Data/Scripts.rxdata').read_bytes())):
        raw_name=entry[1].decode('utf-8') if isinstance(entry[1],bytes) else str(entry[1])
        name=re.sub(r'[^A-Za-z0-9_]', '_', raw_name)
        (stage/f'{i:03}_{name}.rb').write_text(zlib.decompress(entry[2]).decode('utf-8-sig'),encoding='utf-8')
    if out.exists():shutil.rmtree(out)
    stage.rename(out)
print('Prepared reference scripts from the project archive.')
