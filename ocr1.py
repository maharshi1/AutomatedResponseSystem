from base64 import b64encode
from os import makedirs
from os.path import join, basename
from sys import argv
import json
import requests

ENDPOINT_URL = 'https://vision.googleapis.com/v1/images:annotate'
RESULTS_DIR = 'jsons'
makedirs(RESULTS_DIR, exist_ok=True)

def make_image_data_list(image_filenames):
    img_requests = []
    for imgname in image_filenames:
        with open(imgname, 'rb') as f:
            ctxt = b64encode(f.read()).decode()
            img_requests.append({
                    'image': {'content': ctxt},
                    'features': [{
                        'type': 'TEXT_DETECTION',
                        'maxResults': 1
                    }]
            })
    return img_requests

def make_image_data(image_filenames):
    imgdict = make_image_data_list(image_filenames)
    return json.dumps({"requests": imgdict }).encode()


def request_ocr(api_key, image_filenames):
    response = requests.post(ENDPOINT_URL,
                             data=make_image_data(image_filenames),
                             params={'key': api_key},
                             headers={'Content-Type': 'application/json'})
    return response


if __name__ == '__main__':
    api_key, *image_filenames = argv[1:]
    if not api_key or not image_filenames:
        print("""
            Please supply an api key, then one or more image filenames
            $ python ocr1.py api_key image1.jpg image2.png""")
    else:
        response = request_ocr(api_key, image_filenames)
        if response.status_code != 200 or response.json().get('error'):
            print(response.text)
        else:
            import re
            text = response.json()['responses'][0]['fullTextAnnotation']['text']
            desc = response.json()['responses'][0]['textAnnotations'][0]['description']
            text = re.sub('(\\n)', ' ', text)
            
            # ***THIS IS THE STRING I'M Getting Some variables are Just not extractable eg. A/c Status which is Aue Status in response.
            # and some of the paramerts are not in line e.g. Name, HEMOGLOBIN: Hb, BLOOD ... etc***
            
            # Dr Lal PathLabs34-LPL AMRITSAR5 S.TOWER PLOT NO 59 SHOPNO-4,OPPEN.T HOSPITAL MAJITHA ROADAMRITSAR 143001NameLab No.Aue StatusP14/4/2017 
            # 12:35:00PM14/4/2017 1:10 18PM14/4/2017 4:03:49PMMrs. SANTOSH SHARMACollectedReportedReport Status Finai237698612Age: 62 YearsGender. 
            # FemaleRef By: 
            # SELFBio Ref. IntervaUnitsTest NameHEMOGLOBIN: Hb, BLOODPhotometry)CREATININE, SERUMResultsgid11 50-15.009.106.210 60-1,00Jaffes reuction, IDMS 
            # traceable)End of report
            
            data = {
                'name': r'(M\w+\.\s\w+\s\w+)',
                'lab_no': r'([0-9]{9})',
                'age': r'(?:Age:\s)([0-9]+\s\w+)',
                'gender': r'(?:Gender.\s)(Female|Male)',
                'ac_status': r'(?:A\w+e\sStatus)(\w{1})',
                'ref_by': r'(?:Ref\sBy:\s)(\w+)',
            }
            for k, v in data.items():
                match = re.search(v, text)
                data[k] = match.groups()[0]

            jpath = join(RESULTS_DIR, 'report1' + '.json')
            with open(jpath, 'w') as f:
                    datatxt = json.dumps(data, indent=2)
                    print("Wrote", len(datatxt), "bytes to", jpath)
                    f.write(datatxt)
