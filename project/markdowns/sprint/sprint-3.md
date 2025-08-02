# Sprint 3

* **Sprint Notes:**
  * ..
  * ..
  * ..
  * ..

* **Expected point completion within Sprint:** `100 points`

* **Point Completion Logic:** The entire project backlog consists of '300 points'. Dividing this into three sprints, the first sprint was assigned '100 points' of workload. 

* **Daily Scrum:** 
<br>
<div align="left">
  <img src="../../img/sprint/Sprint3/meeting-3.png" alt="Meeting Visual" width="70%" />
</div>

<br>
<div align="left">
  <img src="../../img/sprint/Sprint3/meeting-4.png" alt="Meeting Visual" width="70%" />
</div>

<br>
<div align="left">
  <img src="../../img/sprint/Sprint3/meeting-5.png" alt="Meeting Visual" width="70%" />
</div>

* **Meeting Dates:** `July 7nd,  July 14nd,  July 16nd,  July 20nd.`

* **Product Backlog URL:**
  
<br>
<div align="left">
  <img src="../../img/sprint/Sprint-2.png" alt="Product Backlog" width="70%" />
</div>


* **Sprint Review:**
  * ..
  * ..
  * ..
  * ..

* **Sprint Review Participants:** `Doğukan Vatansever, Hatice Ece Kırık, Zeynep Atik, Mevlüt Han Aşcı, Helin Hümeyra Saraçoğlu.`
  
* **Sprint Retrospective:**
  * ..
  * ..
  * ..
 
  ---
 <details>
    <summary><h3>Backend</h3></summary>

   * **Backend Developers:**
      * Zeynep ATİK
      * Mevlüt Han AŞCI
      * Doğukan VATANSEVER

</details>


---

 <details>
    <summary><h3>Frontend</h3></summary>

# 🧠 MEDIARY - AI-Powered Medical Diagnosis System

**MEDIARY** is an AI-assisted medical diagnosis and patient management system.  
It is a comprehensive web application that digitalizes the processes of medical examination, diagnosis, and treatment planning for doctors.

---

## 🩺 Features

### 🔹 Core Features
- **🧠 AI-Based Diagnosis System**: Provides suggestions based on patient complaints and lab results
- **📋 Patient Management**: Full-featured patient registration and follow-up system
- **🔄 Examination Workflow**: Structured 4-step digital examination process
- **💊 Prescription Creation**: Digital prescription generation and printing
- **🤖 AI Chatbot**: Smart assistant for general medical questions
- **📱 Responsive Design**: Fully compatible with mobile, tablet, and desktop devices

---

<br>
<div align="left">
  <img src="../../img/sprint/Sprint3/main_entrance.png" alt="Meeting Visual" width="70%" />
</div>

<br>
<div align="left">
  <img src="../../img/sprint/Sprint3/doctor_login_page.png" alt="Meeting Visual" width="70%" />
</div>

## 👨‍⚕️ Demo Users

The system comes with predefined demo users:

| Username  | Password  | Doctor Name               | Specialty            |
|-----------|-----------|---------------------------|----------------------|
| skoz      | doktor123 | Prof. Dr. Süleyman Köz    | Cardiology           |
| ademir    | hekim456  | Dr. Ayşe Demir            | Internal Medicine    |
| myilmaz   | tip789    | Dr. Mehmet Yılmaz         | General Practitioner |
| admin     | admin123  | Admin User                | System Administrator |


<br>
<div align="left">
  <img src="../../img/sprint/Sprint3/dashboard_page.png" alt="Meeting Visual" width="70%" />
</div>

---

## 🩻 Examination Workflow

1. **📝 Initial Patient Interview**  
   Logging of complaints and doctor’s notes

2. **🧪 Lab Test Request**  
   AI-suggested diagnostic tests based on symptoms

3. **📊 AI Interpretation**  
   AI-powered analysis of lab results

4. **💊 Prescription & Outcome**  
   Final diagnosis, prescription generation, and medical recommendations

## 📱 Usage

### Logging In
1. On the homepage, click the **"Doctor Login"** button  
2. Use one of the demo credentials or enter your own login details  
3. Access the system dashboard  

### Patient Examination
1. On the dashboard, click **"Start Patient Examination"**  
2. Select an existing patient or use **"New Patient Registration"** to add one  
3. Follow the 4-step examination process:
   - Record the patient's complaint  
   - Select the required tests  
   - Wait for the AI analysis  
   - Generate the prescription and recommendations  

### AI Assistant
- Use the AI chatbot located at the bottom-right corner to ask general medical questions  
- You can choose from predefined questions or type your own inquiries  
---

<br>
<div align="left">
  <img src="../../img/sprint/Sprint3/patient_preliminary_interview.png" alt="Meeting Visual" width="70%" />
</div>

<br>
<div align="left">
  <img src="../../img/sprint/Sprint3/analysis_request_page.png" alt="Meeting Visual" width="70%" />
</div>

<br>
<div align="left">
  <img src="../../img/sprint/Sprint3/Ai_comment_page.png" alt="Meeting Visual" width="70%" />
</div>

<br>
<div align="left">
  <img src="../../img/sprint/Sprint3/reçete_sayfası.png" alt="Meeting Visual" width="70%" />
</div>


## 🗄️ Database Models

### 🧑‍⚕️ Doctor
- One-to-One relationship with Django `User` model  
- Medical specialty  
- License number  

### 🧍 Patient
- Personal information (name, national ID, age, gender)  
- Medical history  
- Allergy details  
- Blood type  

### 📝 Examination
- Relation between patient and doctor  
- Complaint records  
- Diagnosis information  
- Prescription and medical recommendations  

### 🧪 TestRequest
- Linked to an examination  
- Test name and priority  
- AI suggestion status  

## 🏗️ Project Structure

<br>
<div align="left">
  <img src="../../img/sprint/Sprint3/project_structure.png" alt="Meeting Visual" width="70%" />
</div>


### ⚙️ Technical Specifications

- Django 4.2.7 framework  
- SQLite database  
- Django authentication system  
- AJAX API endpoints  
- Responsive design using CSS Grid and Flexbox  
- Font Awesome icon set  

## 🎨 Design Features

- **Modern UI/UX**: Gradient backgrounds and glassmorphism effects  
- **Responsive**: Mobile-first design approach  
- **Animations**: CSS3 transitions and hover effects  
- **Color Palette**: Medical theme (shades of blue, green, and white)  
- **Typography**: Segoe UI font family  
- **Icons**: Font Awesome 6.0  

---

## 🔒 Security

- Built-in Django Authentication system  
- CSRF protection  
- Session-based authentication  
- SQL Injection protection (via Django ORM)  
- XSS protection  
- Secure form validation  
- Password hashing mechanism  

---
**Frontend Developers:**
  * Helin Hümeyra SARAÇOĞLU
  * Hatice Ece KIRIK
---

</details>

---

<details>
  <summary><h3>Road Map</h3></summary>

## Development Roadmap

### v1.1 (Upcoming Release)
- **PDF Export** – Print prescriptions and medical reports  
- **Database Integration** – Support for MySQL/PostgreSQL  
- **API Integration** – RESTful API support  
- **User Authentication** – Login/Logout system  

### v1.2 (Mid-Term)
- **Real AI Integration** – OpenAI or custom ML model integration  
- **Patient Appointment System** – Calendar and scheduling support  
- **E-Nabız Integration** – Turkish Ministry of Health data sync  
- **Multi-language Support** – English interface support  

### v2.0 (Long-Term)
- **Hospital Management System** – Multi-doctor and multi-department support  
- **Lab Results Integration** – Automated lab data synchronization  
- **Mobile Application** – React Native app for iOS and Android  
- **Blockchain Integration** – Secure data storage and verification  

<br>
<div align="left">
  <img src="../../img/sprint/Sprint3/roadmap_1.png" alt="Meeting Visual" width="70%" />
</div>

<div align="left">
  <img src="../../img/sprint/Sprint3/roadmap_2.png" alt="Meeting Visual" width="70%" />
</div>

<div align="left">
  <img src="../../img/sprint/Sprint3/roadmap_3.png" alt="Meeting Visual" width="70%" />
</div>

<div align="left">
  <img src="../../img/sprint/Sprint3/roadmap_4.png" alt="Meeting Visual" width="70%" />
</div>
 
</details>

---


> ⚠️ **Note**: This system is for **demonstration purposes only** and is **not suitable for real medical use**.  
> Always consult a qualified physician for medical decisions.
 --- 

> **[Click to return to the main file](../../README.md)**
