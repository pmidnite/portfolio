// app/static/js/admin.js

// Global State management
const state = {
  token: localStorage.getItem('admin_token') || '',
  currentTab: 'tab-dashboard',
  profileEmail: ''
};

// In-memory lists to track records without rendering database IDs in HTML attributes
let experiencesList = [];
let educationsList = [];
let skillsList = [];
let certsList = [];
let testimonialsList = [];
let messagesList = [];

// Helper: Escape HTML strings to prevent XSS/Injection
function escapeHtml(str) {
  if (str === null || str === undefined) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

let onConfirmCallback = null;
function showConfirmModal(title, message, onConfirm) {
  document.getElementById('confirmModalTitle').textContent = title;
  document.getElementById('confirmModalMessage').textContent = message;
  onConfirmCallback = onConfirm;
  bootstrap.Modal.getOrCreateInstance(document.getElementById('confirmModal')).show();
}

// Helper: Toast Display
function showToast(message, isError = false) {
  const container = document.getElementById('toastContainer');
  const toast = document.createElement('div');
  toast.className = `custom-toast ${isError ? 'error' : ''}`;
  toast.innerHTML = `
    <div class="d-flex align-items-center">
      <i class="bi ${isError ? 'bi-exclamation-triangle-fill text-danger' : 'bi-check-circle-fill text-success'} me-2"></i>
      <span>${escapeHtml(message)}</span>
    </div>
    <button class="btn btn-close btn-close-white ms-3" style="padding: 0.25rem; font-size: 0.75rem;" onclick="this.parentElement.remove()"></button>
  `;
  container.appendChild(toast);
  setTimeout(() => {
    if (toast.parentElement) toast.remove();
  }, 4000);
}

// Initialize Page
document.addEventListener('DOMContentLoaded', () => {
  // Set Theme to Icon
  updateThemeIcon();

  // Confirmation Modal Action Handler
  document.getElementById('btnConfirmAction').addEventListener('click', async () => {
    if (onConfirmCallback) {
      await onConfirmCallback();
    }
    bootstrap.Modal.getOrCreateInstance(document.getElementById('confirmModal')).hide();
  });

  // Check Session
  if (state.token) {
    document.getElementById('loginOverlay').classList.add('d-none');
    loadAllData();
  }

  // Login Form handler
  document.getElementById('loginForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const btn = document.getElementById('btnLogin');
    const txt = document.getElementById('loginText');

    btn.disabled = true;
    txt.textContent = 'Signing in...';

    try {
      const res = await fetch('/get_token', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
      });
      const data = await res.json();
      if (data.success) {
        state.token = data.data.access_token;
        localStorage.setItem('admin_token', state.token);
        document.getElementById('loginOverlay').classList.add('d-none');
        showToast('Authenticated successfully.');
        loadAllData();
      } else {
        showToast(data.message || 'Authentication failed', true);
      }
    } catch (err) {
      showToast('Network error during login.', true);
    } finally {
      btn.disabled = false;
      txt.textContent = 'Sign In';
    }
  });

  // Profile Form Handler
  document.getElementById('profileForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const payload = {
      "Email": document.getElementById('prof-email').value,
      "City": document.getElementById('prof-city').value,
      "Current Company": document.getElementById('prof-company').value,
      "Current Designation": document.getElementById('prof-designation').value,
      "Degree": document.getElementById('prof-degree').value,
      "Description": document.getElementById('prof-desc').value,
      "Phone": document.getElementById('prof-phone').value,
      "Self Facts": document.getElementById('prof-facts').value,
      "Short Description": document.getElementById('prof-short-desc').value,
      "Summary": document.getElementById('prof-summary').value,
      "Website": document.getElementById('prof-website').value
    };

    const res = await request('/api/about', 'POST', payload);
    if (res) {
      showToast('Profile updated successfully.');
      loadProfile();
    }
  });

  // Skill Form Handler
  document.getElementById('skillForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const isEditing = document.getElementById('skillFormTitle').textContent.includes('Edit');
    const skillName = document.getElementById('skill-name').value;
    const skillLogo = document.getElementById('skill-logo').value;
    
    const payload = {
      "Skill Name": skillName,
      "Skill Logo": skillLogo
    };
    
    const res = await request('/api/skill', 'POST', [payload]);
    
    if (res) {
      if (state.profileEmail && !isEditing) {
        const currentMapped = await request('/api/skill/mapping/exact') || [];
        const names = currentMapped.map(s => s["Skill Name"]);
        if (!names.includes(skillName)) {
          names.push(skillName);
        }
        await request('/api/skill/mapping', 'POST', {
          "Email": state.profileEmail,
          "Skill Names": names.join(',')
        });
      }
      showToast(isEditing ? `Skill '${skillName}' updated.` : `Skill '${skillName}' registered and mapped.`);
      cancelSkillEdit();
      loadSkills();
      loadStats();
    }
  });

  // Certificate Form Handler
  document.getElementById('certForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const isEditing = document.getElementById('certFormTitle').textContent.includes('Edit');
    const certName = document.getElementById('cert-name').value;
    const authority = document.getElementById('cert-authority').value;
    const certType = document.getElementById('cert-type').value;
    const certImage = document.getElementById('cert-image').value;
    const certUrl = document.getElementById('cert-url').value || '';
    
    const payload = {
      "Cert Name": certName,
      "Authority": authority,
      "Cert Type": certType,
      "Cert Logo": certImage,
      "Cert Url": certUrl
    };
    
    const res = await request('/api/certification', 'POST', payload);
    if (res) {
      showToast(isEditing ? `Certification '${certName}' updated.` : `Certification '${certName}' added.`);
      cancelCertEdit();
      loadCerts();
    }
  });

  // Experience Form Handler
  document.getElementById('experienceForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const payload = [{
      "Email": state.profileEmail,
      "Designation": document.getElementById('exp-designation').value,
      "Company Name": document.getElementById('exp-company').value,
      "Start Year": document.getElementById('exp-start-year').value,
      "End Year": document.getElementById('exp-end-year').value,
      "Address": document.getElementById('exp-address').value,
      "Description": document.getElementById('exp-description').value
    }];

    const res = await request('/api/experience', 'POST', payload);
    if (res) {
      bootstrap.Modal.getInstance(document.getElementById('experienceModal')).hide();
      showToast('Experience record saved successfully.');
      loadExperience();
    }
  });

  // Education Form Handler
  document.getElementById('educationForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const payload = {
      "Email": state.profileEmail,
      "Degree": document.getElementById('edu-degree').value,
      "University": document.getElementById('edu-institution').value,
      "Start Year": document.getElementById('edu-start-year').value,
      "Passing Year": document.getElementById('edu-passing-year').value,
      "Address": document.getElementById('edu-address').value
    };

    const res = await request('/api/education', 'POST', payload);
    if (res) {
      bootstrap.Modal.getInstance(document.getElementById('educationModal')).hide();
      showToast('Education record saved successfully.');
      loadEducation();
    }
  });

  // Testimonial Edit Form Handler
  document.getElementById('testimonialEditForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const payload = {
      "Name": document.getElementById('test-name').value,
      "Email": document.getElementById('test-email').value,
      "Designation": document.getElementById('test-designation').value,
      "Company": document.getElementById('test-company').value,
      "Message": document.getElementById('test-message').value,
      "Reviewed": document.getElementById('test-reviewed').value === 'true'
    };

    const res = await request('/api/testimonial', 'POST', payload);
    if (res) {
      bootstrap.Modal.getInstance(document.getElementById('testimonialModal')).hide();
      showToast('Testimonial updated successfully.');
      loadTestimonials();
    }
  });
});

// Main API Requester
async function request(url, method = 'GET', body = null) {
  const headers = { 'Authorization': `Bearer ${state.token}` };
  if (body) {
    headers['Content-Type'] = 'application/json';
  }
  try {
    const options = { method, headers };
    if (body) options.body = JSON.stringify(body);
    const res = await fetch(url, options);
    if (res.status === 401 || res.status === 422) {
      logout();
      showToast('Session expired. Please log in again.', true);
      return null;
    }
    const data = await res.json();
    if (!data.success) {
      showToast(data.message || 'Error occurred.', true);
      return null;
    }
    return data.data || data;
  } catch (err) {
    showToast('Connection failed.', true);
    return null;
  }
}

// Loader Core Actions
function loadAllData() {
  loadProfile().then(() => {
    loadStats();
    loadExperience();
    loadEducation();
    loadSkills();
    loadCerts();
    loadTestimonials();
    loadMessages();
  });
}

async function loadStats() {
  const msgs = await request('/api/contact');
  const testimonies = await request('/api/testimonial/all');
  const skills = await request('/api/skill');
  
  if (msgs) document.getElementById('stat-messages').textContent = msgs.length;
  if (testimonies) document.getElementById('stat-testimonials').textContent = testimonies.filter(t => t["Reviewed"]).length;
  if (skills) document.getElementById('stat-skills').textContent = skills.length;
}

async function loadProfile() {
  const profile = await request('/api/about');
  if (profile) {
    state.profileEmail = profile["Email"] || '';
    document.getElementById('prof-email').value = profile["Email"] || '';
    document.getElementById('prof-city').value = profile["City"] || '';
    document.getElementById('prof-company').value = profile["Current Company"] || '';
    document.getElementById('prof-designation').value = profile["Current Designation"] || '';
    document.getElementById('prof-degree').value = profile["Degree"] || '';
    document.getElementById('prof-desc').value = profile["Description"] || '';
    document.getElementById('prof-phone').value = profile["Phone"] || '';
    document.getElementById('prof-facts').value = profile["Self Facts"] || '';
    document.getElementById('prof-short-desc').value = profile["Short Description"] || '';
    document.getElementById('prof-summary').value = profile["Summary"] || '';
    document.getElementById('prof-website').value = profile["Website"] || '';
  }
}

async function loadExperience() {
  const container = document.getElementById('experience-list');
  container.innerHTML = '<tr><td colspan="4" class="text-center">Loading...</td></tr>';
  const items = await request('/api/experience');
  experiencesList = items || [];
  if (items && items.length > 0) {
    container.innerHTML = items.map((item, index) => `
      <tr>
        <td><strong>${escapeHtml(item["Designation"])}</strong></td>
        <td>${escapeHtml(item["Company Name"])}</td>
        <td>${escapeHtml(item["Start Year"])} - ${escapeHtml(item["End Year"])}</td>
        <td>
          <button type="button" class="btn btn-sm btn-outline-info me-2" onclick="event.preventDefault(); editExperience(${index})"><i class="bi bi-pencil"></i></button>
          <button type="button" class="btn btn-sm btn-outline-danger" onclick="event.preventDefault(); event.stopPropagation(); deleteExperience(${index})"><i class="bi bi-trash"></i></button>
        </td>
      </tr>
    `).join('');
  } else {
    container.innerHTML = '<tr><td colspan="4" class="text-center text-muted">No records.</td></tr>';
  }
}

async function loadEducation() {
  const container = document.getElementById('education-list');
  container.innerHTML = '<tr><td colspan="4" class="text-center">Loading...</td></tr>';
  const items = await request('/api/education');
  educationsList = items || [];
  if (items && items.length > 0) {
    container.innerHTML = items.map((item, index) => `
      <tr>
        <td><strong>${escapeHtml(item["Degree"])}</strong></td>
        <td>${escapeHtml(item["University"])}</td>
        <td>${escapeHtml(item["Start Year"])} - ${escapeHtml(item["Passing Year"])}</td>
        <td>
          <button type="button" class="btn btn-sm btn-outline-info me-2" onclick="event.preventDefault(); editEducation(${index})"><i class="bi bi-pencil"></i></button>
          <button type="button" class="btn btn-sm btn-outline-danger" onclick="event.preventDefault(); event.stopPropagation(); deleteEducation(${index})"><i class="bi bi-trash"></i></button>
        </td>
      </tr>
    `).join('');
  } else {
    container.innerHTML = '<tr><td colspan="4" class="text-center text-muted">No records.</td></tr>';
  }
}

async function loadSkills() {
  const container = document.getElementById('skill-list');
  container.innerHTML = '<li class="text-center py-3 text-muted">Loading...</li>';
  const items = await request('/api/skill');
  skillsList = items || [];
  if (items && items.length > 0) {
    container.innerHTML = items.map((item, index) => `
      <li class="list-group-item d-flex justify-content-between align-items-center" style="background: transparent; border-bottom: 1px solid var(--border-color); color: var(--text-primary);">
        <div>
          <strong>${escapeHtml(item["Skill Name"])}</strong>
        </div>
        <div>
          <button type="button" class="btn btn-sm btn-link text-info me-2" onclick="event.preventDefault(); event.stopPropagation(); editSkill(${index})"><i class="bi bi-pencil"></i></button>
          <button type="button" class="btn btn-sm text-danger btn-link" onclick="event.preventDefault(); event.stopPropagation(); deleteSkill(${index})"><i class="bi bi-trash"></i></button>
        </div>
      </li>
    `).join('');
  } else {
    container.innerHTML = '<li class="text-center py-3 text-muted">No skills mapped.</li>';
  }
}

async function loadCerts() {
  const container = document.getElementById('cert-list');
  container.innerHTML = '<li class="text-center py-3 text-muted">Loading...</li>';
  const items = await request('/api/certification');
  certsList = items || [];
  if (items && items.length > 0) {
    container.innerHTML = items.map((item, index) => `
      <li class="list-group-item d-flex justify-content-between align-items-center" style="background: transparent; border-bottom: 1px solid var(--border-color); color: var(--text-primary);">
        <div>
          <strong>${escapeHtml(item["Cert Name"])}</strong>
          <small class="d-block text-muted">${escapeHtml(item["Authority"])} (${escapeHtml(item["Cert Type"])})</small>
        </div>
        <div>
          <button type="button" class="btn btn-sm btn-link text-info me-2" onclick="event.preventDefault(); event.stopPropagation(); editCert(${index})"><i class="bi bi-pencil"></i></button>
          <button type="button" class="btn btn-sm text-danger btn-link" onclick="event.preventDefault(); event.stopPropagation(); deleteCert(${index})"><i class="bi bi-trash"></i></button>
        </div>
      </li>
    `).join('');
  } else {
    container.innerHTML = '<li class="text-center py-3 text-muted">No certifications.</li>';
  }
}

async function loadTestimonials() {
  const container = document.getElementById('testimonial-list');
  container.innerHTML = '<tr><td colspan="5" class="text-center">Loading...</td></tr>';
  const items = await request('/api/testimonial/all');
  testimonialsList = items || [];
  if (items && items.length > 0) {
    container.innerHTML = items.map((item, index) => `
      <tr>
        <td><strong>${escapeHtml(item["Name"])}</strong></td>
        <td>${escapeHtml(item["Designation"])} (${escapeHtml(item["Company"] || 'Private')})</td>
        <td>
          <span class="badge ${item["Reviewed"] ? 'bg-success' : 'bg-warning'}">${item["Reviewed"] ? 'Approved' : 'Pending'}</span>
        </td>
        <td>
          <small class="text-muted">${escapeHtml((item["Message"] || '').substring(0, 50))}...</small>
          <button class="btn btn-link btn-sm p-0 ms-1" style="font-size: 0.8rem;" onclick="event.preventDefault(); readMore('testimonial', ${index})">Read</button>
        </td>
        <td class="text-nowrap">
          <button type="button" class="btn btn-sm btn-outline-success me-1" onclick="event.preventDefault(); event.stopPropagation(); reviewTestimonial(${index})">
            <i class="bi ${item["Reviewed"] ? 'bi-x-circle' : 'bi-check-circle'}"></i> ${item["Reviewed"] ? 'Reject' : 'Approve'}
          </button>
          <button type="button" class="btn btn-sm btn-outline-info me-1" onclick="event.preventDefault(); event.stopPropagation(); editTestimonial(${index})">
            <i class="bi bi-pencil"></i>
          </button>
          <button type="button" class="btn btn-sm btn-outline-danger" onclick="event.preventDefault(); event.stopPropagation(); deleteTestimonial(${index})">
            <i class="bi bi-trash"></i>
          </button>
        </td>
      </tr>
    `).join('');
  } else {
    container.innerHTML = '<tr><td colspan="5" class="text-center text-muted">No testimonials received.</td></tr>';
  }
}

async function loadMessages() {
  const container = document.getElementById('message-list');
  container.innerHTML = '<tr><td colspan="5" class="text-center">Loading...</td></tr>';
  const items = await request('/api/contact');
  messagesList = items || [];
  if (items && items.length > 0) {
    container.innerHTML = items.map((item, index) => `
      <tr>
        <td><strong>${escapeHtml(item["Name"])}</strong><br><small>${escapeHtml(item["Email"])}</small></td>
        <td>${escapeHtml(item["Designation"])} at ${escapeHtml(item["Company"])}</td>
        <td><small>${item["Contact Date"] ? new Date(item["Contact Date"]).toLocaleString() : 'N/A'}</small></td>
        <td>
          <small class="text-muted">${escapeHtml((item["Message"] || '').substring(0, 50))}...</small>
          <button class="btn btn-link btn-sm p-0 ms-1" style="font-size: 0.8rem;" onclick="event.preventDefault(); readMore('message', ${index})">Read</button>
        </td>
        <td class="text-nowrap">
          <button type="button" class="btn btn-sm btn-outline-danger" onclick="event.preventDefault(); event.stopPropagation(); deleteMessage(${index})"><i class="bi bi-trash"></i></button>
        </td>
      </tr>
    `).join('');
  } else {
    container.innerHTML = '<tr><td colspan="5" class="text-center text-muted">No messages in inbox.</td></tr>';
  }
}

// Action Methods
async function deleteExperience(index) {
  const item = experiencesList[index];
  if (!item) return;
  showConfirmModal(
    'Delete Work Experience',
    `Are you sure you want to delete this experience record?`,
    async () => {
      const res = await request('/api/experience', 'DELETE', { "Email": item.Email, "Start Year": item["Start Year"] });
      if (res) {
        showToast('Experience deleted.');
        loadExperience();
      }
    }
  );
}

async function deleteEducation(index) {
  const item = educationsList[index];
  if (!item) return;
  showConfirmModal(
    'Delete Education Record',
    'Are you sure you want to delete this education record?',
    async () => {
      const res = await request('/api/education', 'DELETE', { "Email": item.Email, "Start Year": item["Start Year"] });
      if (res) {
        showToast('Education deleted.');
        loadEducation();
      }
    }
  );
}

async function deleteSkill(index) {
  const item = skillsList[index];
  if (!item) return;
  showConfirmModal(
    'Remove Skill Mapping',
    `Are you sure you want to remove the skill map for '${escapeHtml(item["Skill Name"])}'?`,
    async () => {
      if (state.profileEmail) {
        await request('/api/skill/mapping', 'DELETE', { "Email": state.profileEmail, "Skill Name": item["Skill Name"] });
      }
      const res = await request('/api/skill', 'DELETE', { "Skill Name": item["Skill Name"] });
      if (res) {
        showToast('Skill mapping removed.');
        loadSkills();
        loadStats();
      }
    }
  );
}

async function deleteCert(index) {
  const item = certsList[index];
  if (!item) return;
  showConfirmModal(
    'Delete Certification',
    `Are you sure you want to delete the certification for '${escapeHtml(item["Cert Name"])}'?`,
    async () => {
      const res = await request('/api/certification', 'DELETE', { "Cert Name": item["Cert Name"] });
      if (res) {
        showToast('Certification removed.');
        loadCerts();
      }
    }
  );
}

async function reviewTestimonial(index) {
  const item = testimonialsList[index];
  if (!item) return;
  const approveState = !item.Reviewed;
  const res = await request('/api/testimonial/review', 'PATCH', { "Email": item.Email, "Reviewed": approveState });
  if (res) {
    showToast(approveState ? 'Testimonial approved.' : 'Testimonial marked pending review.');
    loadTestimonials();
    loadStats();
  }
}

async function deleteTestimonial(index) {
  const item = testimonialsList[index];
  if (!item) return;
  showConfirmModal(
    'Delete Testimonial',
    `Are you sure you want to delete the testimonial from ${escapeHtml(item.Name)}?`,
    async () => {
      const res = await request('/api/testimonial', 'DELETE', { "Email": item.Email });
      if (res) {
        showToast('Testimonial deleted.');
        loadTestimonials();
        loadStats();
      }
    }
  );
}

async function deleteMessage(index) {
  const item = messagesList[index];
  if (!item) return;
  showConfirmModal(
    'Delete Message',
    `Are you sure you want to delete this message?`,
    async () => {
      const res = await request('/api/contact', 'DELETE', { "Email": item.Email, "Contact Date": item["Contact Date"] });
      if (res) {
        showToast('Message deleted.');
        loadMessages();
        loadStats();
      }
    }
  );
}

// Modal Helpers
function showAddExperienceModal() {
  document.getElementById('experienceForm').reset();
  document.getElementById('expModalTitle').textContent = 'Add New Work Experience';
  bootstrap.Modal.getOrCreateInstance(document.getElementById('experienceModal')).show();
}

// Inline edit helpers for Skills & Certs
function editSkill(index) {
  const item = skillsList[index];
  if (!item) return;
  document.getElementById('skill-name').value = item["Skill Name"] || '';
  document.getElementById('skill-logo').value = item["Skill Logo"] || '';
  document.getElementById('skillFormTitle').textContent = 'Edit Skill Map';
  document.getElementById('btnSubmitSkill').textContent = 'Save Changes';
  document.getElementById('btnCancelSkillEdit').classList.remove('d-none');
  document.getElementById('skill-name').focus();
}

function cancelSkillEdit() {
  document.getElementById('skillForm').reset();
  document.getElementById('skillFormTitle').textContent = 'Add a New Skill Map';
  document.getElementById('btnSubmitSkill').textContent = 'Add Skill & Map';
  document.getElementById('btnCancelSkillEdit').classList.add('d-none');
}

function editCert(index) {
  const item = certsList[index];
  if (!item) return;
  document.getElementById('cert-name').value = item["Cert Name"] || '';
  document.getElementById('cert-authority').value = item["Authority"] || '';
  document.getElementById('cert-type').value = item["Cert Type"] || '';
  document.getElementById('cert-image').value = item["Cert Logo"] || '';
  document.getElementById('cert-url').value = item["Cert Url"] || '';
  document.getElementById('certFormTitle').textContent = 'Edit Certification';
  document.getElementById('btnSubmitCert').textContent = 'Save Changes';
  document.getElementById('btnCancelCertEdit').classList.remove('d-none');
  document.getElementById('cert-name').focus();
}

function cancelCertEdit() {
  document.getElementById('certForm').reset();
  document.getElementById('certFormTitle').textContent = 'Add a New Certification';
  document.getElementById('btnSubmitCert').textContent = 'Add Certificate';
  document.getElementById('btnCancelCertEdit').classList.add('d-none');
}

// Testimonial Edit Dialog
function editTestimonial(index) {
  const item = testimonialsList[index];
  if (!item) return;
  document.getElementById('test-reviewed').value = item.Reviewed;
  document.getElementById('test-name').value = item.Name || '';
  document.getElementById('test-email').value = item.Email || '';
  document.getElementById('test-designation').value = item.Designation || '';
  document.getElementById('test-company').value = item.Company || '';
  document.getElementById('test-message').value = item.Message || '';
  bootstrap.Modal.getOrCreateInstance(document.getElementById('testimonialModal')).show();
}

// Full Text Preview Modal
function readMore(type, index) {
  const container = document.getElementById('readModalContent');
  
  if (type === 'message') {
    const data = messagesList[index];
    if (!data) return;
    container.innerHTML = `
      <div class="mb-3"><strong>Sender:</strong> ${escapeHtml(data.Name)} (<a href="mailto:${escapeHtml(data.Email)}">${escapeHtml(data.Email)}</a>)</div>
      <div class="mb-3"><strong>Details:</strong> ${escapeHtml(data.Designation)} at ${escapeHtml(data.Company)}</div>
      <div class="mb-3"><strong>Date:</strong> ${data["Contact Date"] ? new Date(data["Contact Date"]).toLocaleString() : 'N/A'}</div>
      <hr style="border-top: 1px solid var(--border-color);">
      <div class="mb-3"><strong>Message Content:</strong></div>
      <div class="p-3 rounded" style="background-color: var(--bg-primary); white-space: pre-wrap;">${escapeHtml(data.Message)}</div>
    `;
    document.getElementById('readModalTitle').textContent = 'Contact Message Details';
  } else if (type === 'testimonial') {
    const data = testimonialsList[index];
    if (!data) return;
    container.innerHTML = `
      <div class="mb-3"><strong>Author Name:</strong> ${escapeHtml(data.Name)} (<a href="mailto:${escapeHtml(data.Email)}">${escapeHtml(data.Email)}</a>)</div>
      <div class="mb-3"><strong>Organization:</strong> ${escapeHtml(data.Designation)} at ${escapeHtml(data.Company || 'Private')}</div>
      <div class="mb-3"><strong>Review Status:</strong> <span class="badge ${data.Reviewed ? 'bg-success' : 'bg-warning'}">${data.Reviewed ? 'Approved' : 'Pending'}</span></div>
      <hr style="border-top: 1px solid var(--border-color);">
      <div class="mb-3"><strong>Testimonial Content:</strong></div>
      <div class="p-3 rounded" style="background-color: var(--bg-primary); white-space: pre-wrap;">${escapeHtml(data.Message)}</div>
    `;
    document.getElementById('readModalTitle').textContent = 'Testimonial Details';
  }
  
  bootstrap.Modal.getOrCreateInstance(document.getElementById('readModal')).show();
}

function editExperience(index) {
  const item = experiencesList[index];
  if (!item) return;
  document.getElementById('exp-designation').value = item["Designation"] || '';
  document.getElementById('exp-company').value = item["Company Name"] || '';
  document.getElementById('exp-start-year').value = item["Start Year"] || '';
  document.getElementById('exp-end-year').value = item["End Year"] || '';
  document.getElementById('exp-address').value = item["Address"] || '';
  document.getElementById('exp-description').value = item["Description"] || '';
  document.getElementById('expModalTitle').textContent = 'Edit Work Experience';
  bootstrap.Modal.getOrCreateInstance(document.getElementById('experienceModal')).show();
}

function editEducation(index) {
  const item = educationsList[index];
  if (!item) return;
  document.getElementById('edu-degree').value = item["Degree"] || '';
  document.getElementById('edu-institution').value = item["University"] || '';
  document.getElementById('edu-start-year').value = item["Start Year"] || '';
  document.getElementById('edu-passing-year').value = item["Passing Year"] || '';
  document.getElementById('edu-address').value = item["Address"] || '';
  document.getElementById('eduModalTitle').textContent = 'Edit Education Record';
  bootstrap.Modal.getOrCreateInstance(document.getElementById('educationModal')).show();
}

function showAddEducationModal() {
  document.getElementById('educationForm').reset();
  document.getElementById('eduModalTitle').textContent = 'Add Education Record';
  bootstrap.Modal.getOrCreateInstance(document.getElementById('educationModal')).show();
}

// Tab switcher logic
function switchTab(tabId, btnElement) {
  document.querySelectorAll('.nav-item-btn').forEach(btn => btn.classList.remove('active'));
  btnElement.classList.add('active');

  document.querySelectorAll('.admin-tab-content').forEach(tab => tab.classList.add('d-none'));
  
  const targetTab = document.getElementById(tabId);
  targetTab.classList.remove('d-none');

  document.getElementById('currentTabTitle').textContent = btnElement.textContent.trim();
  state.currentTab = tabId;

  document.getElementById('sidebar').classList.remove('show');
}

// Toggle Mobile Sidebar
function toggleMobileSidebar() {
  document.getElementById('sidebar').classList.toggle('show');
}

// Logout
function logout() {
  state.token = '';
  localStorage.removeItem('admin_token');
  document.getElementById('loginOverlay').classList.remove('d-none');
}

// Theme Switcher Implementation
function toggleTheme() {
  const curr = document.documentElement.getAttribute('data-theme');
  const next = curr === 'light' ? 'dark' : 'light';
  document.documentElement.setAttribute('data-theme', next);
  localStorage.setItem('theme', next);
  updateThemeIcon();
}

function updateThemeIcon() {
  const theme = document.documentElement.getAttribute('data-theme') || 'dark';
  const icon = document.getElementById('themeIcon');
  if (theme === 'light') {
    icon.className = 'bi bi-moon-fill';
  } else {
    icon.className = 'bi bi-sun-fill';
  }
}
