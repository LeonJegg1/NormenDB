from transformers import AutoModel, AutoTokenizer
import os

tokenizer = AutoTokenizer.from_pretrained('ucaslcl/GOT-OCR2_0', trust_remote_code=True)
model = AutoModel.from_pretrained('ucaslcl/GOT-OCR2_0', trust_remote_code=True, low_cpu_mem_usage=True, device_map='cuda', use_safetensors=True, pad_token_id=tokenizer.eos_token_id)
model = model.eval().cuda()

# Pfad zum Ausgabeordner
output_folder = './imageOut'

# For-Schleife, die alle Dateinamen im Ordner durchläuft
for filename in os.listdir(output_folder):
    # Nur Dateien zurückgeben (keine Unterordner)
    if os.path.isfile(os.path.join(output_folder, filename)):
        res = model.chat(tokenizer, f'./{output_folder}/{filename}', ocr_type='ocr')
        print(res,'\n\n')
