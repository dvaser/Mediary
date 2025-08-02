// Global variables
let currentPatientId = 1;

// Patient data structure
let patientsData = {
    1: {
        name: "Mehmet Kaya",
        tc: "12345678901",
        age: 42,
        gender: "Erkek",
        bloodType: "A+",
        complaint: "Yaklaşık üç gündür sağ böbrek bölgemde ara ara şiddetlenen keskin bir ağrı hissediyorum. Ağrı özellikle hareket ettiğimde artıyor ve bazen dayanılmaz hale geliyor. İdrar yaparken yanma hissi yaşıyorum ve idrar rengimde koyulaşma fark ettim. Ayrıca zaman zaman idrarda kan gördüm. Son iki gündür mide bulantısı olan ve kendimi yorgun hissediyorum. Daha önce böbrek taşı düşürmüştüm ve ailemde böbrek yetmezliği öyküsü var. Günlük su tüketimim oldukça az ve son zamanlarda tuzlu gıdalar tüketmeye başladım. Ağrımı hafifletmek için sıcak su torbası kullanıyorum, bu bir nebze rahatlama sağlıyor. Tansiyon ilaçları kullanıyorum ve geçmişte antibiyotik alerjisi yaşamıştım.",
        notes: [
            {
                type: "emphasis",
                text: "Penisilin ilacına karşı alerjisi bulunmaktadır."
            },
            {
                type: "normal",
                text: "Aktif olarak 'Lisinopril' ilacını günde 1 kez kullanmaktadır."
            },
            {
                type: "normal",
                text: "Geçmişte böbrek taşı öyküsü mevcut. Aile öyküsünde böbrek yetmezliği var."
            }
        ]
    },
    2: {
        name: "Fatma Demir",
        tc: "98765432109",
        age: 28,
        gender: "Kadın",
        bloodType: "B+",
        complaint: "Son bir haftadır sürekli baş ağrısı çekiyorum. Özellikle sabahları uyanırken ağrı daha şiddetli oluyor. Gözlerimin önünde parıltılar görüyorum ve bazen bulantı hissediyorum.",
        notes: [
            {
                type: "emphasis",
                text: "Migren aile öyküsü mevcut. Anne tarafından kalıtsal."
            },
            {
                type: "normal",
                text: "Stress seviyesi yüksek, yoğun çalışma temposu var."
            }
        ]
    },
    3: {
        name: "Zehra Özkan",
        tc: "11122233344",
        age: 35,
        gender: "Kadın",
        bloodType: "0+",
        complaint: "Yaklaşık iki gündür boğazımda şiddetli ağrı var. Yutkunmakta güçlük çekiyorum ve ses kısıklığı yaşıyorum. Hafif ateşim de var.",
        notes: []
    },
    4: {
        name: "Ali Veli",
        tc: "55566677788",
        age: 53,
        gender: "Erkek",
        bloodType: "AB+",
        complaint: "Geçen hafta başlayan öksürük giderek artıyor. Özellikle geceleri daha çok öksürüyorum ve balgam çıkarıyorum. Nefes almakta da zorluk yaşıyorum.",
        notes: [
            {
                type: "emphasis",
                text: "30 yıllık sigara kullanım öyküsü mevcut."
            },
            {
                type: "normal",
                text: "KOAH riski yüksek. Düzenli kontroller gerekli."
            }
        ]
    }
};

// Login Modal Functions
function showLoginModal() {
    document.getElementById('loginModal').style.display = 'flex';
}

function closeLoginModal() {
    document.getElementById('loginModal').style.display = 'none';
}

function fillDemoCredentials(username, password) {
    document.getElementById('username').value = username;
    document.getElementById('password').value = password;
}

function handleLogin(event) {
    event.preventDefault();
    
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const errorMessage = document.getElementById('errorMessage');
    const loginSubmit = document.getElementById('loginSubmit');
    
    // Demo credentials
    const validCredentials = {
        'skoz': 'doktor123',
        'ademir': 'hekim456',
        'myilmaz': 'tip789',
        'admin': 'admin123'
    };
    
    if (validCredentials[username] === password) {
        // Show loading state
        const originalText = loginSubmit.innerHTML;
        loginSubmit.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Giriş yapılıyor...';
        loginSubmit.disabled = true;
        loginSubmit.style.background = 'linear-gradient(135deg, #00695c, #004d40)';
        
        // Add realistic delay (2-3 seconds)
        setTimeout(() => {
            closeLoginModal();
            showMediarySystem(username);
            
            // Reset button state for next time
            loginSubmit.innerHTML = originalText;
            loginSubmit.disabled = false;
            loginSubmit.style.background = 'linear-gradient(135deg, #3b82f6, #1e40af)';
            document.getElementById("mediarySystem").scrollIntoView({ behavior: "auto" });
        }, 2500); // 2.5 second delay
        
    } else {
        // Show error with shake animation
        loginSubmit.style.animation = 'shake 0.5s ease-in-out';
        errorMessage.style.display = 'block';
        
        setTimeout(() => {
            errorMessage.style.display = 'none';
            loginSubmit.style.animation = '';
        }, 3000);
    }
}

function showMediarySystem(username) {
    document.getElementById('main-website').style.display = 'none';
    const mediarySystem = document.getElementById('mediarySystem');
    mediarySystem.style.display = 'block';

    // Sistemi yumuşak geçişle göster
    setTimeout(() => {
        mediarySystem.classList.add('show');
    }, 100);

    // Doktor adı eşle
    const doctorNames = {
        'skoz': 'Dr. Süleyman Köz',
        'ademir': 'Dr. Ayşe Demir',
        'myilmaz': 'Dr. Mehmet Yılmaz',
        'admin': 'Admin User'
    };
    
    const doctorName = doctorNames[username] || 'Dr. Kullanıcı';
    document.getElementById('currentUserName').textContent = doctorName;
    document.getElementById('userBadgeName').textContent = doctorName;
    document.getElementById('loginTime').textContent = new Date().toLocaleTimeString('tr-TR');

    // Dashboard görünümünü göster
    showDashboard();

    // Hoş geldin bildirimi
    setTimeout(() => {
        showNotification(`Hoş geldiniz ${doctorName}! MEDIARY sistemine başarıyla giriş yaptınız.`, 'success');
    }, 1000);
}

function resetSystem() {
    // Tüm metin girişlerini ve textarea'ları temizle
    document.querySelectorAll('input[type="text"], textarea').forEach(el => el.value = '');

    // Tüm checkbox'ları temizle
    document.querySelectorAll('input[type="checkbox"]').forEach(el => el.checked = false);

    // Manuel test listesi temizle
    const manualList = document.getElementById('manualTestsList');
    if (manualList) manualList.innerHTML = '';

    // Seçilen testleri temizle
    const selectedList = document.getElementById('selectedTestsList');
    if (selectedList) {
        selectedList.innerHTML = '<div class="selected-test" style="color: rgba(255,255,255,0.5);">• Henüz tetkik seçilmedi</div>';
    }

    const summaryTitle = document.querySelector('.selected-tests-summary h5');
    if (summaryTitle) {
        summaryTitle.textContent = 'Seçilen Tetkikler (0 adet):';
    }

    const aiResults = document.getElementById('aiResults');
    if (aiResults) aiResults.style.display = 'none';

    const evaluationLoading = document.getElementById('evaluationLoading');
    if (evaluationLoading) evaluationLoading.style.display = 'none';

    const evaluateBtn = document.getElementById('evaluateBtn');
    if (evaluateBtn) {
        evaluateBtn.style.display = 'block';
    }

    const prescriptionList = document.getElementById('prescriptionList');
    if (prescriptionList) {
        prescriptionList.innerHTML = `
            <div class="prescription-item">
                <div class="drug-info">
                    <input type="text" class="drug-name" placeholder="İlaç adı" />
                    <input type="text" class="drug-dosage" placeholder="Dozaj" />
                    <input type="text" class="drug-frequency" placeholder="Kullanım sıklığı" />
                    <input type="text" class="drug-duration" placeholder="Süre" />
                    <button class="remove-drug-btn" onclick="removeDrug(this)">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
            </div>
        `;
    }

    // AI, Reçete ve Tahlil sekmelerini kilitle
    const tabs = ['aiAnalysisTab', 'prescriptionTab', 'evaluationTab'];
    tabs.forEach(id => {
        const tab = document.getElementById(id);
        if (tab) {
            tab.classList.add('locked');
            const lockIcon = tab.querySelector('.fa-lock');
            if (lockIcon) lockIcon.style.display = 'inline';
        }
    });

    showTab('preview');
}

function returnToHomepage() {
    document.getElementById('mediarySystem').style.display = 'none';
    document.getElementById('main-website').style.display = 'block';
}

// Patient dropdown toggle
function togglePatientDropdown() {
    const options = document.getElementById('patientOptions');
    const arrow = document.getElementById('dropdownArrow');
    
    options.classList.toggle('show');
    arrow.style.transform = options.classList.contains('show') ? 'rotate(180deg)' : 'rotate(0deg)';
}

// View Management Functions
function showDashboard() {
    document.getElementById('dashboardView').classList.remove('hidden');
    document.getElementById('dashboardView').style.display = 'block';
    document.getElementById('examinationView').classList.remove('active');
    document.getElementById('examinationView').style.display = 'none';
    document.getElementById('backToDashboard').style.display = 'none';
}

// Dashboard action functions
function startPatientExamination() {
    // Dashboard görünümünü gizle
    document.getElementById('dashboardView').style.display = 'none';
    
    // Muayene görünümünü göster
    document.getElementById('examinationView').style.display = 'block';
    document.getElementById('examinationView').classList.add('active');
    
    // Dashboard'a dönüş butonunu göster
    document.getElementById('backToDashboard').style.display = 'inline-block';

    // Bugünün tarihini ayarla
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('selectedDate').value = today;

    // İlk hasta verisini yükle
    loadPatientData(1);

    // Bildirim göster
    showNotification('Hasta muayene modülü başlatıldı. Hasta seçin ve muayeneye başlayın.', 'success');
}

        function openAIAssistant() {
    showAIAssistant();
}


// Close dropdown when clicking outside
document.addEventListener('click', function(event) {
    const dropdown = document.querySelector('.patient-dropdown');
    const options = document.getElementById('patientOptions');
    const arrow = document.getElementById('dropdownArrow');
    
    if (dropdown && !dropdown.contains(event.target)) {
        options.classList.remove('show');
        arrow.style.transform = 'rotate(0deg)';
    }
});

// Select patient function
function selectPatient(element, patientId, patientName) {
    resetSystem();
    currentPatientId = patientId;
    
    document.getElementById('selectedPatient').textContent = patientName;
    
    document.querySelectorAll('.patient-option').forEach(option => {
        option.classList.remove('selected');
    });
    element.classList.add('selected');
    
    document.getElementById('patientOptions').classList.remove('show');
    document.getElementById('dropdownArrow').style.transform = 'rotate(0deg)';
    
    loadPatientData(patientId);
}

// Load patient data
function loadPatientData(patientId) {
    const patient = patientsData[patientId];
    if (!patient) {
        console.warn('Patient not found:', patientId);
        return;
    }
    
    document.getElementById('patientTC').textContent = patient.tc;
    document.getElementById('patientAge').textContent = patient.age;
    document.getElementById('patientGender').textContent = patient.gender;
    document.getElementById('patientBloodType').textContent = patient.bloodType;
    
    document.getElementById('complaintText').value = patient.complaint;
    
    updatePatientNotes(patient.notes);
}

// Update patient notes
function updatePatientNotes(notes) {
    const notesContainer = document.querySelector('.patient-notes');
    const existingNotes = notesContainer.querySelectorAll('.note-item');
    
    existingNotes.forEach(note => note.remove());
    
    if (!notes || notes.length === 0) {
        notesContainer.style.display = 'none';
    } else {
        notesContainer.style.display = 'block';
        
        notes.forEach(note => {
            const noteElement = document.createElement('div');
            noteElement.className = note.type === 'emphasis' ? 'note-item note-emphasis' : 'note-item';
            noteElement.textContent = note.text;
            notesContainer.appendChild(noteElement);
        });
    }
}

    // Clear workflow cache and reset all tabs
function clearWorkflowCache() {
    // Reset all tabs to locked state except first one
    const evaluationTab = document.getElementById('evaluationTab');
    const aiAnalysisTab = document.getElementById('aiAnalysisTab');
    const prescriptionTab = document.getElementById('prescriptionTab');
    
    // Lock tabs
    evaluationTab.classList.add('locked');
    aiAnalysisTab.classList.add('locked');
    prescriptionTab.classList.add('locked');
    
    // Show lock icons
    const evaluationLock = evaluationTab.querySelector('.fa-lock');
    const aiLock = aiAnalysisTab.querySelector('.fa-lock');
    const prescriptionLock = prescriptionTab.querySelector('.fa-lock');
    
    if (evaluationLock) evaluationLock.style.display = 'inline';
    if (aiLock) aiLock.style.display = 'inline';
    if (prescriptionLock) prescriptionLock.style.display = 'inline';
    
    // Reset active tab to first one
    document.querySelectorAll('.nav-tab').forEach(tab => tab.classList.remove('active'));
    document.querySelector('.nav-tab').classList.add('active');
    
    // Show only first tab content
    document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
    document.getElementById('preview-tab').classList.add('active');
    
    // Reset AI analysis state
    const evaluateBtn = document.getElementById('evaluateBtn');
    const loadingSpinner = document.getElementById('evaluationLoading');
    const aiResults = document.getElementById('aiResults');
    const progressFill = document.getElementById('progressFill');
    
    if (evaluateBtn) {
        evaluateBtn.style.display = 'flex';
        evaluateBtn.disabled = false;
        evaluateBtn.innerHTML = '<i class="fas fa-brain"></i> Testleri AI ile Değerlendir';
    }
    
    if (loadingSpinner) {
        loadingSpinner.classList.remove('show');
    }
    
    if (aiResults) {
        aiResults.style.display = 'none';
        aiResults.classList.remove('show');
    }
    
    if (progressFill) {
        progressFill.style.width = '0%';
    }
    
    // Reset save button
    const saveBtn = document.getElementById('saveComplaintBtn');
    if (saveBtn) {
        saveBtn.innerHTML = '<i class="fas fa-save"></i> Tahlil İsteğinde Bulun';
        saveBtn.classList.remove('saved');
    }
    
    // Reset test selections to default
    resetTestSelections();
    
    // Clear any existing notifications
    const existingNotifications = document.querySelectorAll('.notification');
    existingNotifications.forEach(notification => {
        if (document.body.contains(notification)) {
            document.body.removeChild(notification);
        }
    });
}

// Reset test selections to default and update display
function resetTestSelections() {
    // Uncheck all tests first
    document.querySelectorAll('.test-checklist input[type="checkbox"]').forEach(checkbox => {
        checkbox.checked = false;
    });
    
    // Check default tests (urgent ones)
    const defaultTests = ['urinalysis', 'creatinine_gfr', 'kidney_ultrasound'];
    defaultTests.forEach(testId => {
        const checkbox = document.getElementById(testId);
        if (checkbox) {
            checkbox.checked = true;
        }
    });
    
    // Update selected tests display immediately
    updateSelectedTests();
}

// Tab switching function with lock check
function showTab(tabName) {
    const targetTab = document.getElementById(tabName + '-tab');
    const targetButton = event ? event.target.closest('.nav-tab') : document.querySelector(`[onclick="showTab('${tabName}')"]`);
    
    // Check if tab is locked
    if (targetButton && targetButton.classList.contains('locked')) {
        targetButton.style.animation = 'shake 0.5s ease-in-out';
        setTimeout(() => {
            targetButton.style.animation = '';
        }, 500);
        
        showNotification('Bu sekmeye erişmek için önceki adımları tamamlamanız gerekiyor.', 'warning');
        return;
    }
    
    // Hide all tab contents
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });
    
    // Remove active class from all tab buttons
    document.querySelectorAll('.nav-tab').forEach(button => {
        button.classList.remove('active');
    });
    
    // Show target tab and activate button
    if (targetTab) {
        targetTab.classList.add('active');
    }
    
    if (targetButton) {
        targetButton.classList.add('active');
    }
}

// Save complaint and unlock evaluation tab
function saveComplaintAndUnlock() {
    const text = document.getElementById('complaintText').value.trim();
    
    if (text === '') {
        showNotification('Lütfen hasta şikayetini yazınız.', 'warning');
        return;
    }
    
    patientsData[currentPatientId].complaint = text;
    
    // Unlock evaluation tab
    const evaluationTab = document.getElementById('evaluationTab');
    evaluationTab.classList.remove('locked');
    const lockIcon = evaluationTab.querySelector('.fa-lock');
    if (lockIcon) {
        lockIcon.style.display = 'none';
    }
    
    // Switch to evaluation tab
    showTab('evaluation');
    
    // Update button text
    const saveBtn = document.getElementById('saveComplaintBtn');
    saveBtn.innerHTML = '<i class="fas fa-check"></i> Şikayet Kaydedildi';
    saveBtn.classList.add('saved');
    
    showNotification('Hasta şikayeti kaydedildi! Tahlil İsteği sekmesi açıldı.', 'success');
}

function requestTestsAndUnlock() {
    const selectedTests = new Set();

    // Checkbox ile seçilen testleri al
    document.querySelectorAll('.test-checklist input[type="checkbox"]:checked').forEach(cb => {
        const label = cb.nextElementSibling?.textContent.trim();
        if (label) selectedTests.add(label);
    });

    // Manuel olarak eklenen testleri al (#manualTestsList)
    document.querySelectorAll('#manualTestsList .selected-test').forEach(el => {
        const testName = el.textContent.replace('•', '').trim();
        if (testName) selectedTests.add(testName);
    });

    // Eğer hiç test yoksa uyarı
    if (selectedTests.size === 0) {
        showNotification('Lütfen en az bir tetkik seçiniz.', 'warning');
        return;
    }

    // Bildirim doğru sayı ile
    showNotification(`Seçilen ${selectedTests.size} tetkik isteği laboratuvara gönderildi!`, 'success');

    // AI sekmesini aç
    const aiAnalysisTab = document.getElementById('aiAnalysisTab');
    if (aiAnalysisTab) {
        aiAnalysisTab.classList.remove('locked');
        const lockIcon = aiAnalysisTab.querySelector('.fa-lock');
        if (lockIcon) lockIcon.style.display = 'none';
    }

    // Sekmeyi değiştir
    showTab('ai-analysis');
}




// View PDF function
function viewPDF(pdfType) {
    const pdfNames = {
        'kan-tahlili': 'Kan Tahlili Sonuçları',
        'idrar-tahlili': 'İdrar Tahlili Sonuçları',
        'ultrason': 'Ultrason Raporu'
    };
    
    showNotification(`${pdfNames[pdfType]} görüntüleniyor...`, 'info');
}

// Enhanced Evaluate tests function with progress bar and notification
function evaluateTests() {
    const evaluateBtn = document.getElementById('evaluateBtn');
    const loadingSpinner = document.getElementById('evaluationLoading');
    const aiResults = document.getElementById('aiResults');
    const progressFill = document.getElementById('progressFill');
    
    // Disable button and show loading
    evaluateBtn.disabled = true;
    evaluateBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Analiz Ediliyor...';
    loadingSpinner.classList.add('show');
    
    // Animate progress bar
    let progress = 0;
    const progressInterval = setInterval(() => {
        progress += 2;
        progressFill.style.width = progress + '%';
        
        if (progress >= 100) {
            clearInterval(progressInterval);
        }
    }, 60);
    
    // Simulate AI analysis with realistic timing
    setTimeout(() => {
        loadingSpinner.classList.remove('show');
        aiResults.style.display = 'block';
        aiResults.classList.add('show');
        // evaluateBtn.style.display = 'none';
        evaluateBtn.disabled = false;
        evaluateBtn.innerHTML = '<i class="fas fa-brain"></i> Testleri AI ile Değerlendir';
        
        // Reset progress bar
        progressFill.style.width = '0%';
        
        // Scroll to results with smooth animation
        setTimeout(() => {
            aiResults.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }, 100);
        
        // Add a subtle success notification
        showNotification('AI analizi başarıyla tamamlandı!', 'success');
    }, 3000);
}

// Unlock prescription tab
function unlockPrescriptionTab() {
    const prescriptionTab = document.getElementById('prescriptionTab');
    prescriptionTab.classList.remove('locked');
    const lockIcon = prescriptionTab.querySelector('.fa-lock');
    if (lockIcon) {
        lockIcon.style.display = 'none';
    }
    
    // Switch to prescription tab
    showTab('prescription');
    
    showNotification('AI analizi tamamlandı! Şimdi reçete hazırlayabilirsiniz.', 'success');
}

function updateSelectedTests() {
    const selectedTestsList = document.getElementById('selectedTestsList');
    selectedTestsList.innerHTML = '';

    const selectedTests = new Set(); // hem checkbox hem manuel eklenenleri tek set içinde tutar

    // Checkbox ile seçilen testler
    const checkboxes = document.querySelectorAll('.test-checklist input[type="checkbox"]:checked');
    checkboxes.forEach(checkbox => {
        const label = checkbox.nextElementSibling.textContent.trim();
        selectedTests.add(label);
    });

    // Manuel eklenen testler
    const manualTests = document.querySelectorAll('#manualTestsList .selected-test');
    manualTests.forEach(testItem => {
        const label = testItem.textContent.replace('•', '').trim();
        selectedTests.add(label);
    });

    // Seçili testleri listele
    if (selectedTests.size === 0) {
        selectedTestsList.innerHTML = '<div class="selected-test" style="color: rgba(255,255,255,0.5);">• Henüz tetkik seçilmedi</div>';
    } else {
        selectedTests.forEach(label => {
            const testDiv = document.createElement('div');
            testDiv.className = 'selected-test';
            testDiv.innerHTML = `• ${label}`;
            selectedTestsList.appendChild(testDiv);
        });
    }

    // Sayıyı güncelle
    const summaryTitle = document.querySelector('.selected-tests-summary h5');
    if (summaryTitle) {
        summaryTitle.textContent = `Seçilen Tetkikler (${selectedTests.size} adet):`;
    }
}

function addManualTest() {
    const input = document.getElementById('manualTestInput');
    const testName = input.value.trim();

    if (testName === "") return;

    // Seçilen testler listesine ekle
    const selectedList = document.getElementById('selectedTestsList');

    // Aynı test daha önce eklendiyse tekrar eklenmesin
    const alreadyExists = Array.from(selectedList.children).some(el =>
        el.textContent.includes(testName)
    );
    if (alreadyExists) {
        alert("Bu tetkik zaten eklendi.");
        input.value = '';
        return;
    }

    const selectedItem = document.createElement('div');
    selectedItem.className = 'selected-test';
    selectedItem.textContent = `• ${testName}`;
    selectedList.appendChild(selectedItem);

    // Toplam sayıyı güncelle
    updateSelectedTestCount();

    // Input temizle
    input.value = '';
}

const suggestions = [
    "ALT (SGPT)", "AST (SGOT)", "HbA1c", "Açlık Kan Şekeri",
    "Vitamin B12", "TSH", "fT3", "fT4","Demir", "Ferritin", 
    "Akciğer Grafisi", "Batın Ultrasonu"
];

function filterSuggestions() {
    const input = document.getElementById('manualTestInput');
    const query = input.value.toLowerCase();
    const box = document.getElementById('customSuggestions');

    box.innerHTML = '';
    if (query === '') {
        box.style.display = 'none';
        return;
    }

    const filtered = suggestions.filter(item => item.toLowerCase().includes(query));
    filtered.forEach(s => {
        const div = document.createElement('div');
        div.textContent = s;
        div.onclick = () => {
            input.value = s;
            box.style.display = 'none';
        };
        box.appendChild(div);
    });

    box.style.display = filtered.length > 0 ? 'block' : 'none';
}


function updateSelectedTestCount() {
    const count = document.querySelectorAll('#selectedTestsList .selected-test').length;
    const summaryHeader = document.querySelector('.selected-tests-summary h5');
    summaryHeader.textContent = `Seçilen Tetkikler (${count} adet):`;
}

// Add drug to prescription
function addDrug() {
    const prescriptionList = document.getElementById('prescriptionList');
    const drugItem = document.createElement('div');
    drugItem.className = 'prescription-item';
    drugItem.innerHTML = `
        <div class="drug-info">
            <input type="text" class="drug-name" placeholder="İlaç adı" />
            <input type="text" class="drug-dosage" placeholder="Dozaj" />
            <input type="text" class="drug-frequency" placeholder="Kullanım sıklığı" />
            <input type="text" class="drug-duration" placeholder="Süre" />
            <button class="remove-drug-btn" onclick="removeDrug(this)">
                <i class="fas fa-times"></i>
            </button>
        </div>
    `;
    prescriptionList.appendChild(drugItem);
}

// Remove drug from prescription
function removeDrug(button) {
    const drugItem = button.closest('.prescription-item');
    drugItem.remove();
}

// Save prescription
function savePrescription() {
    showNotification('Reçete başarıyla kaydedildi!', 'success');
}

// Print prescription
function printPrescription() {
    showNotification('Reçete yazdırma işlemi başlatılıyor...', 'info');
}

// Enhanced notification system
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${type === 'success' ? '#4caf50' : type === 'warning' ? '#ff9800' : '#2196f3'};
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        z-index: 2000;
        animation: slideInRight 0.3s ease;
        max-width: 350px;
        font-size: 0.9rem;
        line-height: 1.4;
    `;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'slideOutRight 0.3s ease';
        setTimeout(() => {
            if (document.body.contains(notification)) {
                document.body.removeChild(notification);
            }
        }, 300);
    }, 3000);
}

    // AI Assistant functions
function showAIAssistant() {
    document.getElementById('aiChatbot').classList.add('show');
}

function closeAIChatbot() {
    document.getElementById('aiChatbot').classList.remove('show');
}

function askQuickQuestion(question) {
    const messagesContainer = document.getElementById('chatbotMessages');
    
    // Add user message
    const userMessage = document.createElement('div');
    userMessage.className = 'message user';
    userMessage.textContent = question;
    messagesContainer.appendChild(userMessage);
    
    // Show typing indicator
    const typingIndicator = document.getElementById('typingIndicator');
    typingIndicator.classList.add('show');
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
    
    // Simulate AI response after delay
    setTimeout(() => {
        typingIndicator.classList.remove('show');
        
        const botMessage = document.createElement('div');
        botMessage.className = 'message bot';
        botMessage.innerHTML = getAIResponse(question);
        messagesContainer.appendChild(botMessage);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }, 2000);
}

function sendMessage() {
    const input = document.getElementById('chatbotInput');
    const message = input.value.trim();
    
    if (message === '') return;
    
    askQuickQuestion(message);
    input.value = '';
}

function getAIResponse(question) {
    const responses = {
        'Yüksek tansiyon belirtileri nelerdir?': 'Yüksek tansiyon belirtileri: baş ağrısı, burun kanaması, nefes darlığı, göğüs ağrısı, baş dönmesi olabilir. Ancak çoğu zaman sessiz seyreder.<br><br><strong>⚠️ Önemli:</strong> Tansiyon takibi için düzenli doktor kontrolü şarttır.',
        
        'Diabetin önlenmesi nasıl sağlanır?': 'Diabetin önlenmesi için: düzenli egzersiz, sağlıklı beslenme, kilo kontrolü, şekerli içeceklerden kaçınma, lif açısından zengin gıdalar tüketme önemlidir.<br><br><strong>⚠️ Önemli:</strong> Risk faktörleri için doktorunuzla görüşün.',
        
        'Böbrek taşı nasıl önlenir?': 'Böbrek taşı önlenmesi: günde 2-3 litre su içme, tuz kısıtlaması, kalsiyum açısından dengeli beslenme, oksalat içeren gıdaları sınırlama.<br><br><strong>⚠️ Önemli:</strong> Geçmişte taş öyküsü varsa üroloji takibi gereklidir.',
        
        'Sağlıklı beslenme önerileri': 'Sağlıklı beslenme: çok çeşitli sebze-meyve, tam tahıllar, yağsız protein, sınırlı işlenmiş gıda, bol su tüketimi.<br><br><strong>⚠️ Önemli:</strong> Özel diyetler için beslenme uzmanına danışın.'
    };
    
    // Check if it's a specific question
    if (responses[question]) {
        return responses[question];
    }
    
    // Check for keywords for general responses
    if (question.toLowerCase().includes('ağrı') || question.toLowerCase().includes('acı')) {
        return 'Ağrı konusunda genel öneriler verebilirim ancak sürekli veya şiddetli ağrılar için mutlaka doktorunuza başvurun.<br><br><strong>🏥 Acil durumlar için en yakın sağlık kuruluşuna gidin.</strong>';
    }
    
    if (question.toLowerCase().includes('ilaç') || question.toLowerCase().includes('doz')) {
        return 'İlaç kullanımı konusunda sadece doktorunuz size doğru bilgi verebilir. İlaç dozları ve etkileşimleri kişiye özeldir.<br><br><strong>⚠️ Önemli:</strong> İlaç değişikliği için mutlaka doktorunuzla görüşün.';
    }
    
    if (question.toLowerCase().includes('kanser') || question.toLowerCase().includes('tümör')) {
        return 'Kanser ve tümör konularında sadece onkoloji uzmanları doğru bilgi verebilir.<br><br><strong>🏥 Bu konular için en yakın sağlık kuruluşuna gidip uzman doktor görüşü alın.</strong>';
    }
    
    // Default response for complex medical questions
    return 'Bu çok spesifik bir tıp sorusu. Bu tür sorular için:<br><br><strong>🩺 Doktorunuzla görüşün</strong><br><strong>🏥 En yakın sağlık kuruluşuna gidin</strong><br><br>Ben sadece genel sağlık bilgileri verebilirim. Teşhis ve tedavi için mutlaka uzman görüşü alın.';
}

function viewPatientRecords() {
    showNotification('Hasta kayıtları modülü geliştiriliyor...', 'info');
}

function openAIAssistant() {
    showNotification();
}

function viewReports() {
    showNotification('Raporlar modülü geliştiriliyor...', 'info');
}

// Dashboard ana sayfaya dönüş
function returnToDashboard() {
    // Muayene panelini gizle, dashboard'ı göster
    document.getElementById('patientSidebar').style.display = 'none';
    document.getElementById('examinationContent').style.display = 'none';
    document.getElementById('dashboardSidebar').style.display = 'block';
    document.getElementById('dashboardContent').style.display = 'block';
    
    showNotification('Dashboard\'a dönüldü.', 'info');
}

// New Patient Modal functions
function showAddPatientModal() {
    document.getElementById('newPatientModal').style.display = 'flex';
}

function closeAddPatientModal() {
    document.getElementById('newPatientModal').style.display = 'none';
    document.getElementById('newPatientForm').reset();
    document.getElementById('medicalHistoryDetail').classList.remove('show');
    document.getElementById('allergyDetail').classList.remove('show');
}

function saveNewPatient(event) {
    event.preventDefault();
    
    const formData = {
        name: document.getElementById('newPatientName').value,
        tc: document.getElementById('newPatientTC').value,
        age: document.getElementById('newPatientAge').value,
        gender: document.getElementById('newPatientGender').value,
        bloodType: document.getElementById('newPatientBloodType').value,
        medicalHistory: document.querySelector('input[name="medicalHistory"]:checked').value === 'yes' ? 
            document.getElementById('newPatientMedicalHistory').value : '',
        smoking: document.querySelector('input[name="smoking"]:checked').value,
        allergy: document.querySelector('input[name="allergy"]:checked').value === 'yes' ? 
            document.getElementById('newPatientAllergy').value : ''
    };
    
    const newPatientId = Math.max(...Object.keys(patientsData).map(Number)) + 1;
    
    patientsData[newPatientId] = {
        name: formData.name,
        tc: formData.tc,
        age: parseInt(formData.age),
        gender: formData.gender,
        bloodType: formData.bloodType,
        complaint: "",
        notes: []
    };
    
    // Add allergy note if exists
    if (formData.allergy) {
        patientsData[newPatientId].notes.push({
            type: "emphasis",
            text: "İlaç alerjisi: " + formData.allergy
        });
    }
    
    // Add smoking note if exists
    if (formData.smoking === 'yes') {
        patientsData[newPatientId].notes.push({
            type: "normal",
            text: "Sigara kullanımı mevcut."
        });
    }
    
    // Add to dropdown
    const patientOptions = document.getElementById('patientOptions');
    const newOption = document.createElement('div');
    newOption.className = 'patient-option';
    newOption.textContent = formData.name;
    newOption.onclick = function() { selectPatient(this, newPatientId, formData.name); };
    patientOptions.appendChild(newOption);
    
    // Select the new patient
    selectPatient(newOption, newPatientId, formData.name);
    
    closeAddPatientModal();
    showNotification('Yeni hasta başarıyla kaydedildi!', 'success');
}

// Medical history toggle function
function toggleMedicalHistoryDetail(show) {
    const detail = document.getElementById('medicalHistoryDetail');
    if (show) {
        detail.classList.add('show');
    } else {
        detail.classList.remove('show');
        document.getElementById('newPatientMedicalHistory').value = '';
    }
}

// Allergy toggle function
function toggleAllergyDetail(show) {
    const detail = document.getElementById('allergyDetail');
    if (show) {
        detail.classList.add('show');
    } else {
        detail.classList.remove('show');
        document.getElementById('newPatientAllergy').value = '';
    }
}

// Close modal when clicking outside
document.addEventListener('click', function(e) {
    if (e.target.id === 'loginModal') {
        closeLoginModal();
    }
});

// ESC tuşu ile modal kapatma
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        closeLoginModal();
    }
});

// Add enter key support for login
document.addEventListener('DOMContentLoaded', function() {
    // Login form enter key support
    const loginInputs = document.querySelectorAll('#username, #password');
    loginInputs.forEach(input => {
        input.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                document.getElementById('loginSubmit').click();
            }
        });
    });
});

// Suppress console errors for better user experience
window.addEventListener('error', function(e) {
    e.preventDefault();
    return false;
});

window.addEventListener('unhandledrejection', function(e) {
    e.preventDefault();
});

// Initialize test change listeners
function initializeTestListeners() {
    const testCheckboxes = document.querySelectorAll('.test-checklist input[type="checkbox"]');
    testCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            updateSelectedTests();
            
            // Add visual feedback
            const checkboxItem = this.closest('.checkbox-item');
            if (this.checked) {
                checkboxItem.style.background = 'rgba(76, 175, 80, 0.2)';
                checkboxItem.style.borderLeft = '4px solid #4CAF50';
            } else {
                checkboxItem.style.background = 'rgba(255, 255, 255, 0.05)';
                checkboxItem.style.borderLeft = 'none';
            }
        });
    });
}

// Close modal when clicking outside
document.addEventListener('click', function(e) {
    if (e.target.id === 'newPatientModal') {
        closeAddPatientModal();
    }
    if (e.target.id === 'loginModal') {
        closeLoginModal();
    }
});

// ESC tuşu ile modal kapatma
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        closeLoginModal();
        closeAddPatientModal();
        closeAIChatbot();
    }
});


// Add enter key support for chatbot and login
document.addEventListener('DOMContentLoaded', function() {
    // Initialize test listeners
    setTimeout(() => {
        initializeTestListeners();
        updateSelectedTests();
    }, 1000);
    
    // Add search functionality for tests
    const testSearchInput = document.getElementById('testSearchInput');
    if (testSearchInput) {
        testSearchInput.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase();
            const checkboxItems = document.querySelectorAll('.checkbox-item');
            
            checkboxItems.forEach(item => {
                const label = item.querySelector('label').textContent.toLowerCase();
                if (label.includes(searchTerm)) {
                    item.style.display = 'flex';
                } else {
                    item.style.display = 'none';
                }
            });
        });
    }
    
    // Chatbot enter key support
    const chatbotInput = document.getElementById('chatbotInput');
    if (chatbotInput) {
        chatbotInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });
    }

    // Login form enter key support
    const loginInputs = document.querySelectorAll('#username, #password');
    loginInputs.forEach(input => {
        input.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                document.getElementById('loginSubmit').click();
            }
        });
    });
});

// Suppress console errors for better user experience
window.addEventListener('error', function(e) {
    e.preventDefault();
    return false;
});

window.addEventListener('unhandledrejection', function(e) {
    e.preventDefault();
});