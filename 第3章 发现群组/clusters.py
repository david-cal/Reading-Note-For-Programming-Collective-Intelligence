from PIL import Image,ImageDraw,ImageFont

def readfile(filename):
  lines=[line for line in open(filename,mode = 'r')]
    
  colnames=lines[0].strip().split('\t')[1:]
  rownames=[]
  data=[]
  for line in lines[1:]:
    p=line.strip().split('\t')
    rownames.append(p[0])
    data.append([float(x) for x in p[1:]])
  return rownames,colnames,data

from math import sqrt
def pearson(v1,v2):
  sum1=sum(v1)
  sum2=sum(v2)
    
  sum1Sq=sum([pow(v,2) for v in v1])
  sum2Sq=sum([pow(v,2) for v in v2])
   
  pSum=sum([v1[i]*v2[i] for i in range(len(v1))])

  num=pSum-(sum1*sum2/len(v1))
  den=sqrt((sum1Sq-pow(sum1,2)/len(v1))*(sum2Sq-pow(sum2,2)/len(v1)))
  if den==0: return 0
    
  return 1.0-num/den

class bicluster:
  def __init__(self,vec,left=None,right=None,distance=0.0,id=None):
    self.left=left
    self.right=right
    self.vec=vec
    self.id=id
    self.distance=distance

def hcluster(rows,distance=pearson):
  distances={}
  currentclustid=-1
    
  clust=[bicluster(rows[i],id=i) for i in range(len(rows))]

  while len(clust)>1:
    lowestpair=(0,1)
    closest=distance(clust[0].vec,clust[1].vec)
        
    for i in range(len(clust)):
      for j in range(i+1,len(clust)):
        if (clust[i].id,clust[j].id) not in distances:
          distances[(clust[i].id,clust[j].id)]=distance(clust[i].vec,clust[j].vec)
        
        d=distances[(clust[i].id,clust[j].id)]
                
        if d<closest:
          closest=d
          lowestpair=(i,j)
         
    mergevec=[
    (clust[lowestpair[0]].vec[i]+clust[lowestpair[1]].vec[i])/2.0
    for i in range(len(clust[0].vec))]
       
    newcluster=bicluster(mergevec,left=clust[lowestpair[0]],
                         right=clust[lowestpair[1]],
                         distance=closest,id=currentclustid)

         
    currentclustid-=1
    del clust[lowestpair[1]]
    del clust[lowestpair[0]]
    clust.append(newcluster)
  return clust[0]

def printclust(clust, labels=None,n=0):
    for i in range(n): print(' '),
    if clust.id<0:
        print('-')
    else:
        if labels==None: print(clust.id)
        else: print(labels[clust.id])
    
    if clust.left!=None: printclust(clust.left,labels=labels,n=n+1)
    if clust.right!=None: printclust(clust.right,labels=labels,n=n+1)

def getheight(clust):
  if clust.left == None and clust.right == None: return 1
  
  return getheight(clust.left)+getheight(clust.right)

def getdepth(clust):
  if clust.left==None and clust.right == None: return 0
  
  return max(getdepth(clust.left),getdepth(clust.right))+clust.distance

def drawdendrogram(clust,labels,jpeg='clusters.jpg'):
  h=getheight(clust)*20
  w=1200
  depth=getdepth(clust)
    
  scaling=float(w-150)/depth

  img=Image.new('RGB',(w,h),(255,255,255))
  draw=ImageDraw.Draw(img)
    
  draw.line((0,h/2,10,h/2),fill=(255,0,0))

  drawnode(draw,clust,10,(h/2),scaling,labels)
  img.save(jpeg,'JPEG')


def drawnode(draw,clust,x,y,scaling,labels):
  if clust.id<0:
    h1=getheight(clust.left)*20
    h2=getheight(clust.right)*20
    top=y-(h1+h2)/2
    bottom=y+(h1+h2)/2
        
    ll=clust.distance*scaling
       
    draw.line((x,top+h1/2,x,bottom-h2/2),fill=(255,0,0))
        
    draw.line((x,top+h1/2,x+ll,top+h1/2),fill=(255,0,0))
        
    draw.line((x,bottom-h2/2,x+ll,bottom-h2/2),fill=(255,0,0))

    drawnode(draw,clust.left,x+ll,top+h1/2,scaling,labels)
    drawnode(draw,clust.right,x+ll,bottom-h2/2,scaling,labels)
  else:
    draw.text((x+5,y-7),labels[clust.id],(0,0,0)) 

def rotatematrix(data):
  newdata=[]
  for i in range(len(data[0])):
    newrow=[data[j][i] for j in range(len(data))]
    newdata.append(newrow)
  return newdata

import random
def kcluster(rows,distance=pearson,k=4):
    ranges=[(min([row[i] for row in rows]), max([row[i] for row in rows])) for i in range(len(rows[0]))]

    clusters=[[random.random()*(ranges[i][1]-ranges[i][0])+ranges[i][0] for i in range(len(rows[0]))] for i in range(k)]

    lastmatches=None
    for t in range(100):
        print('Iteration %d' % t)
        bestmatches=[[] for i in range(k)]
        
        for j in range(len(rows)):
            row=rows[j]
            bestmatch=0
            for i in range(k):
                d=distance(clusters[i],row)
                if d<distance(clusters[bestmatch],row): bestmatch=i
            bestmatches[bestmatch].append(j)

        if bestmatches==lastmatches: break
        lastmatches=bestmatches
        
        for i in range(k):
            avgs=[0.0]*len(rows[0])
            if len(bestmatches[i])>0:
                for rowid in bestmatches[i]:
                    for m in range(len(rows[rowid])):
                        avgs[m]+=rows[rowid][m]
                for j in range(len(avgs)):
                    avgs[j]/=len(bestmatches[i])
                clusters[i]=avgs
        return bestmatches

def tanimoto(v1,v2):
  c1,c2,shr=0,0,0
  
  for i in range(len(v1)):
    if v1[i]!=0:  c1+=1
    if v2[i]!=0:  c2+=1
    if v1[i]!=0 and v2[i]!=0: shr+=1
  return 1.0-(float(shr)/(c1+c2-shr))

def scaledown(data,distance=pearson,rate=0.01):
  n=len(data)
  realdist=[[distance(data[i],data[j]) for j in range(n)] for i in range(0,n)]
  outersum=0.0
  
  loc=[[random.random(),random.random()] for i in range(n)]
  fakedist=[[0.0 for j in range(n)] for i in range(n)]

  lasterror=None
  for m in range(0,1000):
    for i in range(n):
      for j in range(n):
        fakedist[i][j]=sqrt(sum([pow(loc[i][x]-loc[j][x],2) for x in range(len(loc[i]))]))

    grad=[[0.0,0.0] for i in range(n)]
  
    totalerror=0
    for k in range(n):
      for j in range(n):
        if j==k: continue
        errorterm=(fakedist[j][k]-realdist[j][k])/realdist[j][k]
      
        grad[k][0]+=((loc[k][0]-loc[j][0])/fakedist[j][k])*errorterm
        grad[k][1]+=((loc[k][1]-loc[j][1])/fakedist[j][k])*errorterm
      
        totalerror+=abs(errorterm)
    print(totalerror)
 
    if lasterror and lasterror<totalerror: break
    lasterror=totalerror
    
    for k in range(n):
      loc[k][0]-=rate*grad[k][0]
      loc[k][1]-=rate*grad[k][1]
  return loc

def draw2d(data,labels,jpeg='mds2d.jpg'):
    img=Image.new('RGB',(2000,2000),(255,255,255))
    draw=ImageDraw.Draw(img)
    for i in range(len(data)):
        x=(data[i][0]+0.5)*1000
        y=(data[i][1]+0.5)*1000
    
        font = ImageFont.truetype("simsun.ttc",encoding="unic")#注意中文标签要改写为utf-8格式
        draw.text((x,y),labels[i],(0,0,0),font)
    img.save(jpeg,'JPEG')


def draw2d_chn(data, labels, jpeg = 'mds2d.jpg'):
    
   #生成画板
    img =Image.new('RGB',(2000,2000),(255,255,255))#(255,255,255)表示白
    draw = ImageDraw.Draw(img)
    
    for i in range(len(data)):
        #放大坐标系
        x = (data[i][0] + 0.5) * 1000
        y = (data[i][1] + 0.5) * 1000
        
        #画点
        font = ImageFont.truetype("simsun.ttc",encoding="unic")#注意中文标签要改写为utf-8格式
        draw.text((x,y),labels,(0,0,0),font) #(0,0,0)表示黑
        
    img.save(jpeg,'JPEG')
 
