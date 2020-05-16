from pytesser import image_file_to_string

class OCR:
    __texto = ""
    def executar(self, diretorio):
        try:
            self.__texto = image_file_to_string(diretorio)
            return True
        except:
            print()
            return False
        
        
    def getTexto(self):
        return self.__texto