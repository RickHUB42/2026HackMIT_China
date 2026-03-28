import cv2
import easyocr

reader = easyocr.Reader(
    ['ch_sim', 'en'],
    model_storage_directory='.\\OCR\\Model',
    user_network_directory='.\\OCR\\Network',
    gpu=True
)

def preprocess_image(path):
    img = cv2.imread(path)
    img = cv2.resize(img, None, fx=2.0, fy=2.0, interpolation=cv2.INTER_CUBIC)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    return blurred

def OCR_image(path):
    preprocessed_img = preprocess_image(path)
    
    results = reader.readtext(
        preprocessed_img, 
        adjust_contrast=True, 
        mag_ratio=1.5         
    )
    texts = []
    confidences = []
    for bbox, text, confidence in results:
       #print(f"Text: {text} | Confidence: {confidence:.2f}")
        texts.append(text)
        confidences.append(confidence)
        
OCR_image('test.jpg')