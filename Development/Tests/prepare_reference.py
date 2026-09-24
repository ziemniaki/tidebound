from pathlib import Path
import re,zlib
from rubymarshal.reader import loads
here=Path(__file__).resolve().parent
out=here/'engine_reference';out.mkdir(exist_ok=True)
for i,entry in enumerate(loads((here.parent.parent/'Data/Scripts.rxdata').read_bytes())):
    name=re.sub(r'[^A-Za-z0-9_]', '_', str(entry[1]))
    (out/f'{i:03}_{name}.rb').write_text(zlib.decompress(entry[2]).decode('utf-8-sig'))
print('Prepared reference scripts from the project archive.')
