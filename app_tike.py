import os
import streamlit as st
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, VectorParams, Distance
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
from groq import Groq

# โหลด environment variables
load_dotenv()

# เริ่มต้น Qdrant (แบบ In-Memory)
qdrant_client = QdrantClient(":memory:")

# สร้าง Collection สำหรับเก็บเวกเตอร์
qdrant_client.recreate_collection(
    collection_name="documents",
    vectors_config=VectorParams(size=384, distance=Distance.COSINE)
)

# ข้อมูลเอกสารที่กำหนดเอง
documents = [
    "วัดหัวเวียงเหนือ ตำบลฝายแก้ว, ที่อยู่: 123 หมู่ 4 ตำบลฝายแก้ว อำเภอฝายแก้ว จังหวัดน่าน https://maps.app.goo.gl/drwuxr2PwRgcUdrx8 "
    "",
    "วัดศรีมงคล หรือที่รู้จักกันในชื่อ, 'วัดก๋ง' ตำบลยม ที่อยู่: ตำบลยม อำเภอท่าวังผา จังหวัดน่าน https://maps.app.goo.gl/5DrYvwijsjSGDAbm6",
    "วัดภูมินทร์ ตำบลในเวียง, ที่อยู่: 123 หมู่ 4 ตำบลในเวียง อำเภอเมือง จังหวัดน่าน https://maps.app.goo.gl/aJEQKt5WcepTNoGq8",
    "วัดพระธาตุเเช่เเห้ง ตำบลทุ่งช้าง, ที่อยู่: 123 หมู่ 4 ตำบลทุ่งช้าง อำเภอทุ่งช้าง จังหวัดน่าน https://maps.app.goo.gl/tVYpbdar8nveRQ6T6",
    "วัดศรีบุญเรือง ตำบลท่าวังผา, ที่อยู่: 123 หมู่ 4 ตำบลท่าวังผา อำเภอท่าวังผา จังหวัดน่าน https://maps.app.goo.gl/JBHhAEfmTjd7FY2h9",
    "วัดพระธาตุช้างค้ำวรวิหาร ตำบลเมืองน่าน, ที่อยู่: 123 หมู่ 4 ตำบลเมืองน่าน อำเภอเมือง จังหวัดน่าน https://maps.app.goo.gl/75cbEb1D74oy3ZvZ8",
    "วัดเชียงของ ตำบลเชียงของ, ที่อยู่: ตำบลเชียงของ อำเภอเชียงของ จังหวัดน่าน https://maps.app.goo.gl/TxLVR4vw8uMudz4Y9",
    "วัดนาเกลือ ตำบลเชียงของ, ที่อยู่: ตำบลเชียงของ อำเภอเชียงของ จังหวัดน่าน https://maps.app.goo.gl/SYaSxXZ2QNZFQW1r6",
    "วัดน้ำหิน ตำบลเชียงของ, ที่อยู่: ตำบลเชียงของ อำเภอเชียงของ จังหวัดน่าน https://maps.app.goo.gl/PQ927GAXWrZpPGeo7",
    "วัดดอนไชย ตำบลนาน้อย, ที่อยู่: ตำบลนาน้อย อำเภอนาน้อย จังหวัดน่าน https://maps.app.goo.gl/uZdUNWL7teuUd59RA",
    "วัดนาน้อย ตำบลนาน้อย, ที่อยู่: ตำบลนาน้อย อำเภอนาน้อย จังหวัดน่าน https://maps.app.goo.gl/4MZffkyLEw1XVRo5A",
    "วัดนาราบ ตำบลนาน้อย, ที่อยู่: ตำบลนาน้อย อำเภอนาน้อย จังหวัดน่าน https://maps.app.goo.gl/juPXkLuKNza2Px5B8",
    "วัดนาหลวง ตำบลนาน้อย, ที่อยู่: ตำบลนาน้อย อำเภอนาน้อย จังหวัดน่าน https://maps.app.goo.gl/g7oeLvpXW182CoUM6",
    "วัดบุ้ง ตำบลนาน้อย, ที่อยู่: ตำบลนาน้อย อำเภอนาน้อย จังหวัดน่าน https://maps.app.goo.gl/y4WGcrpHEEEdKQrF9",
    "วัดเปา ตำบลน้ำตก, ที่อยู่: ตำบลน้ำตก อำเภอท่าวังผา จังหวัดน่าน https://maps.app.goo.gl/FufBfbgQc9cPWvef7",
    "วัดนาไค้ ตำบลบัวใหญ่, ที่อยู่: ตำบลบัวใหญ่ อำเภอเมือง จังหวัดน่าน https://maps.app.goo.gl/GvKoaBEA3jxkmpvFA",
    "วัดนาแหน ตำบลบัวใหญ่, ที่อยู่: ตำบลบัวใหญ่ อำเภอเมือง จังหวัดน่าน https://maps.app.goo.gl/qA6SnNpcCBcoiJHy5",
    "วัดสบหลม ตำบลบัวใหญ่, ที่อยู่: ตำบลบัวใหญ่ อำเภอเมือง จังหวัดน่าน https://maps.app.goo.gl/h4Czq26TqURD27QB8",
    "วัดอ้อย ตำบลบัวใหญ่, ที่อยู่: ตำบลบัวใหญ่ อำเภอเมือง จังหวัดน่าน https://maps.app.goo.gl/1MXKXLy5N4zkhCSF8",
    "วัดนาเตา ตำบลศรีสะเกษ, ที่อยู่: ตำบลศรีสะเกษ อำเภอท่าวังผา จังหวัดน่าน https://maps.app.goo.gl/NgKVN8VXzeZyPWZX6",
    "วัดป่าค่า ตำบลศรีสะเกษ, ที่อยู่: ตำบลศรีสะเกษ อำเภอท่าวังผา จังหวัดน่าน https://maps.app.goo.gl/9E7wAtNvT7bnqgEU8",
    "วัดสันทะ ตำบลสันทะ, ที่อยู่: ตำบลสันทะ อำเภอเชียงกลาง จังหวัดน่าน https://maps.app.goo.gl/N5vKz8CcNVNnbH6s6",
    "วัดคอวัง ตำบลกองควาย, ที่อยู่: ตำบลกองควาย อำเภอท่าวังผา จังหวัดน่าน https://maps.app.goo.gl/MnMJDNSgbE4MbXY76",
    "วัดธงหลวง ตำบลกองควาย, ที่อยู่: ตำบลกองควาย อำเภอท่าวังผา จังหวัดน่าน https://maps.app.goo.gl/8WnL3FWY4ggr34dS7",
    "วัดนาผา ตำบลกองควาย, ที่อยู่: ตำบลกองควาย อำเภอท่าวังผา จังหวัดน่าน https://maps.app.goo.gl/TUY6VbKKe5VM2eur9",
    "วัดน้ำครกเก่า ตำบลกองควาย, ที่อยู่: ตำบลกองควาย อำเภอท่าวังผา จังหวัดน่าน https://maps.app.goo.gl/vdkgaNjq17NKvFWP7",
    "วัดพุฒิมาราม ตำบลกองควาย, ที่อยู่: ตำบลกองควาย อำเภอท่าวังผา จังหวัดน่าน https://maps.app.goo.gl/1WroZEindt1TLjFr7",
    "วัดไชยสถาน ตำบลไชยสถาน, ที่อยู่: ตำบลไชยสถาน อำเภอเชียงกลาง จังหวัดน่าน https://maps.app.goo.gl/pnd3PXVSuWJkxC6u7",
    "วัดปางค่า ตำบลไชยสถาน, ที่อยู่: ตำบลไชยสถาน อำเภอเชียงกลาง จังหวัดน่าน https://maps.app.goo.gl/xa516NBDgUv4n4no7",
    "วัดฝาง ตำบลไชยสถาน, ที่อยู่: ตำบลไชยสถาน อำเภอเชียงกลาง จังหวัดน่าน https://maps.app.goo.gl/drwuxr2PwRgcUdrx8",
    "วัดเจดีย์ ตำบลดู่ใต้, ที่อยู่: ตำบลดู่ใต้ อำเภอปัว จังหวัดน่าน https://maps.app.goo.gl/wDeN64fyjr3WsYLPA",
    "วัดเชียงราย ตำบลดู่ใต้, ที่อยู่: ตำบลดู่ใต้ อำเภอปัว จังหวัดน่าน https://maps.app.goo.gl/hTSWFHBCaJq99FmSA",
    "วัดดอนมูล ตำบลดู่ใต้, ที่อยู่: ตำบลดู่ใต้ อำเภอปัว จังหวัดน่าน https://maps.app.goo.gl/moRFkywe4CiN4hhs5",
    "วัดดู่ใต้ ตำบลดู่ใต้, ที่อยู่: ตำบลดู่ใต้ อำเภอปัว จังหวัดน่าน https://maps.app.goo.gl/WiwgeqAmewH87HGJ6",
    "วัดพญาวัด ตำบลดู่ใต้, ที่อยู่: ตำบลดู่ใต้ อำเภอปัว จังหวัดน่าน https://maps.app.goo.gl/H5TydxtDDyhtVx6d8",
    "วัดพระธาตุเขาน้อย ตำบลดู่ใต้, ที่อยู่: ตำบลดู่ใต้ อำเภอปัว จังหวัดน่าน https://maps.app.goo.gl/CXpMcjCXYqdXXV8B6",
    "วัดสมุน ตำบลดู่ใต้, ที่อยู่: ตำบลดู่ใต้ อำเภอเมือง จังหวัดน่าน https://maps.app.goo.gl/ijn9Us11s25EuLhF6",
    "วัดเขื่อนแก้ว ตำบลถืมตอง, ที่อยู่: ตำบลถืมตอง อำเภอท่าวังผา จังหวัดน่าน https://maps.app.goo.gl/m5WRsP5reGqMxdLK7",
    "วัดดอนถืมตอง ตำบลถืมตอง, ที่อยู่: ตำบลถืมตอง อำเภอท่าวังผา จังหวัดน่าน https://maps.app.goo.gl/82VKyNVqqHbJY88q9",
    "วัดถิ่มตอง ตำบลถืมตอง, ที่อยู่: ตำบลถืมตอง อำเภอท่าวังผา จังหวัดน่านhttps://maps.app.goo.gl/t6hHq84LNV4NphdC6",
    "วัดนวราษฎร์ ตำบลนาซาว, ที่อยู่: ตำบลนาซาว อำเภอนาน้อย จังหวัดน่าน https://maps.app.goo.gl/FehqRkaMApm25FSBA",
    "วัดนาซาว ตำบลนาซาว, ที่อยู่: ตำบลนาซาว อำเภอนาน้อย จังหวัดน่าน https://maps.app.goo.gl/HdHsjDuwiUvjHnFj7",
    "วัดบ้านต้าม ตำบลนาซาว, ที่อยู่: ตำบลนาซาว อำเภอนาน้อย จังหวัดน่าน https://maps.app.goo.gl/WFvX4WKaR3e9SN4MA",
    "วัดสะไมย์ ตำบลนาซาว, ที่อยู่: ตำบลนาซาว อำเภอนาน้อย จังหวัดน่าน https://maps.app.goo.gl/3aymGcrSJzR4YdUZ6",
    "วัดกู่คำ ตำบลในเวียง, ที่อยู่: ตำบลในเวียง อำเภอเมือง จังหวัดน่าน https://maps.app.goo.gl/S9F5EYxinekLn7hB8",
    "วัดช้างเผือก ตำบลในเวียง, ที่อยู่: ตำบลในเวียง อำเภอเมือง จังหวัดน่าน https://maps.app.goo.gl/LnjgS6tPS7AkX3HG8",
    "วัดเชียงเเข็ง ตำบลในเวียง, ที่อยู่: ตำบลในเวียง อำเภอเมือง จังหวัดน่าน https://maps.app.goo.gl/NZUWeF8CJsvDm2zx9",
    "วัดดอนเเก้ว ตำบลในเวียง, ที่อยู่: ตำบลในเวียง อำเภอเมือง จังหวัดน่าน https://maps.app.goo.gl/knFsHZJB9AsYvBSM7",
    "วัดท่าช้าง ตำบลในเวียง, ที่อยู่: ตำบลในเวียง อำเภอเมือง จังหวัดน่าน https://maps.app.goo.gl/sormWnbvEH36jtfX6",
    "วัดน้ำล้อม ตำบลในเวียง, ที่อยู่: ตำบลในเวียง อำเภอเมือง จังหวัดน่าน https://maps.app.goo.gl/Vj79qyR4xc5ggCr66",
    "วัดไผ่เหลือง ตำบลในเวียง, ที่อยู่: ตำบลในเวียง อำเภอเมือง จังหวัดน่าน https://maps.app.goo.gl/BnPGYkshzmzrrRCj8",
    "วัดพระเกิด ตำบลในเวียง, ที่อยู่: ตำบลในเวียง อำเภอเมือง จังหวัดน่าน https://maps.app.goo.gl/TThbb8ArHF54d9jz9",
    "วัดพระเนตร ตำบลในเวียง, ที่อยู่: ตำบลในเวียง อำเภอเมือง จังหวัดน่าน https://maps.app.goo.gl/FSFC8UtUm5QiQxrH8",
    "วัดศรีเกิด ตำบลไชยสถาน, ที่อยู่: ตำบลไชยสถาน อำเภอเมือง จังหวัดน่าน https://maps.app.goo.gl/XaCkSwj7BD4sAQSu9",
    "วัดพวงพยอม ตำบลในเวียง, ที่อยู่: ตำบลในเวียง อำเภอเมือง จังหวัดน่าน https://maps.app.goo.gl/atp3JMBVAoe5RKn68"
    
]

# โหลดโมเดลแปลงข้อความเป็นเวกเตอร์
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

# ฟังก์ชันเพิ่มเอกสารเข้า Qdrant
def add_documents_to_qdrant(documents):
    vectors = embedding_model.encode(documents).tolist()
    
    points = [
        PointStruct(id=i, vector=vectors[i], payload={"text": documents[i]})
        for i in range(len(documents))
    ]
    qdrant_client.upsert(collection_name="documents", points=points)

# ฟังก์ชันค้นหาเอกสารแบบ Hybrid Search (เวกเตอร์ + Keyword Matching)
def search_documents(query):
    query_vector = embedding_model.encode([query])[0].tolist()
    
    search_results = qdrant_client.search(
        collection_name="documents",
        query_vector=query_vector,
        limit=59   # คืนค่ามา 5 อันดับแรก
    )

    # กรองเฉพาะผลลัพธ์ที่มีค่าความคล้ายสูงกว่า 0.7 และมีคำค้นหาอยู่ในข้อความ
    results = [
        hit.payload["text"] for hit in search_results
        if hit.score > 0.7 or query in hit.payload["text"]
    ]
    
    return results

# โหลดข้อมูลเข้า Qdrant
add_documents_to_qdrant(documents)

# UI ด้วย Streamlit
st.title("RAG Chatbot ค้นหาวัดในจังหวัดน่าน 🏯")

query = st.text_input("กรุณาป้อนชื่อวัดที่ต้องการค้นหา:")
if st.button("ค้นหา"):
    if query:
        results = search_documents(query)
        if results:
            st.write("🔍 ผลลัพธ์การค้นหา:")
            for idx, result in enumerate(results, start=1):
                st.write(f"{idx}. {result}")
        else:
            st.write("❌ ไม่พบข้อมูลที่เกี่ยวข้อง")
    else:
        st.write("⚠️ กรุณากรอกข้อความเพื่อค้นหา")
