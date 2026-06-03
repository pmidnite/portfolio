// static/script.js
// All API responses follow the APIResponse format:
//   { "success": true/false, "data": <payload>, "message": "..." }
// GET endpoints: access payload via response.data
// POST endpoints: access message via response.message

document.addEventListener('DOMContentLoaded', loadAndRenderData);
function loadAndRenderData() {
  initThemeToggle();
  fetchAndRenderAbout();
  fetchAndRenderSkill();
  fetchAndRenderEducation();
  fetchAndRenderExperience();
  fetchAndRenderTestimony();
  handleSegmentControl();
  updateFormMode('contact');
  fetchAndRenderCerts();
};


function fetchAndRenderAbout() {
  fetch('/api/about')
    .then(response => response.json())
    .then(res => {
      const data = res.data || {};
      const cls_data_mapper = {
        "short-desc": "Short Description", "long-desc": "Description",
        "current-desig": "Current Designation", "current-company": "Current Company",
        "current-birthday": "Birthday", "current-website": "Website",
        "current-city": "City", "current-degree": "Degree",
        "current-phone": "Phone", "current-email": "Email",
        "current-fact": "Self Facts", "education-summary": "Summary"
      };
      for (const cls in cls_data_mapper) {
        const elements = document.querySelectorAll('.' + cls);
        elements.forEach(el => {
          el.innerHTML = data[cls_data_mapper[cls]];
        });
      }
    })
    .catch(error => {
      console.error('Error fetching about data:', error);
    });
}

function fetchAndRenderSkill() {
  fetch('/api/skill/mapping/exact')
    .then(response => response.json())
    .then(res => {
      const skills = res.data || [];
      const dataContainer = document.getElementById('skills-content-id');
      dataContainer.innerHTML = '';

      // Define classification array for core skills (lowercase for robust mapping)
      const coreSkills = [
        'python', 'flask', 'django', 'fastapi', 'sqlalchemy', 'javascript', 'angularjs', 'html5'
      ];

      const languagesList = [];
      const toolsList = [];

      skills.forEach(item => {
        const nameLower = (item['Skill Name'] || '').toLowerCase();
        if (coreSkills.includes(nameLower)) {
          languagesList.push(item);
        } else {
          toolsList.push(item);
        }
      });

      // Helper function to render a list of cards under a container
      const createSkillsGroup = (title, items) => {
        if (items.length === 0) return;

        // Create Title Row
        const titleCol = document.createElement('div');
        titleCol.setAttribute('class', 'col-12');
        const h3 = document.createElement('h3');
        h3.setAttribute('class', 'skills-category-title');
        h3.textContent = title;
        titleCol.appendChild(h3);
        dataContainer.appendChild(titleCol);

        // Create Card Grid Container Row
        const gridRow = document.createElement('div');
        gridRow.setAttribute('class', 'row justify-content-start g-3');

        items.forEach(item => {
          const col = document.createElement('div');
          col.setAttribute('class', 'col-lg-2 col-md-3 col-sm-4 col-6');

          const card = document.createElement('div');
          card.setAttribute('class', 'skill-card');

          const img = document.createElement('img');
          img.setAttribute('src', '/static/' + item['Skill Logo']);
          img.setAttribute('alt', item['Skill Name']);
          img.setAttribute('class', 'img-fluid');

          const span = document.createElement('span');
          span.textContent = item['Skill Name'];

          card.appendChild(img);
          card.appendChild(span);
          col.appendChild(card);
          gridRow.appendChild(col);
        });

        dataContainer.appendChild(gridRow);
      };

      // Render the categorized sections
      createSkillsGroup('Languages & Frameworks', languagesList);
      createSkillsGroup('Tools, DevOps & Platforms', toolsList);
    })
    .catch(error => {
      console.error('Error fetching skills data:', error);
    });
}

function fetchAndRenderEducation() {
  fetch('/api/education')
    .then(response => response.json())
    .then(res => {
      const educations = res.data || [];
      const educationContainer = document.getElementById('education');
      educations.forEach(item => {
        const h4 = document.createElement('h4');
        const h5 = document.createElement('h5');
        const p = document.createElement('p');
        const div = document.createElement('div');
        div.setAttribute('class', 'resume-item');
        h4.innerHTML = item['Degree'];
        h5.innerHTML = item['Start Year'] + ' - ' + item['Passing Year'];
        p.innerHTML = `<em>${item['University'] + ', ' + item['Address']}</em>`;
        div.append(h4, h5, p);
        educationContainer.appendChild(div);
      });
    })
    .catch(error => {
      console.error('Error fetching education data:', error);
    });
}

function fetchAndRenderExperience() {
  fetch('/api/experience')
    .then(response => response.json())
    .then(res => {
      const experiences = res.data || [];
      const experienceContainer = document.getElementById('experience');
      experiences.forEach((item, index) => {
        const div = document.createElement('div');
        div.setAttribute('class', "col-lg-6 pb-4");
        div.setAttribute('data-aos', "fade-up");
        const innerDiv = document.createElement('div');
        innerDiv.setAttribute('class', "resume-item h-100");
        const h3 = document.createElement('h3');
        h3.setAttribute('class', "resume-title");
        const h4 = document.createElement('h4');
        const h5 = document.createElement('h5');
        const p = document.createElement('p');
        const ul = document.createElement('ul');
        h4.innerHTML = item['Designation'];
        h5.innerHTML = item['Start Year'] + ' - ' + item['End Year'];
        p.innerHTML = `<em>${item['Company Name'] + ', ' + item['Address']}</em>`;
        
        // Split text description into bullet points for a clean recruiter-friendly layout
        const descText = item["Description"] || "";
        const sentences = descText.split('.').map(s => s.trim()).filter(s => s.length > 0);
        sentences.forEach(sentence => {
          const li = document.createElement('li');
          li.innerHTML = sentence + '.';
          ul.appendChild(li);
        });

        if (index == 0) {
          h3.innerHTML = "Product Contributions &amp; Experience";
        }
        else if (index == 1) {
          h3.innerHTML = "&nbsp;";
          h3.setAttribute('style', "height: 30px");
        }
        innerDiv.append(h4, h5, p, ul);
        div.append(h3, innerDiv);
        experienceContainer.appendChild(div);
      });
    })
    .catch(error => {
      console.error('Error fetching experience data:', error);
    });
}

function fetchAndRenderTestimony() {
  fetch('/api/testimonial')
    .then(response => response.json())
    .then(res => {
      // data is null/undefined when no reviewed testimonials exist (success=false)
      const testimonials = res.data || [];
      renderSwiperTestimony(testimonials);
    })
    .catch(error => {
      console.error('Error fetching testimonials:', error);
    });

  function renderSwiperTestimony(data) {
    const swiperContainer = document.querySelector('.testimonials-slider');
    const swiperWrapper = swiperContainer.querySelector('.swiper-wrapper');
    swiperWrapper.innerHTML = '';

    data.forEach(item => {
      const div = document.createElement('div');
      const innerDiv = document.createElement('div');
      const h3 = document.createElement('h3');
      const h4 = document.createElement('h4');
      const p = document.createElement('p');
      
      const message = item['Message'] || '';
      const maxChar = 280;
      const isLong = message.length > maxChar;
      const displayText = isLong ? message.substring(0, maxChar) + '...' : message;

      h3.innerHTML = item['Name'];
      if (item['Company']) {
        h4.innerHTML = item['Designation'] + ' , ' + item['Company'];
      } else {
        h4.innerHTML = item['Designation'];
      }

      innerDiv.setAttribute('class', 'testimonial-item');
      innerDiv.setAttribute('data-aos', 'fade-up');

      p.innerHTML = `<i class="bx bxs-quote-alt-left quote-icon-left"></i>
        <span class="testimonial-text">${displayText}</span>
        <i class="bx bxs-quote-alt-right quote-icon-right"></i>`;
      
      const readMoreBtn = document.createElement('button');
      readMoreBtn.className = 'testimonial-read-more';
      readMoreBtn.textContent = 'Read More';
      readMoreBtn.addEventListener('click', (e) => {
        e.preventDefault();
        showTestimonialModal(item);
      });

      innerDiv.append(p, readMoreBtn, h3, h4);

      div.setAttribute('class', 'swiper-slide');
      div.appendChild(innerDiv);
      swiperWrapper.appendChild(div);
    });

    // Initialize Swiper if it's not initialized yet
    if (!swiperContainer.swiper) {
      swiperContainer.swiper = new Swiper('.testimonials-slider', {
        speed: 600,
        loop: true,
        autoplay: {
          delay: 5000,
          disableOnInteraction: false
        },
        slidesPerView: 'auto',
        pagination: {
          el: '.swiper-pagination',
          type: 'bullets',
          clickable: true
        },
        breakpoints: {
          320: {
            slidesPerView: 1,
            spaceBetween: 20
          },
          1200: {
            slidesPerView: 3,
            spaceBetween: 20
          }
        }
      });
    } else {
      // Update Swiper if it's already initialized
      swiperContainer.swiper.update();
    }
  }
}

function sendMessageOrContact(msgType) {
  const nameInput = document.getElementById('name');
  const emailInput = document.getElementById('email');
  const companyInput = document.getElementById('company');
  const designationInput = document.getElementById('designation');
  const messageTextarea = document.getElementsByName('message')[0];
  const submitButton = document.querySelector('.contact-form button[type="submit"]');
  const inputs = [nameInput, emailInput, companyInput, designationInput, messageTextarea];

  const formData = {
    Name: nameInput ? nameInput.value : '',
    Email: emailInput ? emailInput.value : '',
    Company: companyInput ? companyInput.value : '',
    Designation: designationInput ? designationInput.value : '',
    Message: messageTextarea ? messageTextarea.value : ''
  };

  const originalButtonText = submitButton ? submitButton.textContent : 'Submit';

  // Disable inputs and button immediately to prevent double submissions
  inputs.forEach(input => { if (input) input.disabled = true; });
  if (submitButton) {
    submitButton.disabled = true;
    submitButton.textContent = 'Submitting...';
  }

  // Immediately clear the form fields in the UI as requested
  const form = document.getElementsByClassName('contact-form')[0];
  if (form) form.reset();

  const apiUrl = '/api/' + msgType;
  fetch(apiUrl, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(formData)
  })
    .then(response => {
      if (!response.ok) {
        return response.json().then(err => { throw new Error(err.message || 'Request failed'); });
      }
      return response.json();
    })
    .then(res => {
      console.log('Message sent:', res);
      showToast(res.message, 'success');

      // Re-enable inputs
      inputs.forEach(input => { if (input) input.disabled = false; });
      if (submitButton) {
        submitButton.disabled = false;
        submitButton.textContent = originalButtonText;
      }
      
      // Reset segment button states back to default ('contact')
      const hiddenInput = document.getElementById('message-type-input');
      if (hiddenInput) {
        hiddenInput.value = 'contact';
        const buttons = document.querySelectorAll('.action-segment-control .segment-btn');
        buttons.forEach(btn => {
          if (btn.getAttribute('data-value') === 'contact') {
            btn.classList.add('active');
          } else {
            btn.classList.remove('active');
          }
        });
        updateFormMode('contact');
      }
    })
    .catch(error => {
      console.error('Error sending message:', error);
      
      // Restore the input values in case of failure so data is not lost
      inputs.forEach(input => { if (input) input.disabled = false; });
      if (submitButton) {
        submitButton.disabled = false;
        submitButton.textContent = originalButtonText;
      }

      if (nameInput) nameInput.value = formData.Name;
      if (emailInput) emailInput.value = formData.Email;
      if (companyInput) companyInput.value = formData.Company;
      if (designationInput) designationInput.value = formData.Designation;
      if (messageTextarea) messageTextarea.value = formData.Message;

      // Restore the correct mode UI state on the text elements
      const hiddenInput = document.getElementById('message-type-input');
      if (hiddenInput) {
        hiddenInput.value = msgType;
        updateFormMode(msgType);
      }

      showToast(error.message || 'Please fill the form properly and try again.', 'error');
    });
}

function updateFormMode(mode) {
  const messageLabel = document.getElementById('message-label');
  const messageTextarea = document.getElementById('message');
  const submitButton = document.querySelector('.contact-form button[type="submit"]');
  const actionHint = document.getElementById('action-hint');

  if (mode === 'testimonial') {
    if (messageLabel) messageLabel.textContent = 'Testimonial';
    if (messageTextarea) messageTextarea.setAttribute('placeholder', 'Write your testimony here...');
    if (submitButton) submitButton.textContent = 'Submit Testimonial';
    if (actionHint) actionHint.textContent = 'Your testimony will be published on the website after manual approval.';
  } else {
    if (messageLabel) messageLabel.textContent = 'Message';
    if (messageTextarea) messageTextarea.setAttribute('placeholder', 'Write within 500 characters...');
    if (submitButton) submitButton.textContent = 'Send Message';
    if (actionHint) actionHint.textContent = 'Your message will be sent directly to my email.';
  }
}

function handleSegmentControl() {
  const buttons = document.querySelectorAll('.action-segment-control .segment-btn');
  const hiddenInput = document.getElementById('message-type-input');
  if (!hiddenInput) return;

  buttons.forEach(btn => {
    btn.addEventListener('click', () => {
      buttons.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      const val = btn.getAttribute('data-value');
      hiddenInput.value = val;
      updateFormMode(val);
    });
  });
}

function fetchAndRenderCerts() {
  fetch('/api/certification')
    .then(response => response.json())
    .then(res => {
      const certs = res.data || [];
      const dataContainer = document.getElementsByClassName('portfolio-container')[0];
      if (!dataContainer) return;

      dataContainer.innerHTML = ''; // clear first
      certs.forEach(item => {
        const filter_div = document.createElement('div');
        const wrap_div = document.createElement('div');
        const anchor = document.createElement('a');
        const img = document.createElement('img');
        img.setAttribute('src', "/static/img/certs/" + `${item['Cert Logo']}`);
        img.setAttribute('title', `${item['Cert Name']}`);
        img.setAttribute('class', 'img-fluid');
        anchor.setAttribute('href', `${item['Cert Url']}`);
        anchor.setAttribute('target', '_blank');
        anchor.appendChild(img);
        wrap_div.appendChild(anchor);
        wrap_div.setAttribute('class', 'portfolio-wrap');
        filter_div.setAttribute('class', 'col-lg-4 col-md-6 portfolio-item filter-' + `${item['Cert Type']}`.toLowerCase().replace(' ', '-'));
        filter_div.appendChild(wrap_div);
        dataContainer.appendChild(filter_div);
      });

      // Initialize Isotope after items are added to the DOM and images are loaded
      if (typeof Isotope !== 'undefined') {
        let imagesLoadedCount = 0;
        const totalImages = certs.length;

        const initIso = () => {
          const portfolioIsotope = new Isotope(dataContainer, {
            itemSelector: '.portfolio-item',
            layoutMode: 'fitRows'
          });

          const portfolioFilters = document.querySelectorAll('#portfolio-flters li');
          portfolioFilters.forEach(el => {
            el.addEventListener('click', function(e) {
              e.preventDefault();
              portfolioFilters.forEach(li => li.classList.remove('filter-active'));
              this.classList.add('filter-active');
              portfolioIsotope.arrange({
                filter: this.getAttribute('data-filter')
              });
              if (typeof AOS !== 'undefined') {
                AOS.refresh();
              }
            });
          });
        };

        if (totalImages === 0) {
          initIso();
        } else {
          const checkImages = () => {
            imagesLoadedCount++;
            if (imagesLoadedCount === totalImages) {
              initIso();
            }
          };

          dataContainer.querySelectorAll('img').forEach(img => {
            if (img.complete) {
              checkImages();
            } else {
              img.addEventListener('load', checkImages);
              img.addEventListener('error', checkImages); // handle broken images
            }
          });
        }
      }
    })
    .catch(error => {
      console.error('Error fetching certifications:', error);
    });
}


document.getElementsByClassName('contact-form')[0].addEventListener('submit', function (event) {
  event.preventDefault(); // Prevent default form submission
  const hiddenInput = document.getElementById('message-type-input');
  const messageType = hiddenInput ? hiddenInput.value : 'contact';
  sendMessageOrContact(messageType);
});

// Theme Toggle Functionality
function initThemeToggle() {
  const toggleBtn = document.getElementById('theme-toggle');
  if (!toggleBtn) return;

  const toggleIcon = toggleBtn.querySelector('i');
  const toggleText = toggleBtn.querySelector('.theme-toggle-text');

  // Check saved preference or fallback to system preference
  const currentTheme = localStorage.getItem('theme') || 
    (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');

  // Set initial theme
  document.documentElement.setAttribute('data-theme', currentTheme);
  updateToggleUI(currentTheme);

  toggleBtn.addEventListener('click', () => {
    const activeTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = activeTheme === 'dark' ? 'light' : 'dark';
    
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    updateToggleUI(newTheme);
  });

  function updateToggleUI(theme) {
    if (theme === 'dark') {
      if (toggleIcon) {
        toggleIcon.className = 'bi bi-sun';
      }
      if (toggleText) {
        toggleText.textContent = 'Light Mode';
      }
    } else {
      if (toggleIcon) {
        toggleIcon.className = 'bi bi-moon-stars';
      }
      if (toggleText) {
        toggleText.textContent = 'Dark Mode';
      }
    }
  }
}

// Toast Notification System helper functions
function showToast(message, type = 'success') {
  let container = document.getElementById('toast-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toast-container';
    document.body.appendChild(container);
  }

  const toast = document.createElement('div');
  toast.className = `toast-notification toast-${type}`;
  
  let iconClass = 'bi bi-info-circle-fill';
  if (type === 'success') {
    iconClass = 'bi bi-check-circle-fill';
  } else if (type === 'error') {
    iconClass = 'bi bi-exclamation-triangle-fill';
  } else if (type === 'warning') {
    iconClass = 'bi bi-exclamation-circle-fill';
  }

  toast.innerHTML = `
    <div class="toast-content">
      <i class="${iconClass}"></i>
      <span class="toast-message">${message}</span>
    </div>
    <button class="toast-close-btn">&times;</button>
  `;

  container.appendChild(toast);

  // Trigger CSS entry animation
  setTimeout(() => {
    toast.classList.add('show');
  }, 10);

  // Auto dismiss after 4 seconds
  const autoDismiss = setTimeout(() => {
    dismissToast(toast);
  }, 4000);

  // Close button click handler
  toast.querySelector('.toast-close-btn').addEventListener('click', () => {
    clearTimeout(autoDismiss);
    dismissToast(toast);
  });
}

function dismissToast(toast) {
  toast.classList.remove('show');
  toast.classList.add('hide');
  toast.addEventListener('transitionend', () => {
    toast.remove();
  });
}

function showTestimonialModal(item) {
  let modal = document.getElementById('testimonial-modal');
  if (!modal) {
    modal = document.createElement('div');
    modal.id = 'testimonial-modal';
    modal.className = 'testimonial-modal';
    modal.innerHTML = `
      <div class="testimonial-modal-content">
        <button class="testimonial-modal-close" id="testimonial-modal-close">&times;</button>
        <div class="testimonial-modal-quote" id="testimonial-modal-quote"></div>
        <div class="testimonial-modal-author" id="testimonial-modal-author"></div>
        <div class="testimonial-modal-meta" id="testimonial-modal-meta"></div>
      </div>
    `;
    document.body.appendChild(modal);

    // Setup close listeners
    const closeBtn = modal.querySelector('#testimonial-modal-close');
    closeBtn.addEventListener('click', hideModal);
    modal.addEventListener('click', (e) => {
      if (e.target === modal) hideModal();
    });
  }

  const quote = modal.querySelector('#testimonial-modal-quote');
  const author = modal.querySelector('#testimonial-modal-author');
  const meta = modal.querySelector('#testimonial-modal-meta');

  quote.textContent = item['Message'];
  author.textContent = item['Name'];
  meta.textContent = item['Company'] ? `${item['Designation']} at ${item['Company']}` : item['Designation'];

  // Show modal
  setTimeout(() => {
    modal.classList.add('show');
  }, 10);

  function hideModal() {
    modal.classList.remove('show');
  }
}

