import requests
import shutil
import os
import sys
from bs4 import BeautifulSoup as bs
from zipfile import ZipFile
from tqdm import tqdm

class Name:
    PROVIDER = "http://www.mangareader.net/"


    def __init__(self, mangaName="", chapterNum="", lastChapter=""):
        self.mangaName = mangaName
        self.chapterNum = chapterNum
        self.lastChapter = lastChapter

    @property
    def mangaName(self):
        return self.__mangaName
    @mangaName.setter
    def mangaName(self, name):
        self.__mangaName = name

    @property
    def chapterNum(self):
        return self.__chapterNum
    @chapterNum.setter
    def chapterNum(self, num):
        self.__chapterNum = num

    @property
    def lastChapter(self):
        return self.__lastChapter
    @lastChapter.setter
    def lastChapter(self, num):
        self.__lastChapter = num


    def get_provider(self):
        return Name.PROVIDER + self.mangaName +"/"+str(self.chapterNum)+"/"

    def get_download_path(self):
        return self.mangaName +"/"+str(self.chapterNum)+"/"

    def __str__(self):
         return "Downloading {},from Chapter {} to chapter {}".format(self.mangaName, self.chapterNum, self.lastChapter)




class Download:

    def add_zeros(self, pageNum):
        zeros = "0" * (3 - len(pageNum))
        return zeros + pageNum


    def send_request(self, url, binary=False):
        try:
            request = requests.get(url, stream=binary)
        except:
            print("Request Error, poor internet connection")
            exit()
        return request


    def download_episode(self, manga):
        pages = []
        current_page = 1
        download_path = manga.get_download_path()


        while True :
            page_url = manga.get_provider() + str(current_page)
            request = self.send_request(page_url)
            raw_html = request.text
            if request.status_code != 200 or not len(raw_html):
                print("DOESNT_EXIST" if not len(raw_html) else "")
                break
            parsed_html = bs(raw_html, "html.parser")
            img_url = parsed_html.find("img", {"id" :"img"}).get("src")
            pages.append(img_url)
            current_page = current_page + 1

        loading = len(pages)
        with tqdm(total=loading) as pbar:
            x=0
            while x < len(pages):
                if not os.path.exists(download_path):
                    os.makedirs(download_path)
                img_name = self.add_zeros(str(x)) + ".jpg"
                img_path = download_path + img_name
                request = self.send_request(pages[x], True)
                with open(img_path, 'wb') as file_path:
                    request.raw.decode_content = True
                    shutil.copyfileobj(request.raw, file_path)
                #print(DOWNLOADING_MESSAGE + str(x))
                pbar.set_description("Chapter {} Page {}".format(manga.chapterNum, x))
                pbar.refresh()
                pbar.update(1)
                x+=1
            pbar.close()



    def episode_zip(self, manga):
        directory = manga.get_download_path()
        file_paths = []
            # crawling through directory and subdirectories
        for root, directories, files in os.walk(directory):
            for filename in files:
            # join the two strings in order to form the full filepath.
                filepath = os.path.join(root, filename)
                file_paths.append(filepath)

        # writing files to a zipfile
        with ZipFile(manga.mangaName+'/'+str(manga.chapterNum)+".zip",'w') as zip:
            # writing each file one by one
            for file in file_paths:
                zip.write(file)



    def download_chapters(self, manga):
        while int(manga.chapterNum) <= int(manga.lastChapter):
            self.download_episode(manga)
            self.episode_zip(manga)
            shutil.rmtree(manga.mangaName+'/'+str(manga.chapterNum))
            manga.chapterNum = int(manga.chapterNum) + 1
        print("Done")





def main():

    manga = Name()
    manga.mangaName  = input("Enter the manga name : ").lower()
    manga.chapterNum, manga.lastChapter = input("Chapters to download : ").split()


    download = Download()
    download.download_chapters(manga)


main()
