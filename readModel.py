'''
Created on 17 Sep 2015

@author: nut67271
'''

import random,shutil,subprocess
import numpy as np

class Model():
    '''
    classdocs
    '''


    def __init__(self, path):
      '''
      Constructor
      '''
      print(path)
      self.model_path = path
      f = open(path)
      
      self.inModelText= []
      self.model_units = dict()      
      self.inModelText=  f.readlines()
      
      i = -1
      for line in self.inModelText:
        i=i+1
        if line.startswith('INITIAL CONDITIONS'):
          break
        elif line.startswith('RIVER'):
          unit = RiverSection(self.inModelText,i)
          #print(unit.unit_name)
          self.model_units[unit.unit_name]=unit

    def varyAllUnits(self):
      for unit_name in self.model_units:
        self.model_units[unit_name].varyDistNext(0.05)
        self.model_units[unit_name].varyN(0.2)
        self.model_units[unit_name].varyDx(0.1)
        self.model_units[unit_name].varyZ(0.05)
    
    def makeModelText(self):
      for unit_name in self.model_units:
        self.modelText = self.model_units[unit_name].replaceInModelText(self.inModelText)
     
    def writeModelToFile(self,outPath): 
      outf = open( outPath,'w')
      for line in self.modelText:
        outf.write(line)


class RiverSection():
  def __init__(self,inModelText,line_n):
    self.unit_comment = inModelText[line_n][6:-1]
    self.unit_type = inModelText[line_n+1][:-1]  
    self.unit_name = inModelText[line_n+2][:12].replace('\n','') 
    if len(inModelText[line_n+2])>13:
      self.spilll = inModelText[line_n+2][12:24].replace('\n','')    
    if len(inModelText[line_n+2])>25:
      self.spillr = inModelText[line_n+2][24:36].replace('\n','')
    if len(inModelText[line_n+2])>37:
      self.lat1 = inModelText[line_n+2][36:48].replace('\n','')
    if len(inModelText[line_n+2])>25:
      self.lat2 = inModelText[line_n+2][48:60].replace('\n','')      
          
    if inModelText[line_n+1].startswith('SECTION')==False:
      pass  ## not a river section, must be routing

    else:   
      self.distance_to_next = float(inModelText[line_n+3][:10])
      if len(inModelText[line_n+3]) > 20:
        self.gradient = float(inModelText[line_n+3][20:30])
      else:
        self.gradient = None
      self.number_of_rows = int(inModelText[line_n+4][:10])
      
      self.data =dict()
      self.data['dx']=[]
      self.data['z']=[]
      self.data['n']=[]
      self.data['p']=[]
      self.data['rpl']=[]
      self.data['marker']=[]
      self.data['x']=[]
      self.data['y']=[]    
      
      for l in inModelText[line_n+5:line_n+5+self.number_of_rows]:
        self.data['dx'].append(float(l[:10]))
        self.data['z'].append(float(l[10:20]))
        self.data['n'].append(float(l[20:30]))
        self.data['p'].append(l[30:31])
        self.data['rpl'].append(float(l[31:40]))
        self.data['marker'].append(l[40:50])
        self.data['x'].append(float(l[50:60]))
        self.data['y'].append(float(l[60:70])) 
  
  
  def replaceInModelText(self,modelText):
    i = 0
    for line in modelText:
      if line.startswith(self.unit_name):
        line_n = i
        break
      i=i+1
    modelText[line_n-2]='RIVER '+self.unit_comment+'\n'
    modelText[line_n+1]='{:>10}'.format(str(self.distance_to_next))+'{:>20}'.format(str(self.gradient))+'\n'
    
    existing_number_data_rows = int(modelText[line_n+2][:-1])
    del modelText[line_n+3:line_n+3+existing_number_data_rows]
    modelText[line_n+2]='{:>10}'.format(str(len(self.data['dx'])))+'\n'
  
    
    for i in range(len(self.data['dx'])):
      row = '{:>10}'.format(str(self.data['dx'][i]))
      row = row +'{:>10}'.format(str(self.data['z'][i]))
      row = row +'{:>10}'.format(str(self.data['n'][i]))
      row = row +'{:>1}'.format(str(self.data['p'][i]))
      row = row +'{:>9}'.format(str(self.data['rpl'][i]))
      row = row +'{:>10}'.format(str(self.data['marker'][i]))
      row = row +'{:>10}'.format(str(self.data['x'][i]))
      row = row +'{:>10}'.format(str(self.data['y'][i]))
      row = row +'\n'
      modelText.insert(line_n+3+i, row)
    
    return modelText    
    
  
  def varyN(self,sd):
    f = random.normalvariate(1.0,sd)
    for i in range(len(self.data['n'])):
      self.data['n'][i] = round(f*self.data['n'][i],3)
  
  def varyDx(self,sd):
    previous_dx = self.data['dx'][0]-3*sd
    for i in range(len(self.data['dx'])):
      dx = random.normalvariate(0.0,sd)
      new_dx = dx+self.data['dx'][i]
      self.data['dx'][i] = round(max(previous_dx+0.001,new_dx),3)
      previous_dx = self.data['dx'][i]      
        
  def varyZ(self,sd):
      for i in range(len(self.data['z'])):
        self.data['z'][i] = round(random.normalvariate(0.0,sd)+self.data['z'][i],3)          

  def varyDistNext(self,sd):
    if self.distance_to_next !=0:
      self.distance_to_next = round(random.normalvariate(1.0,sd)*self.distance_to_next,3)  

class Ief():
  def __init__(self):   
    self.iefFile = 'None'
    self.datFile = 'None'
    self.runType = 'None'
    self.start = 'None'
    self.finish = 'None'
    self.timestep = 'None'
    self.iCsFrom = ''
    self.icFile = ''
    self.iedFile = 'None'
    self.resultLocation = 'None'
    self.zznFile = 'None'
    self.zzdFile = 'None'
    self.imageFile = 'None'
    self.timestep2D  = 'None'
    self.tcfFile = 'None'
    self.zzdMessage = 'None'

  def readIef(self,path):
    iefFile = open(path)
    self.iefText = list()
    for line in iefFile.readlines():
      self.iefText.append(line[:-1])    
    
  def checkIef(self):
    pass
    
  def writeIef(self,path):
    pass

if __name__=='__main__':
  isisPath=r"C:\isis\bin\isisf32.exe"
  tabCsv=r'C:\isis\bin\Tabularcsv.exe'
  
  tcsPath=r'C:\Projects\Top Street\Model\Test.tcs'
          
  path = r'C:\Projects\Top Street\Model\Test.dat'
  iefPath = r'C:\Projects\Top Street\Model\Test.ief'
  iefFile = open(iefPath)
  iefText = list()
  for line in iefFile.readlines():
    iefText.append(line)
  
  nodeOrder=list()
  nodes = dict()
  
  tcsFile = open(tcsPath,'r')
  inNodes=False
  for line in tcsFile.readlines():
    if inNodes:
      if line.startswith('Count'):
        pass
      else:
        node = line.split('=')[-1][:-1]
        nodeOrder.append(node)
        nodes[node]=list()
        
    
    else:
      if line.startswith('[Nodes]'):
        inNodes = True
  print(nodeOrder)  
  
  
  m = Model(path)
  for ensemble in range(30):
    ensembleIef = r'C:\Projects\Top Street\Model\Test_ensemble'+str(ensemble)+'.ief'
    shutil.copy(iefPath,ensembleIef)
    outPath =r'C:\Projects\Top Street\Model\Test_ensemble'+str(ensemble)+'.dat'
    zznFile=r'C:\Projects\Top Street\Model\Test_ensemble'+str(ensemble)+'.zzn'
    
    iefF = open(ensembleIef,'w')
    for line in iefText:
      iefF.write(line.replace(path,outPath))
    iefF.close()
    
    m.varyAllUnits()
    m.makeModelText()
    m.writeModelToFile(outPath)
    
    isisCode = subprocess.call([isisPath,'-sd',ensembleIef])
    
    
    if isisCode == 1 or isisCode ==  2:
      tabCsvCode = subprocess.call([tabCsv,'-silent','-tcs',tcsPath,zznFile])
      print(ensemble,isisCode,tabCsvCode)
      csvPath = zznFile[:-3]+'csv'
      csvFile = open(csvPath)
      lines = csvFile.readlines()
      for l in lines[6:]:
        entries=l.split(',')
        nodes[entries[0]].append(float(entries[1]))
        
    else:
      print(ensemble,isisCode)
  
  outputPath = 'C:\Projects\Top Street\Model\ensemble_summary.csv'
  outFile = open(outputPath,'w')
      
  for node in nodeOrder:
    outFile.write(node+', ')
    for entry in nodes[node]:
      outFile.write(str(round(entry,3))+', ')
    outFile.write(str(round(np.mean(nodes[node]),3))+', '+str(round(np.std(nodes[node]),3))+'\n')        
