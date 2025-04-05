// static/script.js
// Cache DOM elements
const DOM = {
  contactForm: document.getElementsByClassName('contact-form')[0],
  skillsContainer: document.getElementById('skills-content-id'),
  educationContainer: document.getElementById('education'),
  experienceContainer: document.getElementById('experience'),
  portfolioContainer: document.getElementsByClassName('portfolio-container')[0],
  testimonialsSlider: document.querySelector('.testimonials-slider'),
  // Cache form elements
  nameInput: document.getElementById('name'),
  emailInput: document.getElementById('email'),
  companyInput: document.getElementById('company'),
  designationInput: document.getElementById('designation'),
  messageInput: document.getElementsByName('message')[0],
  submitButton: document.querySelector('.contact-form button[type="submit"]')
};

// Cache for API responses with TTL (Time To Live)
const apiCache = new Map();
const CACHE_TTL = 5 * 60 * 1000; // 5 minutes

// Loading states
const loadingStates = {
  about: false,
  skills: false,
  education: false,
  experience: false,
  testimony: false,
  certs: false
};

// Debounce function for performance
function debounce(func, wait) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}

// Memoize function for expensive computations
function memoize(func) {
  const cache = new Map();
  return function (...args) {
    const key = JSON.stringify(args);
    if (cache.has(key)) {
      return cache.get(key);
    }
    const result = func.apply(this, args);
    cache.set(key, result);
    return result;
  };
}

// Intersection Observer for lazy loading
const lazyLoadObserver = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      const img = entry.target;
      img.src = img.dataset.src;
      img.removeAttribute('data-src');
      lazyLoadObserver.unobserve(img);
    }
  });
}, {
  rootMargin: '50px 0px',
  threshold: 0.1
});

document.addEventListener('DOMContentLoaded', loadAndRenderData);

async function loadAndRenderData() {
  try {
    showLoadingStates();
    
    // Load data concurrently with caching and error handling
    const results = await Promise.allSettled([
      fetchAndRenderAbout(),
      fetchAndRenderSkill(),
      fetchAndRenderEducation(),
      fetchAndRenderExperience(),
      fetchAndRenderTestimony(),
      fetchAndRenderCerts()
    ]);
    
    // Handle any failed promises
    results.forEach((result, index) => {
      if (result.status === 'rejected') {
        console.error(`Failed to load section ${index}:`, result.reason);
      }
    });
    
    handleCheckboxSelection();
  } catch (error) {
    console.error('Error loading data:', error);
  } finally {
    hideLoadingStates();
  }
}

function showLoadingStates() {
  Object.keys(loadingStates).forEach(key => {
    const container = document.querySelector(`#${key}-container`);
    if (container) {
      container.classList.add('loading');
    }
  });
}

function hideLoadingStates() {
  Object.keys(loadingStates).forEach(key => {
    const container = document.querySelector(`#${key}-container`);
    if (container) {
      container.classList.remove('loading');
    }
  });
}

async function fetchWithCache(url, options = {}) {
  const cacheKey = `${url}-${JSON.stringify(options)}`;
  const cachedData = apiCache.get(cacheKey);
  
  if (cachedData && Date.now() - cachedData.timestamp < CACHE_TTL) {
    return cachedData.data;
  }

  const response = await fetch(url, options);
  const data = await response.json();
  
  apiCache.set(cacheKey, {
    data,
    timestamp: Date.now()
  });
  
  return data;
}

// Memoized data mapper
const getDataMapper = memoize((type) => {
  const mappers = {
    about: {
      "short-desc": "Short Description", "long-desc": "Description",
      "current-desig": "Current Designation", "current-company": "Current Company",
      "current-birthday": "Birthday", "current-website": "Website",
      "current-city": "City", "current-degree": "Degree",
      "current-phone": "Phone", "current-email": "Email",
      "current-fact": "Self Facts", "education-summary": "Summary"
    }
  };
  return mappers[type] || {};
});

async function fetchAndRenderAbout() {
  try {
    const data = await fetchWithCache('/api/about');
    const mapper = getDataMapper('about');
    
    // Batch DOM updates using requestAnimationFrame
    const updates = [];
    for (const [key, value] of Object.entries(mapper)) {
      const elements = document.querySelectorAll('.' + key);
      elements.forEach(el => {
        updates.push(() => el.innerHTML = data[value]);
      });
    }
    
    requestAnimationFrame(() => {
      updates.forEach(update => update());
    });
  } catch (error) {
    console.error('Error fetching about data:', error);
  }
}

async function fetchAndRenderSkill() {
  try {
    const skill = await fetchWithCache('/api/skill/mapping/exact');
    const fragment = document.createDocumentFragment();
    
    // Create a single container div for all skills
    const skillsContainer = document.createElement('div');
    skillsContainer.className = 'skill-name-logo';
    
    skill.forEach(item => {
      const img = new Image();
      img.dataset.src = "/static/" + item['Skill Logo'];
      img.title = item['Skill Name'];
      img.className = 'lazy-load';
      
      lazyLoadObserver.observe(img);
      skillsContainer.appendChild(img);
    });
    
    fragment.appendChild(skillsContainer);
    DOM.skillsContainer.appendChild(fragment);
  } catch (error) {
    console.error('Error fetching skill data:', error);
  }
}

async function fetchAndRenderEducation() {
  try {
    const education = await fetchWithCache('/api/education');
    const fragment = document.createDocumentFragment();
    
    education.forEach(item => {
      const div = document.createElement('div');
      div.className = 'resume-item';
      
      // Use template literal for better performance
      div.innerHTML = `
        <h4>${item['Degree']}</h4>
        <h5>${item['Start Year']} - ${item['Passing Year']}</h5>
        <p><em>${item['University']}, ${item['Address']}</em></p>
      `;
      
      fragment.appendChild(div);
    });
    
    DOM.educationContainer.appendChild(fragment);
  } catch (error) {
    console.error('Error fetching education data:', error);
  }
}

async function fetchAndRenderExperience() {
  try {
    const experience = await fetchWithCache('/api/experience');
    const fragment = document.createDocumentFragment();
    
    experience.forEach((item, index) => {
      const div = document.createElement('div');
      div.className = 'col-lg-6';
      div.setAttribute('data-aos', 'fade-up');
      
      const innerDiv = document.createElement('div');
      innerDiv.className = 'resume-item';
      
      const h3 = document.createElement('h3');
      h3.className = 'resume-title';
      if (index === 0) {
        h3.textContent = 'Professional Experience';
      } else if (index + 1 === Math.ceil(experience.length / 2)) {
        h3.style.height = '30px';
      }
      
      innerDiv.innerHTML = `
        <h4>${item['Designation']}</h4>
        <h5>${item['Start Year']} - ${item['End Year']}</h5>
        <p><em>${item['Company Name']}, ${item['Address']}</em></p>
        <ul>${item['Description']}</ul>
      `;
      
      div.append(h3, innerDiv);
      fragment.appendChild(div);
    });
    
    DOM.experienceContainer.appendChild(fragment);
  } catch (error) {
    console.error('Error fetching experience data:', error);
  }
}

async function fetchAndRenderTestimony() {
  try {
    const data = await fetchWithCache("/api/testimonial");
    
    if (!data) {
      console.error("Failed to load testimonials");
      return;
    }

    // Handle both array and object responses
    const testimonyData = Array.isArray(data) ? data : Object.values(data);
    renderSwiperTestimony(testimonyData);
  } catch (error) {
    console.error("Failed to load testimonials");
  }
}

function renderSwiperTestimony(data) {
  if (!data) {
    return;
  }

  // Ensure we have an array to work with
  const testimonyArray = Array.isArray(data) ? data : Object.values(data);
  
  if (!Array.isArray(testimonyArray)) {
    return;
  }

  const swiperWrapper = DOM.testimonialsSlider.querySelector(".swiper-wrapper");
  const fragment = document.createDocumentFragment();

  testimonyArray.forEach(item => {
    if (!item || typeof item !== "object") {
      return;
    }

    const slideDiv = document.createElement("div");
    slideDiv.className = "swiper-slide";

    const testimonialDiv = document.createElement("div");
    testimonialDiv.className = "testimonial-item";
    testimonialDiv.setAttribute("data-aos", "fade-up");

    testimonialDiv.innerHTML = `
      <p>
        <i class="bx bxs-quote-alt-left quote-icon-left"></i>
        ${item.Message || ""}
        <i class="bx bxs-quote-alt-right quote-icon-right"></i>
      </p>
      <h3>${item.Name || ""}</h3>
      <h4>${item.Company ? `${item.Designation || ""}, ${item.Company}` : item.Designation || ""}</h4>
    `;

    slideDiv.appendChild(testimonialDiv);
    fragment.appendChild(slideDiv);
  });

  swiperWrapper.innerHTML = "";
  swiperWrapper.appendChild(fragment);

  if (!DOM.testimonialsSlider.swiper) {
    DOM.testimonialsSlider.swiper = new Swiper(".testimonials-slider", {
      speed: 600,
      loop: true,
      autoplay: {
        delay: 5000,
        disableOnInteraction: false
      },
      slidesPerView: "auto",
      pagination: {
        el: ".swiper-pagination",
        type: "bullets",
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
    DOM.testimonialsSlider.swiper.update();
  }
}

// Debounced form submission
const debouncedSubmit = debounce(async (msgType) => {
  try {
    // Disable the submit button
    DOM.submitButton.disabled = true;
    DOM.submitButton.textContent = 'Sending...';

    const formData = {
      Name: DOM.nameInput.value,
      Email: DOM.emailInput.value,
      Company: DOM.companyInput.value,
      Designation: DOM.designationInput.value,
      Message: DOM.messageInput.value
    };
    
    const response = await fetch('/api/' + msgType, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(formData)
    });

    if (!response.ok) {
      throw new Error('Network response was not ok');
    }

    const data = await response.json();
    console.log('Message sent:', data);
    alert(data.Message);
    DOM.contactForm.reset();
  } catch (error) {
    console.error('Error sending message:', error);
    alert('Please fill the form properly and try again.');
  } finally {
    // Re-enable the submit button
    DOM.submitButton.disabled = false;
    DOM.submitButton.textContent = 'Send It';
  }
}, 300);

async function sendMessageOrContact(msgType) {
  await debouncedSubmit(msgType);
}

function handleCheckboxSelection() {
  const checkboxes = DOM.contactForm.querySelectorAll('input[type="checkbox"]');
  checkboxes.forEach(checkbox => {
    checkbox.addEventListener('change', () => {
      checkboxes.forEach(otherCheckbox => {
        if (otherCheckbox !== checkbox) {
          otherCheckbox.checked = false;
        }
      });
    });
  });
}

async function fetchAndRenderCerts() {
  try {
    const certs = await fetchWithCache('/api/certification');
    const fragment = document.createDocumentFragment();
    
    certs.forEach(item => {
      const filterDiv = document.createElement('div');
      filterDiv.className = `col-lg-4 col-md-6 portfolio-item filter-${item['Cert Type'].toLowerCase().replace(' ', '-')}`;
      
      const wrapDiv = document.createElement('div');
      wrapDiv.className = 'portfolio-wrap';
      
      const anchor = document.createElement('a');
      anchor.href = item['Cert Url'];
      anchor.target = '_blank';
      
      const img = new Image();
      img.dataset.src = "/static/img/certs/" + item['Cert Logo'];
      img.title = item['Cert Name'];
      img.className = 'img-fluid lazy-load';
      
      lazyLoadObserver.observe(img);
      anchor.appendChild(img);
      wrapDiv.appendChild(anchor);
      filterDiv.appendChild(wrapDiv);
      fragment.appendChild(filterDiv);
    });
    
    DOM.portfolioContainer.appendChild(fragment);
  } catch (error) {
    console.error('Error fetching certification data:', error);
  }
}

// Optimized form submission handler
DOM.contactForm.addEventListener('submit', async function(event) {
  event.preventDefault();
  const checkboxes = document.querySelectorAll('input[type="checkbox"]');
  const messageType = Array.from(checkboxes).find(checkbox => checkbox.checked)?.value;
  if (messageType) {
    await sendMessageOrContact(messageType);
  }
});
