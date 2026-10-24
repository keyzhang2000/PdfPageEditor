import os, time, tempfile
os.environ["QT_QPA_PLATFORM"]="offscreen"
import pymupdf as fitz
from PySide6.QtWidgets import QApplication
import sys; sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from frontend import main_window as A
d=tempfile.mkdtemp(); p=os.path.join(d,"big.pdf")
doc=fitz.open()
for i in range(500):
    pg=doc.new_page(); pg.insert_text((72,72),f"P{i}")
doc.save(p)
qa=QApplication([]); w=A.MainWindow(); w.load_pdf(p)
t=time.time(); 
for i in (3,50,120,200): w.list.item(i).setSelected(True)
w.delete_selected(); print("delete", round(time.time()-t,3))
t=time.time(); w._write(p); w.saver.wait()
while w.saver: qa.processEvents()
print("save", round(time.time()-t,3), w.docs[0].page_count)
