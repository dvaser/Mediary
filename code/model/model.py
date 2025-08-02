from dotenv import load_dotenv
import os
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

load_dotenv()

embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

# Var olan veritabanını yükle
vectordb = Chroma(
    embedding_function=embeddings,
    persist_directory="./chromaDB_medical_v2"
)

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.2)
retriever = vectordb.as_retriever(search_kwargs={"k": 15})

# Medikal testler için gelişmiş prompt
medical_prompt = PromptTemplate(
    template="""Sen uzman bir tıbbi laboratuvar doktorusun. Aşağıdaki bilgileri kullanarak hastaya anlaşılır ve doğru bir açıklama yap.

📋 Mevcut Test Bilgileri:
{context}

❓ Hasta Sorusu: {question}

📝 Cevap Formatı:
1. 🎯 ANA DEĞERLENDİRME: Test sonucunun genel değerlendirmesi
2. 📊 NORMAL DEĞERLER: İlgili testlerin normal aralıkları
3. ⚠️ ANORMAL DURUM: Eğer değer anormalse, olası sebepleri
4. 🏥 KLİNİK ÖNEMİ: Bu sonucun klinik anlamı
5. 💡 ÖNERİLER: Hasta için öneriler (doktor başvurusu, takip testleri)

⚠️ ÖNEMLİ NOTLAR:
- Kesin tanı koyma, sadece olasılıkları açıkla
- Mutlaka doktor kontrolü öner
- Anlaşılır dil kullan
- Panik yaratma

Cevap:""",
    input_variables=["context", "question"]
)

qa_chain = RetrievalQA.from_chain_type(
    llm=llm, 
    retriever=retriever,
    chain_type_kwargs={"prompt": medical_prompt}
)

def display_relevant_docs(docs):
    """İlgili dokümanları düzenli şekilde göster"""
    print("\n🔎 İlgili Test Bilgileri:")
    print("=" * 50)
    
    # Test adına göre grupla
    test_groups = {}
    for doc in docs:
        test_name = doc.metadata["test"]
        if test_name not in test_groups:
            test_groups[test_name] = []
        test_groups[test_name].append(doc)
    
    for test_name, test_docs in test_groups.items():
        print(f"\n📊 {test_name}:")
        for doc in test_docs:
            trend = "⬇️ Düşük" if doc.metadata["pathological_trend"] == "low" else "⬆️ Yüksek"
            print(f"  {trend}: {doc.metadata['condition']}")
            print(f"  Normal Aralık: {doc.metadata['normal_range']} {doc.metadata['unit']}")
            print(f"  Açıklama: {doc.page_content}")
            print()

def get_test_statistics():
    """Veritabanındaki test istatistiklerini göster"""
    all_docs = vectordb.get()
    test_counts = {}
    
    for metadata in all_docs['metadatas']:
        test_name = metadata["test"]
        test_counts[test_name] = test_counts.get(test_name, 0) + 1
    
    print("\n📈 Mevcut Test Veritabanı:")
    print("=" * 30)
    for test, count in sorted(test_counts.items()):
        print(f"  {test}: {count} kayıt")
    print(f"\nToplam: {sum(test_counts.values())} kayıt")

def process_medical_query(query):
    """
    Medikal sorguyu işleyen ana fonksiyon
    
    Args:
        query (str): Kullanıcının medikal sorusu
    
    Returns:
        dict: Sorgu sonuçları içeren sözlük
    """
    try:
        # İlgili dokümanları al
        relevant_docs = retriever.invoke(query)
        
        # AI cevabını al
        result = qa_chain.invoke(query)
        
        return {
            "success": True,
            "relevant_docs": relevant_docs,
            "ai_response": result["result"],
            "error": None
        }
        
    except Exception as e:
        return {
            "success": False,
            "relevant_docs": None,
            "ai_response": None,
            "error": str(e)
        }

def print_query_result(result):
    """
    Sorgu sonucunu formatlanmış şekilde yazdır
    
    Args:
        result (dict): process_medical_query fonksiyonundan dönen sonuç
    """
    if result["success"]:
        # İlgili dokümanları göster
        if result["relevant_docs"]:
            display_relevant_docs(result["relevant_docs"])
        
        # AI cevabını göster
        print("\n🤖 AI Yorumu:")
        print("=" * 50)
        print(result["ai_response"])
    else:
        print(f"❌ Hata oluştu: {result['error']}")
        print("Lütfen tekrar deneyin.")

# Konsol uygulaması için ana fonksiyon
def run_console_app():
    """Konsol tabanlı uygulama çalıştır"""
    print("🏥 Medikal Test Sorgulama Sistemi")
    print("Kullanılabilir komutlar:")
    print("  - q: Çıkış")
    print("  - stats: Test istatistikleri")
    print("  - help: Bu yardım menüsü")
    print("\nÖrnek sorular:")
    print("  - 'Hemoglobin düşük çıktı, ne anlama geliyor?'")
    print("  - 'AST ve ALT yüksek, karaciğer problemi var mı?'")
    print("  - 'Trombosit sayısı 120, tehlikeli mi?'")


    while True:
        print("\n" + "-" * 50)
        query = input("\n❓ Soru sor: ").strip()
        
        if query.lower() == "q":
            print("👋 Görüşmek üzere!")
            break
        elif query.lower() == "stats":
            get_test_statistics()
            continue
        elif query.lower() == "help":
            print("\n🆘 Yardım:")
            print("Bu sistem medikal test sonuçlarını yorumlar.")
            print("Test adı, değer aralığı veya semptom sorabilirsiniz.")
            continue
        elif not query:
            print("⚠️ Lütfen bir soru yazın.")
            continue

        # Sorguyu işle ve sonucu göster
        result = process_medical_query(query)
        print_query_result(result)

# Eğer bu dosya doğrudan çalıştırılıyorsa konsol uygulamasını başlat
if __name__ == "__main__":
    run_console_app()