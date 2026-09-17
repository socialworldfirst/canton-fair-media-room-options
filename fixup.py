# -*- coding: utf-8 -*-
import json,os,re,time,urllib.request,urllib.parse
UA={'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/128 Safari/537.36'}
WUA={'User-Agent':'CantonFairVenueBoard/1.0 (research; steven)'}
M=json.load(open('images.json',encoding='utf-8'))
def get(u,h=UA,t=50): return urllib.request.urlopen(urllib.request.Request(u,headers=h),timeout=t).read()
def commons(title):
    for _ in range(4):
        try:
            u=("https://commons.wikimedia.org/w/api.php?action=query&prop=imageinfo&iiprop=url|extmetadata"
               "&iiurlwidth=1600&format=json&titles="+urllib.parse.quote("File:"+title))
            p=list(json.loads(get(u,WUA,30))['query']['pages'].values())[0]
            ii=p['imageinfo'][0]; em=ii.get('extmetadata',{})
            g=lambda k: re.sub('<[^>]+>','',em.get(k,{}).get('value','')).strip()
            return {'url':ii.get('thumburl') or ii['url'],'title':title.rsplit('.',1)[0].replace('_',' '),
                    'credit':g('Artist') or 'Wikimedia Commons','lic':g('LicenseShortName') or 'CC / PD',
                    'src':'Wikimedia Commons','page':'https://commons.wikimedia.org/wiki/File:'+urllib.parse.quote(title)}
        except Exception: time.sleep(4)
    return None
DROP={'intercon':['Jumbo'],'media-port':['Treaty port'],'canton-tower':['Baltimore'],
      'party-pier':['Mexican'],'courtyard':['Mandarin Oriental'],'ali-center':['Fortune Global'],
      'area-d':['Cycling Race']}
ADD={
 'press-centre':['Aerial View, Canton Fair Complex 20230701-A.jpg'],
 'area-d':['Aerial View, Zone B, Canton Fair Complex 20230701-C.jpg','Aerial View, Canton Fair Complex 20230701-C.jpg'],
 'courtyard':['Canton Fair Complex and Canton Fair Building.jpg','GZ Shenzhen to GZ Guangzhou interCity Tour bus view 廣州 Guangzhou 海珠區 Haizhu District 琶洲街道 Pazhou 1407pm September 2024 R12S 46.jpg'],
 'intercon':['Poly World Trade Center Exterior 20230726.jpg'],
 'sourcing-centre':['GZ Shenzhen to GZ Guangzhou interCity Tour bus view 廣州 Guangzhou 海珠區 Haizhu District 琶洲街道 Pazhou 1417pm September 2024 R12S 06.jpg'],
 'media-port':['Guangzhou TV HQ.jpg','Canton Tower Pearl River TV Station 20210518.jpg','Guangzhou International Media Arbour 20221002-01.jpg'],
 'canton-tower':['Canton Tower Light Show 20240712 02.jpg'],
 'party-pier':['珠江琶醍街区入口.jpg','Party Pier Station Surface.jpg'],
 'ali-center':['Guangzhou Pazhou Poly Plaza.jpg'],
}
for vid,pats in DROP.items():
    M[vid]=[s for s in M[vid] if not any(p.lower() in (s.get('title','') or '').lower() for p in pats)]
for vid,titles in ADD.items():
    for t in titles:
        if len(M[vid])>=3: break
        c=commons(t)
        if not c: print("  miss",t[:40]); continue
        try:
            data=get(c['url'])
            if len(data)<20000: continue
        except Exception as ex: print("  dl fail",t[:40],ex); continue
        fn='img/%s-%d.jpg'%(vid,len(M[vid])+1)
        open(fn,'wb').write(data); c['file']=fn; M[vid].append(c)
        time.sleep(1.0)
# renumber files so order is stable
for vid,lst in M.items():
    for i,s in enumerate(lst,1):
        want='img/%s-%d.jpg'%(vid,i)
        if s['file']!=want:
            os.replace(s['file'],want+'.tmp'); s['file']=want+'.tmp'
    for s in lst:
        if s['file'].endswith('.tmp'):
            os.replace(s['file'],s['file'][:-4]); s['file']=s['file'][:-4]
json.dump(M,open('images.json','w'),ensure_ascii=False,indent=1)
for k,v in M.items(): print(k,len(v),'|',' / '.join((s.get('title') or '')[:34] for s in v))
