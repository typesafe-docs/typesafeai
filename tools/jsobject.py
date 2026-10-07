"""Tiny parser for the JavaScript object literals used in Mintlify <TypesafeExample example={{...}} /> props."""
import sys,json,re
def unesc(t):
    return t.replace('\\\\n','\n').replace('\\n','\n').replace('\\`','`').replace("\\'","'").replace('\\\\','\\')
def parse(s,i):
    while s[i] in ' \n': i+=1
    c=s[i]
    if c in '`"\'':
        q=c; j=i+1; out=[]
        while s[j]!=q:
            if s[j]=='\\': out.append(s[j:j+2]); j+=2
            else: out.append(s[j]); j+=1
        return unesc(''.join(out)),j+1
    if c=='{':
        d={}; j=i+1
        while True:
            while s[j] in ', \n': j+=1
            if s[j]=='}': break
            if s[j] in '`"\'':
                k,j=parse(s,j)
            else:
                m=re.match(r'([A-Za-z0-9_$]+)',s[j:]); k=m.group(1); j+=m.end()
            while s[j] in ' \n': j+=1
            assert s[j]==':',s[j-20:j+20]; j+=1
            v,j=parse(s,j); d[k]=v
        return d,j+1
    if c=='[':
        l=[]; j=i+1
        while True:
            while s[j] in ', \n': j+=1
            if s[j]==']': break
            v,j=parse(s,j); l.append(v)
        return l,j+1
    m=re.match(r'(null|true|false|-?[0-9.e+-]+)',s[i:])
    return json.loads(m.group(1)),i+m.end()
