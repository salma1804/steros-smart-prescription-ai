import re

texte = """PTS, LÉ LE TN: WU Led D SES RS Du H ne ME ape a CRE Sn Er A. S 6 su Le E, N au 4 Qu RTE En C4 né Un Ce fl 75 46 Pa hat 04 er se save Le NE A EN M 4 a 10 4 A Pen ve x cc A z ve w ie CG N6s 40 TP Ua lac S 1V41 0 ne 0 D mes BNP Tap0 4aw S41Y Cp as A8 60 Piralr flol bo d 2 cassmpp 00n fob iyate"""

mots = re.split(r"[\s\-–—|,;\.]+", texte)
mots = [m.strip(".,;:()[]{}\"'") for m in mots]
mots = [m for m in mots if len(m) >= 2]

print(f"Nombre de mots : {len(mots)}")
print(mots)