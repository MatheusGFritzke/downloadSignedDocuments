documentList = [
  {
    "NewEditor": "X",
    "id": 4527028120715264,
    "patientId": 5550826613768192,
    "documentName": "Contrato Bellas Clínic Estética e Spa ",
    "eSignatureId": "Ce80dao",
    "patientName": "Maria Márcia Pianezzer",
    "fileName": "0f978816-88a2-47eb-a811-43e6733df2a6.document"
  },
]

import os
import requests

download_folder = "documentos-bellasclinic"
os.makedirs(download_folder, exist_ok=True)

total_files = len(documentList)
files_downloaded = 0

with open("token.txt", "r") as file:
        token = file.read().strip()

headers = {"Authorization": f"Bearer {token}"}

for document in documentList:
    newEditor = document.get('NewEditor') == "X"
    digitalSignature = document.get("eDigitalSignatureSigned") == "X"
    
    base_url = ""
    
    if newEditor and not digitalSignature:
        base_url = "https://solution.clinicorp.com/api/digital_certificate/view_document_with_signatures_external"
    elif digitalSignature: 
        base_url = "https://solution.clinicorp.com/api/digital_certificate/download_document"
    else:
        base_url = "https://solution.clinicorp.com/api/esignature/Doc"


    try:
        if newEditor and not digitalSignature:
            data = {"id": document['id'], "multipleSignatures": True}
            response = requests.post(base_url, json=data, headers=headers)
        elif digitalSignature:
            url = f"{base_url}?id={document['id']}"
            response = requests.get(url, headers=headers)
        else: 
            url = f"{base_url}?id={document['eSignatureId']}"
            response = requests.get(url, headers=headers)
        if response.status_code == 200:
            if newEditor or digitalSignature:
                intarray = response.json().get('data', [])
                documentName = os.path.join(download_folder, f"{document['patientName']}-{document['eSignatureId']}.pdf")

                with open(documentName, "wb") as file:
                  for i in intarray:
                    file.write(i.to_bytes(1, byteorder='big'))
            else: 
                intarray = response.content
                documentName = os.path.join(download_folder, f"{document['patientName']}-{document['eSignatureId']}.pdf")
                
                with open(documentName, "wb") as file:
                    file.write(intarray)
            files_downloaded += 1
            print(f"Download do arquivo {documentName} concluído com sucesso! ({files_downloaded}/{total_files} files downloaded)")
        else:
            print(f"Falha ao baixar o arquivo para o código {document['eSignatureId']}. Status code: {response.status_code}")

    except Exception as e:
        print(f"Erro durante a execução: {e}")

print(f"\nTodos os arquivos foram baixados. Total de arquivos: {files_downloaded}/{total_files}")

