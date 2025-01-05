from bs4 import BeautifulSoup as bs
import requests
import pandas as pd
import numpy as np
import re
import tqdm
output_folder="output"
failed=[]
def createfile(url,url_id):
    response=requests.get(url)
    if response.status_code!=200:
        print("404 error in "+url_id)
        return False
    doc=bs(response.text,'html.parser')
    try:
        text=doc.find('h1',class_="entry-title").get_text(separator=' ', strip=True)
    except:
        failed.append(url)
        return False
    try:
        text+=" "+doc.find('div',class_="td-post-content tagdiv-type").get_text(separator=' ', strip=True)
        text=re.sub(r'[^\x00-\x7F]+',' ',text)
        f=open(output_folder+"/"+url_id+".txt","w")
        f.write(text)
        f.close()
    except:
        failed.append(url)

df=pd.read_excel("Input.xlsx")
print("Initial run : ")
for i in tqdm.tqdm(range(len(df))):
    createfile(df.iloc[i,1],df.iloc[i,0])

print("Failed url : (due to element classes)")
for i in failed:
    print(i)

def againCreatefile(url,url_id):
    response=requests.get(url)
    if response.status_code!=200:
        return False
    doc=bs(response.text,'html.parser')
    try:
        text=doc.find('h1',class_="tdb-title-text").get_text(separator=' ', strip=True)
    except:
        return False
    try:
        text+=" "+doc.find('div',class_="td_block_wrap tdb_single_content tdi_130 td-pb-border-top td_block_template_1 td-post-content tagdiv-type").get_text(separator=' ', strip=True)
        text=re.sub(r'[^\x00-\x7F]+',' ',text)
        f=open(output_folder+"/"+url_id+".txt","w")
        f.write(text)
        f.close()
    except:
        return False

print("\nExtracting failed url with different class : ")
for i in tqdm.tqdm(failed):
    againCreatefile(i,df[df.URL==i].iloc[0,0])

print("DONE !")


