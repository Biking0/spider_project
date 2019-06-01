a = []

for line in open("js_key.txt"):
    line_str = line.replace('\\\\', '\\').replace(' ', '').replace('\n', '')
    a.append(line_str)

print(a[57])
print(a[144])
print(a[278])
print(a[438])
print(a[506])
print(a[633])

