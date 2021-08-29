# -*- coding: utf-8 -*-

jstr = u"昏"

print(jstr.encode('iso-2022-jp'))
print(jstr.encode('euc-jp'))
print(jstr.encode('euc-jisx0213'))
print(jstr.encode('euc-jis-2004'))
print(jstr.encode('iso-2022-jp'))
print(jstr.encode('iso-2022-jp-1'))
print(jstr.encode('iso-2022-jp-2'))
print(jstr.encode('iso-2022-jp-3'))
print(jstr.encode('iso-2022-jp-ext'))
print(jstr.encode('iso-2022-jp-2004'))
print()
print(jstr.encode('utf-7'))
print(jstr.encode('utf-8'))
print(jstr.encode('utf-16'))
print(jstr.encode('utf-16-be'))
print(jstr.encode('utf-16-le'))
print()
print(jstr.encode('cp932'))          #文字化けしない。
print(jstr.encode('shift-jis'))      #文字化けしない。
print(jstr.encode('shift-jisx0213')) #文字化けしない。
print(jstr.encode('shift-jis-2004')) #文字化けしない。