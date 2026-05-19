document.addEventListener('DOMContentLoaded', () => {
    // --- STATE & CONSTANTS ---
    const API_URL = 'https://petcare-api-backend.onrender.com';
    const loggedUserId = localStorage.getItem('petcareplus_user_id');
    const loggedUserTipo = localStorage.getItem('petcareplus_user_tipo') || 'tutor';
    const TUTOR_ID_TESTE = parseInt(loggedUserId) || 1; // Fallback for testing UI without login

    let state = {
        pets: [],
        contacts: { vet: '', emergency: '' },
        currentPetId: null,
        editingRecordId: null,
    };
    let socket;

    // --- DOM ELEMENTS ---
    const pages = document.querySelectorAll('.page');
    const petForm = document.getElementById('pet-form');
    const recordModal = document.getElementById('record-modal');
    const recordForm = document.getElementById('record-form');
    const docModal = document.getElementById('doc-modal');
    const docForm = document.getElementById('doc-form');

    // --- NAVIGATION & UI HELPERS ---
    const navigateTo = (pageId) => {
        pages.forEach(page => page.classList.remove('active'));
        const targetPage = document.getElementById(pageId);
        if(targetPage) {
            targetPage.classList.add('active');
            window.scrollTo({ top: 0, behavior: 'smooth' });
            
            // Re-trigger animations
            const animatedElements = targetPage.querySelectorAll('.fade-in-up, .stagger-list > *');
            animatedElements.forEach(el => {
                el.style.animation = 'none';
                el.offsetHeight; /* trigger reflow */
                el.style.animation = null; 
            });
        }
    };

    const getPetAge = (birthdate) => {
        if (!birthdate) return 'Idade não informada';
        const birthDate = new Date(birthdate);
        const today = new Date();
        let years = today.getFullYear() - birthDate.getFullYear();
        let months = today.getMonth() - birthDate.getMonth();
        if (months < 0 || (months === 0 && today.getDate() < birthDate.getDate())) {
            years--; months += 12;
        }
        return years > 0 ? `${years} ano(s) e ${months} mês(es)` : `${months} mês(es)`;
    };

    const showToast = (msg, icon = 'ph-bell-ringing') => {
        const container = document.getElementById('toast-container');
        const toast = document.createElement('div');
        toast.className = 'toast-msg';
        toast.innerHTML = `<i class="ph ${icon}"></i> <span>${msg}</span>`;
        container.appendChild(toast);
        setTimeout(() => toast.remove(), 5000);
    };

    window.logout = () => {
        localStorage.removeItem('petcareplus_user_id');
        localStorage.removeItem('petcareplus_user_tipo');
        window.location.href = 'login.html'; // Adjust based on actual flow
    };

    // --- WEBSOCKETS ---
    const connectWebSocket = () => {
        if (!loggedUserId) return;
        const wsUrl = API_URL.replace('http://', 'ws://').replace('https://', 'wss://');
        
        try {
            socket = new WebSocket(`${wsUrl}/ws/${loggedUserId}`);
            socket.onmessage = async (event) => {
                const badge = document.getElementById('notification-badge');
                if (badge) badge.style.display = 'block';
                showToast(event.data);
                
                await loadStateFromAPI();
                if (state.currentPetId && document.getElementById('pet-details-page').classList.contains('active')) {
                    renderPetDetails();
                }
            };
            socket.onclose = () => setTimeout(connectWebSocket, 5000);
        } catch (e) {
            console.warn("WebSocket não conectado (offline mode).");
        }
    };

    document.getElementById('notification-btn')?.addEventListener('click', () => {
        const badge = document.getElementById('notification-badge');
        if (badge) badge.style.display = 'none';
        showToast("Você não tem novas notificações.", "ph-bell-z");
    });

    // --- API COMMUNICATION ---
    const loadStateFromAPI = async () => {
        try {
            let urlDaApi = loggedUserTipo === 'veterinario' 
                ? `${API_URL}/pets/` 
                : `${API_URL}/usuarios/${TUTOR_ID_TESTE}/pets/`;

            const response = await fetch(urlDaApi);
            if (response.ok) {
                const petsDB = await response.json();
                
                const mapRecord = r => ({
                    id: r.id, name: r.nome, date: r.data, nextDate: r.proxima_data,
                    vet: r.anotacoes, weight: r.peso, notes: r.anotacoes
                });

                state.pets = petsDB.map(p => ({
                    id: p.id, name: p.nome, species: p.especie, breed: p.raca,
                    microchip: p.microchip, birthdate: p.data_nascimento, sex: p.sexo, photo: p.foto,
                    vaccines: p.registros.filter(r => r.tipo === 'vacina').map(mapRecord),
                    parasites: p.registros.filter(r => r.tipo === 'parasita').map(mapRecord),
                    consults: p.registros.filter(r => r.tipo === 'consulta').map(mapRecord),
                    weights: p.registros.filter(r => r.tipo === 'peso').map(mapRecord),
                    documents: p.registros.filter(r => r.tipo === 'documento').map(mapRecord),
                }));
                
                loggedUserTipo === 'veterinario' ? renderVetDashboard() : renderDashboard();
            }
        } catch (error) {
            console.error("Erro ao carregar dados da API:", error);
            // Fallback for UI testing if API is down
            if (state.pets.length === 0) {
               showToast("Trabalhando em modo offline", "ph-wifi-slash");
            }
        }

        const localContacts = localStorage.getItem('petcareplus_contacts');
        if (localContacts) state.contacts = JSON.parse(localContacts);
    };

    const saveLocalContacts = () => localStorage.setItem('petcareplus_contacts', JSON.stringify(state.contacts));

    // --- RENDER FUNCTIONS ---
    const renderDashboard = () => {
        renderReminders();
        const petList = document.getElementById('pet-list');
        petList.innerHTML = '';
        
        const countEl = document.getElementById('pet-count');
        if(countEl) countEl.textContent = `${state.pets.length} Pet${state.pets.length !== 1 ? 's' : ''}`;

        if (state.pets.length === 0) {
            petList.innerHTML = `
                <div class="empty-state">
                    <i class="ph-fill ph-ghost"></i>
                    <p>Nenhum pet encontrado.<br>Que tal adicionar seu primeiro amigo?</p>
                </div>`;
            return;
        }

        state.pets.forEach(pet => {
            const card = document.createElement('div');
            card.className = 'pet-card';
            card.dataset.petId = pet.id;
            card.innerHTML = `
                <img src="${pet.photo || 'assets/placeholder.svg'}" alt="${pet.name}" class="pet-card-photo" onerror="this.src='assets/placeholder.svg'">
                <div class="pet-card-info">
                    <h3>${pet.name}</h3>
                    <p><i class="ph ph-paw-print"></i> ${pet.species} ${pet.breed ? ` • ${pet.breed}` : ''}</p>
                </div>
                <i class="ph ph-caret-right text-muted" style="font-size: 1.2rem;"></i>`;
            card.addEventListener('click', () => {
                state.currentPetId = pet.id;
                renderPetDetails();
                navigateTo('pet-details-page');
            });
            petList.appendChild(card);
        });
    };

    const renderVetDashboard = () => {
        const petList = document.getElementById('vet-pet-list');
        petList.innerHTML = '';
        const countEl = document.getElementById('vet-pet-count');
        if(countEl) countEl.textContent = `${state.pets.length} Pacientes`;

        if (state.pets.length === 0) {
            petList.innerHTML = `<div class="empty-state"><i class="ph-fill ph-folder-open"></i><p>Nenhum paciente cadastrado.</p></div>`;
            return;
        }

        state.pets.forEach(pet => {
            const card = document.createElement('div');
            card.className = 'pet-card vet-style';
            card.innerHTML = `
                <img src="${pet.photo || 'assets/placeholder.svg'}" alt="${pet.name}" class="pet-card-photo" style="border-color: var(--vet-color)" onerror="this.src='assets/placeholder.svg'">
                <div class="pet-card-info">
                    <h3 class="text-vet">${pet.name}</h3>
                    <p><i class="ph ph-tag"></i> Espécie: ${pet.species}</p>
                    <p style="font-size: 0.8rem; margin-top: 4px;"><i class="ph ph-barcode"></i> ${pet.microchip || 'Sem microchip'}</p>
                </div>
                <div class="status-badge clinical"><i class="ph ph-file-text"></i> Prontuário</div>`;
            card.addEventListener('click', () => {
                state.currentPetId = pet.id;
                renderPetDetails();
                navigateTo('pet-details-page');
            });
            petList.appendChild(card);
        });
    };

    const renderReminders = () => {
        const remindersList = document.getElementById('reminders-list');
        remindersList.innerHTML = '';
        const reminders = [];
        const today = new Date();
        today.setHours(0, 0, 0, 0);

        state.pets.forEach(pet => {
            ['vaccines', 'parasites'].forEach(type => {
                (pet[type] || []).forEach(record => {
                    if (record.nextDate) {
                        const nextDate = new Date(record.nextDate + 'T00:00:00');
                        const diffDays = Math.ceil((nextDate - today) / (1000 * 60 * 60 * 24));
                        if (diffDays <= 30 && diffDays >= 0) {
                            reminders.push({ petName: pet.name, recordName: record.name, diffDays, vet: record.vet });
                        }
                    }
                });
            });
        });
        
        if (reminders.length === 0) {
            remindersList.innerHTML = '<p class="text-muted" style="font-size:0.9rem;"><i class="ph ph-check-circle"></i> Tudo em dia! Nenhum lembrete para os próximos 30 dias.</p>';
            return;
        }

        reminders.sort((a, b) => a.diffDays - b.diffDays).forEach(r => {
            const card = document.createElement('div');
            card.className = 'reminder-card';
            const reminderText = r.diffDays === 0 ? 'é hoje!' : `vence em ${r.diffDays} dia(s)`;
            card.innerHTML = `
                <i class="ph-fill ph-warning-circle"></i>
                <div>
                    <strong>${r.petName}</strong>: ${r.recordName}<br>
                    <span style="font-size: 0.85rem; opacity: 0.8;">${reminderText}${r.vet ? ` na ${r.vet}` : ''}</span>
                </div>`;
            remindersList.appendChild(card);
        });
    };

    const renderPetDetails = () => {
        const pet = state.pets.find(p => p.id === state.currentPetId);
        if (!pet) return navigateTo('dashboard-page');

        document.getElementById('details-pet-name').textContent = pet.name;
        document.getElementById('details-content').innerHTML = `
            <img id="details-photo" src="${pet.photo || 'assets/placeholder.svg'}" alt="${pet.name}" onerror="this.src='assets/placeholder.svg'">
            <h2>${pet.name}</h2>
            <p>${pet.species} ${pet.breed ? ` • ${pet.breed}` : ''}</p>
            <div class="badges">
                <span class="status-badge neutral"><i class="ph ph-gender-${pet.sex === 'Fêmea' ? 'female' : 'male'}"></i> ${pet.sex || 'N/I'}</span>
                <span class="status-badge neutral"><i class="ph ph-calendar"></i> ${getPetAge(pet.birthdate)}</span>
                ${pet.microchip ? `<span class="status-badge clinical"><i class="ph ph-barcode"></i> Chip OK</span>` : ''}
            </div>
            <div class="action-buttons mt-4" style="width:100%;">
                <button id="edit-pet-btn" class="btn btn-secondary btn-outline" style="flex:1;"><i class="ph ph-pencil-simple"></i> Editar</button>
                <button id="delete-pet-btn" class="btn btn-secondary" style="color: var(--danger);"><i class="ph ph-trash"></i></button>
            </div>`;
        
        ['vaccine', 'parasite', 'consult', 'weight', 'documento'].forEach(type => {
            renderRecordList(type, pet[type + 's'] || (type==='documento'? pet.documents : []));
        });

        const btnEmitirDoc = document.getElementById('btn-emitir-doc');
        if (btnEmitirDoc) btnEmitirDoc.style.display = loggedUserTipo === 'veterinario' ? 'flex' : 'none';
        
        // Reset Tabs to first
        document.querySelector('.tab-link[data-tab="tab-vaccines"]').click();
    };
    
    const renderRecordList = (type, records) => {
        const listContainer = document.getElementById({
            vaccine: 'vaccine-list', parasite: 'parasite-list', consult: 'consult-list', weight: 'weight-list', documento: 'doc-list'
        }[type]);
        
        if(!listContainer) return;
        listContainer.innerHTML = '';
        
        if (!records || records.length === 0) {
            listContainer.innerHTML = '<div class="empty-state" style="padding: 1.5rem;"><i class="ph-fill ph-file-dashed"></i><p>Nenhum registro.</p></div>';
            return;
        }
        
        records.sort((a, b) => new Date(b.date) - new Date(a.date));

        records.forEach(record => {
            const card = document.createElement('div');
            card.className = type === 'documento' ? 'record-card doc-card' : 'record-card';
            const formattedDate = new Date(record.date + 'T00:00:00').toLocaleDateString('pt-BR');
            let content = `<div class="record-info"><h4>${record.name}</h4><p><i class="ph ph-calendar-blank"></i> ${formattedDate}</p>`;
            
            if (['vaccine', 'parasite'].includes(type)) {
                if (record.vet) content += `<p><i class="ph ph-map-pin"></i> ${record.vet}</p>`;
                if (record.nextDate) content += `<p class="mt-2"><span class="status-badge warning"><i class="ph ph-clock"></i> Próxima: ${new Date(record.nextDate + 'T00:00:00').toLocaleDateString('pt-BR')}</span></p>`;
            } else if (type === 'consult') {
                if (record.vet) content += `<p><i class="ph ph-map-pin"></i> ${record.vet}</p>`;
                if (record.notes) content += `<p class="mt-2 text-muted monospace">${record.notes}</p>`;
            } else if (type === 'weight') {
                content = `<div class="record-info"><h4>${record.weight} kg</h4><p><i class="ph ph-calendar-blank"></i> ${formattedDate}</p>`;
            } else if (type === 'documento') {
                content = `<div class="record-info" style="width:100%;">
                    <h4><i class="ph ph-file-text"></i> ${record.name}</h4>
                    <p><i class="ph ph-calendar-blank"></i> Emitido em ${formattedDate}</p>
                    <div class="mt-4 p-3 bg-light rounded monospace" style="border-radius:8px; padding:12px; white-space: pre-wrap; font-size:0.9rem; color:var(--text-color); border:1px solid var(--border-color);">${record.notes || ''}</div>`;
            }
            content += `</div>`;

            let actionButtons = `
                <div class="record-actions">
                    <button class="edit-record-btn" data-id="${record.id}" data-type="${type}"><i class="ph ph-pencil-simple"></i></button>
                    <button class="delete-record-btn delete-btn" data-id="${record.id}" data-type="${type}"><i class="ph ph-trash"></i></button>
                </div>`;
            
            if (type === 'documento' && loggedUserTipo === 'tutor') actionButtons = ''; 

            card.innerHTML = content + actionButtons;
            listContainer.appendChild(card);
        });
    };

    const renderSettingsPage = () => {
        document.getElementById('contact-vet').value = state.contacts.vet || '';
        document.getElementById('contact-emergency').value = state.contacts.emergency || '';
    };

    // --- SEARCH / FILTERS ---
    window.filterPets = () => {
        const input = document.getElementById('search-pet-input').value.toLowerCase();
        document.querySelectorAll('#pet-list .pet-card').forEach(card => {
            const text = card.textContent.toLowerCase();
            card.style.display = text.includes(input) ? 'flex' : 'none';
        });
    };

    window.filterVetPets = () => {
        const input = document.getElementById('search-vet-input').value.toLowerCase();
        document.querySelectorAll('#vet-pet-list .pet-card').forEach(card => {
            const text = card.textContent.toLowerCase();
            card.style.display = text.includes(input) ? 'flex' : 'none';
        });
    };

    // --- FORMS & MODALS LOGIC ---
    petForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const id = document.getElementById('pet-id').value;
        const photoSrc = document.getElementById('pet-photo-preview').src;
        const petData = {
            nome: document.getElementById('pet-name').value,
            especie: document.getElementById('pet-species').value,
            microchip: document.getElementById('pet-microchip').value || null,
            raca: document.getElementById('pet-breed').value || null,
            data_nascimento: document.getElementById('pet-birthdate').value || null,
            sexo: document.getElementById('pet-sex').value,
            foto: photoSrc.includes('placeholder.svg') ? null : photoSrc
        };

        try {
            const method = id ? 'PUT' : 'POST';
            const url = id ? `${API_URL}/pets/${id}` : `${API_URL}/usuarios/${TUTOR_ID_TESTE}/pets/`;
            const res = await fetch(url, { method, headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(petData) });
            
            if (res.ok) {
                await loadStateFromAPI();
                navigateTo('dashboard-page');
                showToast(`Pet ${id ? 'atualizado' : 'adicionado'} com sucesso!`, "ph-check-circle");
            } else { throw new Error(await res.text()); }
        } catch (error) { showToast("Erro ao salvar pet. Tente novamente.", "ph-warning"); }
    });

    recordForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const type = document.getElementById('record-type').value;
        const recordData = {
            tipo: { vaccine: 'vacina', parasite: 'parasita', consult: 'consulta', weight: 'peso' }[type],
            nome: document.getElementById('record-name').value || 'Registro',
            data: document.getElementById('record-date').value,
            proxima_data: document.getElementById('record-next-date').value || null,
            peso: document.getElementById('record-weight').value ? parseFloat(document.getElementById('record-weight').value) : null,
            anotacoes: type === 'consult' 
                ? [document.getElementById('record-vet').value, document.getElementById('record-notes').value].filter(Boolean).join(' | ') || null
                : document.getElementById('record-vet').value || null
        };

        try {
            const id = document.getElementById('record-id').value;
            const method = id ? 'PUT' : 'POST';
            const url = id ? `${API_URL}/registros/${id}` : `${API_URL}/pets/${state.currentPetId}/registros/`;
            
            const res = await fetch(url, { method, headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(recordData) });
            if (res.ok) {
                await loadStateFromAPI();
                renderPetDetails();
                recordModal.classList.remove('visible');
                showToast("Registro salvo!");
            } else { throw new Error(); }
        } catch (e) { showToast("Erro ao salvar registro.", "ph-warning"); }
    });

    docForm?.addEventListener('submit', async (e) => {
        e.preventDefault();
        const recordData = {
            tipo: 'documento',
            nome: `${document.getElementById('doc-type').value} - ${document.getElementById('doc-vet-name').value}`,
            data: document.getElementById('doc-date').value,
            proxima_data: null, peso: null,
            anotacoes: document.getElementById('doc-content').value
        };
        try {
            const res = await fetch(`${API_URL}/pets/${state.currentPetId}/registros/`, {
                method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(recordData)
            });
            if (res.ok) {
                await loadStateFromAPI();
                renderPetDetails();
                docModal.classList.remove('visible');
                showToast("Documento emitido e enviado ao tutor!", "ph-paper-plane-right");
            } else { throw new Error(); }
        } catch(e) { showToast("Erro ao emitir doc.", "ph-warning"); }
    });

    const openRecordModal = (type, record = null) => {
        recordForm.reset();
        document.getElementById('record-type').value = type;
        recordForm.querySelectorAll('.form-group[data-field]').forEach(el => el.style.display = 'none');
        
        const configs = {
            vaccine: { title: 'Vacina', fields: ['vet', 'next-date'] },
            parasite: { title: 'Controle Parasitário', fields: ['vet', 'next-date'] },
            consult: { title: 'Consulta', fields: ['vet', 'notes'] },
            weight: { title: 'Peso', fields: ['weight'] }
        };
        const config = configs[type];
        document.getElementById('modal-title').textContent = (record ? 'Editar ' : 'Novo(a) ') + config.title;

        const nameInput = document.getElementById('record-name');
        if (type === 'weight') {
            nameInput.parentElement.style.display = 'none'; nameInput.required = false;
        } else {
            nameInput.parentElement.style.display = 'block'; nameInput.required = true;
        }

        config.fields.forEach(f => recordForm.querySelector(`.form-group[data-field="${f}"]`).style.display = 'block');

        if (record) {
            document.getElementById('record-id').value = record.id;
            document.getElementById('record-name').value = record.name;
            document.getElementById('record-date').value = record.date;
            document.getElementById('record-next-date').value = record.nextDate || '';
            document.getElementById('record-vet').value = record.vet || '';
            document.getElementById('record-weight').value = record.weight || '';
            document.getElementById('record-notes').value = record.notes || '';
        } else {
            document.getElementById('record-id').value = '';
            document.getElementById('record-date').value = new Date().toISOString().split('T')[0];
        }
        
        recordModal.classList.add('visible');
    };

    // --- ACCESSIBILITY WIDGET ---
    let a11ySettings = JSON.parse(localStorage.getItem('petcareplus_a11y')) || { highContrast: false, largeText: false, dyslexiaFont: false, highlightLinks: false };
    
    const applyA11y = () => {
        document.body.classList.toggle('high-contrast', a11ySettings.highContrast);
        document.documentElement.classList.toggle('large-text', a11ySettings.largeText); 
        document.body.classList.toggle('dyslexia-font', a11ySettings.dyslexiaFont);
        document.body.classList.toggle('highlight-links', a11ySettings.highlightLinks);
        
        ['contrast', 'largeText', 'dyslexiaFont', 'highlightLinks'].forEach(k => {
            const el = document.getElementById(`toggle-${k.replace(/[A-Z]/g, m => '-' + m.toLowerCase())}`);
            if(el) el.setAttribute('aria-checked', a11ySettings[k]);
        });
        localStorage.setItem('petcareplus_a11y', JSON.stringify(a11ySettings));
    };

    document.getElementById('accessibility-btn').addEventListener('click', (e) => {
        const btn = e.currentTarget;
        const isExpanded = btn.getAttribute('aria-expanded') === 'true';
        btn.setAttribute('aria-expanded', !isExpanded);
        document.getElementById('accessibility-panel').classList.toggle('visible');
    });

    ['contrast', 'largeText', 'dyslexiaFont', 'highlightLinks'].forEach(k => {
        document.getElementById(`toggle-${k.replace(/[A-Z]/g, m => '-' + m.toLowerCase())}`)?.addEventListener('click', () => {
            a11ySettings[k] = !a11ySettings[k]; applyA11y();
        });
    });

    // --- GLOBAL EVENT LISTENERS (DELEGATION) ---
    document.body.addEventListener('click', async (e) => {
        // Navigation Buttons
        const backBtn = e.target.closest('.back-btn');
        if (backBtn) {
            let target = backBtn.dataset.target;
            if (target === 'dashboard-page' && loggedUserTipo === 'veterinario') target = 'vet-dashboard-page';
            navigateTo(target);
        }

        // Tabs Logic
        if (e.target.closest('.tab-link')) {
            const tabBtn = e.target.closest('.tab-link');
            const nav = tabBtn.closest('.tabs-nav');
            const indicator = nav.querySelector('.tab-indicator');
            
            nav.querySelectorAll('.tab-link').forEach(t => t.classList.remove('active'));
            tabBtn.classList.add('active');
            
            // Move indicator
            indicator.style.width = `${tabBtn.offsetWidth}px`;
            indicator.style.transform = `translateX(${tabBtn.offsetLeft}px)`;
            
            document.querySelectorAll('.tab-content').forEach(c => {
                c.classList.remove('active');
                c.classList.remove('fade-in');
            });
            const targetContent = document.getElementById(tabBtn.dataset.tab);
            targetContent.classList.add('active');
            // Re-trigger animation
            setTimeout(() => targetContent.classList.add('fade-in'), 10);
        }

        // Add Pet
        if (e.target.closest('#add-pet-btn-dashboard')) {
            petForm.reset();
            document.getElementById('pet-id').value = '';
            document.getElementById('pet-photo-preview').src = 'assets/placeholder.svg';
            document.getElementById('remove-photo-btn').style.display = 'none';
            document.getElementById('form-title').textContent = 'Adicionar Pet';
            navigateTo('pet-form-page');
        }

        // Photo Upload Proxy
        if (e.target.closest('#select-photo-btn') || e.target.closest('.photo-preview-wrapper')) {
            document.getElementById('pet-photo').click();
        }
        
        // Settings
        if (e.target.closest('#settings-btn')) { renderSettingsPage(); navigateTo('settings-page'); }
        
        // Start App
        if (e.target.closest('#start-app-btn')) {
            localStorage.setItem('petcareplus_visited', 'true');
            navigateTo(loggedUserTipo === 'veterinario' ? 'vet-dashboard-page' : 'dashboard-page');
        }

        // Edit Pet
        if (e.target.closest('#edit-pet-btn')) {
            const pet = state.pets.find(p => p.id === state.currentPetId);
            document.getElementById('form-title').textContent = 'Editar Pet';
            document.getElementById('pet-id').value = pet.id;
            ['name', 'species', 'microchip', 'breed', 'birthdate', 'sex'].forEach(f => document.getElementById(`pet-${f}`).value = pet[f] || '');
            
            const photoPreview = document.getElementById('pet-photo-preview');
            const removeBtn = document.getElementById('remove-photo-btn');
            if (pet.photo) { photoPreview.src = pet.photo; removeBtn.style.display = 'inline-flex'; }
            else { photoPreview.src = 'assets/placeholder.svg'; removeBtn.style.display = 'none'; }
            navigateTo('pet-form-page');
        }

        // Delete Pet
        if (e.target.closest('#delete-pet-btn')) {
            if(confirm('Atenção: Excluir este pet apagará todos os seus registros permanentemente. Continuar?')) {
                try {
                    await fetch(`${API_URL}/pets/${state.currentPetId}`, { method: 'DELETE' });
                    await loadStateFromAPI(); navigateTo('dashboard-page'); showToast("Pet excluído.");
                } catch(e) { showToast("Erro ao excluir", "ph-warning"); }
            }
        }

        // Records Modals Interactions
        if (e.target.closest('.add-record-btn')) openRecordModal(e.target.closest('.add-record-btn').dataset.type);
        if (e.target.closest('.edit-record-btn')) {
            const btn = e.target.closest('.edit-record-btn');
            const { id, type } = btn.dataset;
            if(type === 'documento') return; // Cannot edit official docs this way
            const recordArray = `${type}s`;
            const pet = state.pets.find(p => p.id === state.currentPetId);
            openRecordModal(type, pet[recordArray].find(r => r.id == id));
        }
        if (e.target.closest('.delete-record-btn')) {
            if(confirm('Excluir este registro?')) {
                const btn = e.target.closest('.delete-record-btn');
                try {
                    await fetch(`${API_URL}/registros/${btn.dataset.id}`, { method: 'DELETE' });
                    await loadStateFromAPI(); renderPetDetails(); showToast("Registro excluído.");
                } catch(e) {}
            }
        }

        if (e.target.closest('.close-modal-btn') || e.target.closest('.cancel-modal-btn') || e.target.id === 'record-modal') {
            recordModal.classList.remove('visible');
        }
        
        if (e.target.closest('#btn-emitir-doc')) {
            docForm.reset();
            document.getElementById('doc-date').value = new Date().toISOString().split('T')[0];
            docModal.classList.add('visible');
        }
        if (e.target.closest('.close-doc-btn') || e.target.closest('.cancel-doc-btn') || e.target.id === 'doc-modal') {
            docModal.classList.remove('visible');
        }
    });

    // Handle Image file input
    document.getElementById('pet-photo').addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = (ev) => { 
                document.getElementById('pet-photo-preview').src = ev.target.result;
                document.getElementById('remove-photo-btn').style.display = 'inline-flex';
            };
            reader.readAsDataURL(file);
        }
    });
    document.getElementById('remove-photo-btn').addEventListener('click', () => {
        document.getElementById('pet-photo-preview').src = 'assets/placeholder.svg';
        document.getElementById('pet-photo').value = '';
        document.getElementById('remove-photo-btn').style.display = 'none';
    });

    // Contacts Save
    document.getElementById('contacts-form')?.addEventListener('submit', (e) => {
        e.preventDefault();
        state.contacts.vet = document.getElementById('contact-vet').value;
        state.contacts.emergency = document.getElementById('contact-emergency').value;
        saveLocalContacts(); showToast('Contatos salvos com sucesso!');
    });

    // Initialize Tab Indicator on Window Resize
    window.addEventListener('resize', () => {
        const activeTab = document.querySelector('.tab-link.active');
        if (activeTab) {
            const indicator = document.querySelector('.tab-indicator');
            indicator.style.width = `${activeTab.offsetWidth}px`;
            indicator.style.transform = `translateX(${activeTab.offsetLeft}px)`;
        }
    });

    // --- INIT ---
    const init = async () => {
        applyA11y();
        connectWebSocket();
        await loadStateFromAPI();
        
        // Initial Tab setup
        setTimeout(() => window.dispatchEvent(new Event('resize')), 100);

        if (localStorage.getItem('petcareplus_visited')) {
            navigateTo(loggedUserTipo === 'veterinario' ? 'vet-dashboard-page' : 'dashboard-page');
        } else {
            navigateTo('welcome-page');
        }
    };
    
    init();
});