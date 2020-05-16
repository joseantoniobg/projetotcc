from __future__ import division
from time import gmtime, strftime

import cv2
import numpy as np
import ImageEnhance
import Image, ImageOps
import os 
import glob
import shutil
import OCR
import re
import urllib, cStringIO
import time

preto = [
    ([245, 245, 245], [255, 255, 255])
]

DiretorioCameraIP = "http://192.168.43.1:8080/photo.jpg"

def CapImagenm(Imagem):
    
  file = cStringIO.StringIO(urllib.urlopen(DiretorioCameraIP).read())

  img = Image.open(file)
  
  img.save(Imagem + '.jpg');
 
def Contraste(caminho, name):   
    
    img = cv2.imread(caminho)
    cv2.imwrite('Imagens/contraste.jpg', img)
    img2 = cv2.imread(caminho)
    img2 = (255-img2)
    cv2.imwrite('Imagens/contraste2.jpg', img2)
    
    #im2 = Image.open("Imagens/contraste.jpg") #abre a imagem alvo
    #enb = ImageEnhance.Brightness(im2)
    #enb.enhance(2.2).save("Imagens/contraste.jpg", quality=100) #contraste de 750%, salva a imagem    
    
    im3 = Image.open("Imagens/contraste.jpg") #abre a imagem alvo
    enh2 = ImageEnhance.Contrast(im3)
    enh2.enhance(10.5).save("Imagens/contraste.jpg", quality=100) #contraste de 750%, salva a imagem    
      
    img = cv2.imread("Imagens/contraste.jpg") #abre a imagem salva
    cinza = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) #converte em tons de cinza
    cv2.imwrite("Imagens/" + name + "/" + str(name) + ".jpg", cinza) #salva em tons de cinza  
    
    #im2 = Image.open("Imagens/contraste2.jpg") #abre a imagem alvo
    #enb = ImageEnhance.Brightness(im2)
    #enb.enhance(2.2).save("Imagens/contraste2.jpg", quality=100) #contraste de 750%, salva a imagem    
    
    im3 = Image.open("Imagens/contraste2.jpg") #abre a imagem alvo
    enh2 = ImageEnhance.Contrast(im3)
    enh2.enhance(10.5).save("Imagens/contraste2.jpg", quality=100) #contraste de 750%, salva a imagem    
      
    img = cv2.imread("Imagens/contraste2.jpg") #abre a imagem salva
    cinza = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) #converte em tons de cinza
    cv2.imwrite("Imagens/" + name + "/" + str(name) + "2.jpg", cinza) #salva em tons de cinza
    
        
def DetectaCor(caminho, out):
    
    image = cv2.imread(caminho) #abre a imagem com contraste

    image = (255-image)#inverte as cores da imagem 
    
    # abre a lista de cores, no caso ha somente o preto
    for (comeco, final) in preto:
        # cria arrays dessas cores, para podermos ter o intervalo entre elas
        comeco = np.array(comeco, dtype = "uint8")
        final = np.array(final, dtype = "uint8")
     
        # varre a imagem, mantendo somente as cores presentes no intervalo entre o comeco e o fim
        mascara = cv2.inRange(image, comeco, final)
        saida = cv2.bitwise_and(image, image, mask = mascara) #aplica essas cores como uma mascara na imagem original
     
        saida = (255-saida) #inverte novamente as cores da imagem
 
        # grava o resultado em disco
        cv2.imwrite(out, saida)

def Segmentacao(caminho, diretorio):
    
    # cria o direotorio novo para a captura
    try:
        os.stat('Imagens/Cortes/' + diretorio)
    except:
        os.mkdir('Imagens/Cortes/' + diretorio)    
    
    imagem = cv2.imread(caminho) #le a imagem resultante do resultado anterior
    
    peb = cv2.cvtColor(imagem,cv2.COLOR_BGR2GRAY) # tons de cinza
    _,segmentacao = cv2.threshold(peb,150,255,cv2.THRESH_BINARY_INV) # segmentacao threshold
    holding = cv2.getStructuringElement(cv2.MORPH_CROSS,(1,2)) #1 e 2 sao porporcoes de descoberta
    dilated = cv2.dilate(segmentacao, holding, iterations = 2) #dilatacao dos resultados encontrados
    contornos, hierarchy = cv2.findContours(dilated,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE) # gera array de contornos

    media = 0
        
    b = 0

    for cont in contornos: # para cada contorno gerado

        [x,y,w,h] = cv2.boundingRect(cont) #gera um retangulo da area dos contornos
        
        largimg, altimg = imagem.shape[:2]
        
        contorno = int(largimg / 110)
        
        corte = imagem[y:y+h, x:x+w] #gera a imagem de corte com margens de 3 e 4 px
       
        largura, altura = corte.shape[:2] #pega a largura e altura da imagem de corte
    
        if altura == 0: #caso nao haja altura, se atribui 0,001 para evitar divisao por 0
            altura = 0.001
    
        proporcao = largura / altura #gera a proporcao entre largura e altura
        
        min = largimg / 15
    
        #f largura > 30 and proporcao > 1.28 and proporcao < 2.55:
            
        print(str(x + y) + ".jpg " + str(proporcao) + " " + str(largura)) #printa a proporcao e largura da imagem de corte atual

        media = media + altura
        
        if largura > b:
            b = largura

        cv2.imwrite('Imagens/Cortes/' + diretorio + '/' + str(x + y) + '.jpg', corte) #salva imagem de corte
        imag = Image.open('Imagens/Cortes/' + diretorio + '/' + str(x + y) + '.jpg')
        img_borda = ImageOps.expand(imag, border=10,fill='white')
        img_borda.save('Imagens/Cortes/' + diretorio + '/' + str(x + y) + '.jpg')
        #cv2.rectangle(imagem,(x,y),(x+w,y+h),(255,0,255),2)

    print (b)
    
    #cv2.imwrite('Imagens/Cortes/' + diretorio + '/contornos.jpg', imagem) #salva uma copia da imagem contornada
    
    
def TesseractOCR(diretorio):
    
    ocr = OCR.OCR() #cria uma instancia do OCR

    caminho = "Imagens/cortes/" + diretorio #pega a pasta com as imagens de corte
    
    dirList=os.listdir(caminho) #gera um array com as imagens nesse diretorio
    lista = []
    
    placa = ""
    for fname in dirList: #gera uma lista de numeros inteiros (nome das imagens) ja que estes estao na ordem desejada
        if fname.endswith(".jpg"): #verificacao de extrnsao para nao pegar o thumbs.db
            lista.append(int(fname[:len(fname) - 4]))
    
    lista.sort() #ordena a lista
    
    for fname in lista: #para cada numero presente na lista
        
        ocr.executar("Imagens/Cortes/" + diretorio + "/" + str(fname) + ".jpg") #executa o reconhecimento
        caractere = ocr.getTexto() #pega o texto rsultante
        caractere = re.sub('[^A-Z0-9]+', '', caractere) #retira os caracteres especiais, sobrando somente letras maiusculas e numeros   
        #caractere = caractere[:1] #pega somente o promeiro caractere reconhecido
        
        #if caractere == "": #se nao reconheceu nada, substitui o caractere por '1'
        #   caractere = "1"
        
        placa = placa + caractere #soma o caractere ao texto que sera a placa
        print(str(fname) + ".jpg : " + caractere) #printa o que foi reconhecido na imagem
       
    #pega os tres primeiros caracteres, que deverao ser as letras da placa
    #letras = re.sub('[^A-Z]+', '', placa)
    letras = placa[:3]
    
    #substituicao de caracteres ambiguos
    
    letras = letras.replace("0", "O")
    letras = letras.replace("1", "I")
    
    #o restante reconhecido sao os numeros
    #numeros = re.sub('[^0-9]+', '', placa)
    numeros = placa[3:]
    
    #substituicao de caracteres ambiguos
    numeros = numeros.replace("I", "1")
    numeros = numeros.replace("O", "0")
    numeros = numeros.replace("Q", "0")
    numeros = numeros.replace("B", "8")
    numeros = numeros.replace("D", "8")
    numeros = numeros.replace("E", "9")
    
    #pega somente os 4 primeiros caracteres reconhecidos
    
    #concatena as letras e numeros da placa
    placa = letras + numeros
    
    #printa o que foi reconhecido      
    print ("placa: " + placa)

def LimpaDiretorio():
    #deleta todas as imagens de corte
    directory='Imagens/Cortes'
    os.chdir(directory)
    files=glob.glob('*.jpg')
    for filename in files:
        os.unlink(filename)
        
nome = strftime("%Y%m%d%H%M%S", gmtime())

#LimpaDiretorio()    
caminho = "Imagens/Capturas/Carro15.jpg"

print("Contraste")

print(nome)

try:
    os.stat('Imagens/' + nome)
except:
    os.mkdir('Imagens/' + nome) 

Contraste(caminho, nome) #passo 1

print("Detecta Cor") 

DetectaCor("Imagens/" + nome + "/" + nome + ".jpg", "Imagens/" + nome + "/" + nome + "-f.jpg") #passo 2

DetectaCor("Imagens/" + nome + "/" + nome + "2.jpg", "Imagens/" + nome + "/" + nome + "-f2.jpg") #passo 2

print("Segmentacao de Caracteres")

Segmentacao("Imagens/" + nome + "/" + nome + "-f.jpg", nome) #passo 3

Segmentacao("Imagens/" + nome + "/" + nome + "-f2.jpg", nome) #passo 3

print("OCR")

#TesseractOCR(nome) #passo 4
    
    