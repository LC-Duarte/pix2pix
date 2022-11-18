#!/usr/bin/python
# -*- coding: utf-8 -*-
import logging
import sys
#Basic log config
LOG_LEVEL = logging.DEBUG
def setupLogger(name, level = LOG_LEVEL):
    formatter = logging.Formatter(fmt='%(asctime)s %(process)s %(filename)s:%(lineno)d %(levelname)s: %(message)s', datefmt='%Y-%m-%d %I:%M:%S')
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger = logging.getLogger(name)
    logger.setLevel(LOG_LEVEL)
    logger.addHandler(handler)
    return logger

log = setupLogger("main")

import wget
import os
import urllib.parse
import zipfile
import random
import cv2 as cv
import numpy as np
import time
#Download 
#Where to save and unzip
ZIP_NAME = "basesimpsons.zip"
BASE_PATH="datasets"
DECOMPDIR="BaseSimpsons"
OUT_DIR="Bart2Homer"
#Where to download from 
SRC_URL=urllib.parse.unquote('https://github.com/andrehochuli/teaching/raw/main/ComputerVision/Lecture%2008%20-%20Classification/basesimpsons.zip')

TEST_ZIP_NAME="Teste.zip"
TRAIN_ZIP_NAME="Treino.zip"
FILESTOREMOVE = ["lisa", "family", "maggie", "marge"]

DS_SIZE = 500 #Size of output dataset
IMG_SIZE = 128
def download(url, outpath=None):
    """
    wget.download(url, bar=bar_thermometer)
    """
    log.info(f"Downloading {url} ")
    
    cdir = os.getcwd()#Current dir
    #No save path use current
    if outpath == None:
        outpath = cdir
    #Save path provided, make sure it exists and go to it
    else:
        if not os.path.exists(outpath):
            os.makedirs(outpath)
        os.chdir(outpath)
    log.info(f"Saving on {outpath}")
    file_path = wget.download(url, bar=wget.bar_thermometer, )  
    print()
    #return to original dir
    os.chdir(cdir)  
    return os.path.join(outpath, file_path)

def unzip(zippath, decomp_path = os.getcwd()):
    """
    Unzip a file to a target dir
    if no target dir to decompress will use current dir 
    """
    log.info(f"Decompressing {zippath} on {decomp_path}")
    with zipfile.ZipFile(zippath, 'r') as zip_ref:
        zip_ref.extractall(decomp_path)



def definepairs(srcpath, name1, name2, npairs=DS_SIZE):
    """"
    generates a list of random pairs (of paths)
    """
    log.debug("Defining path pairs")
    paths1 = []
    paths2 = []
    output = []
    #Get avalable paths
    for fname in os.listdir(srcpath):
        if fname.startswith(name1):
            paths1.append(fname)
        if fname.startswith(name2):
            paths2.append(fname)
    #generate random pairs
    for i in range(npairs):
        r1 = random.randrange(len(paths1))
        r2 =  random.randrange(len(paths2))
        p1 =os.path.join(srcpath, paths1[r1])
        p2 =os.path.join(srcpath, paths2[r2])
        output.append((p1, p2))

    return output

def run_da(imgs):
    """"
    data augmentation
    """
    #TODO
    pass

def load_pairs(paired_paths, size=(-1,-1)):
    """"
    Loads image pairs according to pairs
    """
    imgs1 = []
    imgs2 = []
    #no std size set
    log.info("Loading  images in pairs")
    for (p1, p2) in paired_paths:
        try:
            i1 = cv.imread(p1)
        except Exception as e:
            log.exception(f"Failed to load {p1}")
            sys.exit(0)
        try:
            i2 = cv.imread(p2)
        except Exception as e:
            log.exception(f"Failed to load {p1}")
            sys.exit(0)
        #apply std size
        if size != (-1,-1):
            i1 = cv.resize(i1, size, interpolation= cv.INTER_LINEAR)
            i2 = cv.resize(i2, size, interpolation= cv.INTER_LINEAR)
        imgs1.append(i1)
        imgs2.append(i2)
    run_da(imgs1)
    run_da(imgs2)
    return list(zip(imgs1, imgs2))    



def generate_paired_image(pairs):
    """"
    Creates a list of images gennerated by concatenating the pairs from the tuple list 'pairs'
    """
    pairedout =[]
    for (img1, img2) in pairs:
        horizontal_concat = np.concatenate((img1, img2), axis=1)
        pairedout.append(horizontal_concat)
    return pairedout

def assemblepairs(srcpath, name1, name2):
    log.info("Assembling pairs")
    #assign pairs
    paired_paths =  definepairs(srcpath, name1, name2)
    for pair in paired_paths[:3]:
        log.debug(pair)
    log.debug("...")

    #load images
    loaded_pairs = load_pairs(paired_paths, (IMG_SIZE, IMG_SIZE))
    #cv.imshow("P00", loaded_pairs[0][0])
    #cv.imshow("P01", loaded_pairs[0][1])
    #k = cv.waitKey(0)
    out = generate_paired_image(loaded_pairs)
    #cv.imshow("P01", out[0])
    #k = cv.waitKey(0)
    return out


def write_dataset(imgs, outpath):
    log.info(f"Createing dataset as {outpath}")
    #make sure outpath exists
    if not os.path.exists(outpath):
            os.makedirs(outpath)
    c =0
    for id, img in enumerate(imgs):
        imgpath = os.path.join(outpath,f"bh{id}.bmp")
        cv.imwrite(imgpath, img)
        c =id
    log.info(f"Dataset {outpath} generated with {c} samples")


def zipdir(path, ziph):
    # ziph is zipfile handle
    for root, dirs, files in os.walk(path):
        for file in files:
            ziph.write(os.path.join(root, file), 
                       os.path.relpath(os.path.join(root, file), 
                                       os.path.join(path, '..')))

def compress_dataset(path, zippath):
    log.info(f"Compressing dataset from {path} as {zippath}")
    with zipfile.ZipFile(zippath, 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipdir(path, zipf)
    log.info(f"{zippath} Generated")

def main():
    log.info(f"Generating paired dataset with {DS_SIZE} samples")
    #compacted src path
    c_srcpath = ""
    decomp_path = os.path.join(BASE_PATH, DECOMPDIR)
    out_path = os.path.join(BASE_PATH, OUT_DIR)
    comp_path = f"{out_path}.zip"
    #Download
    if("-d" in sys.argv):
        c_srcpath = download(SRC_URL, BASE_PATH)
        log.info(f"{c_srcpath} downloaded")
    else:
        log.warning("download not requested, skiping it")
        c_srcpath = os.path.join(BASE_PATH,ZIP_NAME)
    #Unzip
    if("-u" in sys.argv):
        #Unzip and add to dir
        unzip(c_srcpath, decomp_path)
        #Para base TReino e teste exclisivo para trabalho do de vc
        #salva tudo na pasta dos simpoons
        unzip(os.path.join(decomp_path, TEST_ZIP_NAME), decomp_path)
        unzip(os.path.join(decomp_path, TRAIN_ZIP_NAME), decomp_path)
        #remover arquivos não necessários
        for rmfile in FILESTOREMOVE:
            for fname in os.listdir(decomp_path):
                if fname.startswith(rmfile):
                    os.remove(os.path.join(decomp_path, fname))
        os.remove(os.path.join(decomp_path, TEST_ZIP_NAME))
        os.remove(os.path.join(decomp_path, TRAIN_ZIP_NAME))

    else:
        log.warning("unziping not requested, skiping it")
        
    #Assembling pairs
    dsdata = assemblepairs(decomp_path, "bart", "homer")

    #Writing output
    write_dataset(dsdata, out_path )
    compress_dataset(out_path, comp_path)
    


if __name__ == "__main__":
    start = time.time()
    main()
    end = time.time()
    total_time = end - start
    log.info(f"Script finshed in {round(total_time, 4)}s")