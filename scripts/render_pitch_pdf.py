"""Assemble validated slide renders into a portable PDF (PPTX stays editable)."""
import sys
from pathlib import Path
from reportlab.pdfgen import canvas
root=Path(__file__).resolve().parents[1]
build=Path(sys.argv[1])
slides=sorted(build.glob('slide-*.png'))
if len(slides)!=12:raise ValueError('Expected twelve rendered slides')
c=canvas.Canvas(str(root/'presentation/Final_Pitch.pdf'),pagesize=(960,540))
c.setTitle('AEGIS | Quantum-X final pitch')
for file in slides:c.drawImage(str(file),0,0,width=960,height=540);c.showPage()
c.save()
print('Pitch PDF contains twelve rendered slides; native charts remain in PPTX')
