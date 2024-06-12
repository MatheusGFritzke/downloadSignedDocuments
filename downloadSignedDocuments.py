import os
import requests
import json
from multiprocessing import Process
from concurrent.futures import ThreadPoolExecutor

download_folder = "documentos-lisodontologia"
os.makedirs(download_folder, exist_ok=True)

def download_document(document, headers, download_folder):
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
            documentName = os.path.join(download_folder, f"{document['patientName']}-{document['eSignatureId']}.pdf")
            if newEditor or digitalSignature:
                intarray = response.json().get('data', [])
                with open(documentName, "wb") as file:
                    for i in intarray:
                        file.write(i.to_bytes(1, byteorder='big'))
            else:
                intarray = response.content
                with open(documentName, "wb") as file:
                    file.write(intarray)
            print(f"Download do arquivo {documentName} concluído com sucesso!")
        else:
            print(f"Falha ao baixar o arquivo para o código {document['eSignatureId']}. Status code: {response.status_code}")

    except Exception as e:
        print(f"Erro durante a execução: {e}")

def download_documents(file_name):
    with open(file_name, 'r') as f:
        documentList = json.load(f)

    with open("token.txt", "r") as file:
        token = file.read().strip()

    headers = {"Authorization": f"Bearer {token}"}
    total_files = len(documentList)

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(download_document, document, headers, download_folder) for document in documentList]
        for future in futures:
            try:
                future.result()
            except Exception as e:
                print(f"Erro no download: {e}")

    print(f"\nTodos os arquivos foram baixados do {file_name}. Total de arquivos: {total_files}")

if __name__ == '__main__':
    files = ["documentDownload_1.json"]

    processes = []
    for file_name in files:
        p = Process(target=download_documents, args=(file_name,))
        processes.append(p)
        p.start()

    for p in processes:
        p.join()

    print("Todos os downloads foram concluídos.")
