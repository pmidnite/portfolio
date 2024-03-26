// static/script.js
document.addEventListener('DOMContentLoaded', loadAndRenderData);
function loadAndRenderData() {
  fetchAndRenderAbout();
  fetchAndRenderSkill();
  fetchAndRenderEducation();
  fetchAndRenderExperience();
  fetchAndRenderTestimony();
  handleCheckboxSelection();
};


function fetchAndRenderAbout() {
  fetch('/api/about')
    .then(response => response.json())
    .then(data => {
      cls_data_mapper = {
        "short-desc": "Short Description", "long-desc": "Description",
        "current-desig": "Current Designation", "current-company": "Current Company",
        "current-birthday": "Birthday", "current-website": "Website",
        "current-city": "City", "current-degree": "Degree",
        "current-phone": "Phone", "current-email": "Email",
        "current-fact": "Self Facts", "education-summary": "Summary"
      };
      for (i in cls_data_mapper) {
        const elements = document.querySelectorAll('.' + i);
        elements.forEach(el => {
          el.innerHTML = data[cls_data_mapper[i]];
        });
      }
      // document.getElementsByClassName(i).innerHTML = data[0][id_data_mapper[i]];
    })
    .catch(error => {
      console.error('Error fetching data:', error);
    });
}

function fetchAndRenderSkill() {
  fetch('/api/skill/mapping/exact')
    .then(response => response.json())
    .then(skill => {
      const dataContainer = document.getElementById('skills-content-id');
      skill.forEach(item => {
        const div = document.createElement('div');
        div.innerHTML = `
            <img src="/static/${item['Skill Logo']}" alt="${item['Skill Name']}">
          `;
        div.setAttribute('class', 'skill-name-logo col-lg-2');
        div.setAttribute('title', `${item['Skill Name']}`);
        dataContainer.appendChild(div);
      })
    })
    .catch(error => {
      console.error('Error fetching data:', error);
    });
}

function fetchAndRenderEducation() {
  fetch('/api/education')
    .then(response => response.json())
    .then(education => {
      const educationContainer = document.getElementById('education');
      education.forEach(item => {
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
      })
    })
    .catch(error => {
      console.error('Error fetching data:', error);
    });
}

function fetchAndRenderExperience() {
  fetch('/api/experience')
    .then(response => response.json())
    .then(experience => {
      const experienceContainer = document.getElementById('experience');
      experience.forEach((item, index) => {
        const div = document.createElement('div');
        div.setAttribute('class', "col-lg-6");
        div.setAttribute('data-aos', "fade-up");
        const innerDiv = document.createElement('div');
        innerDiv.setAttribute('class', "resume-item")
        const h3 = document.createElement('h3');
        h3.setAttribute('class', "resume-title");
        const h4 = document.createElement('h4');
        const h5 = document.createElement('h5');
        const p = document.createElement('p');
        const ul = document.createElement('ul');
        h4.innerHTML = item['Designation'];
        h5.innerHTML = item['Start Year'] + ' - ' + item['End Year'];
        p.innerHTML = `<em>${item['Company Name'] + ', ' + item['Address']}</em>`;
        ul.innerHTML = item["Description"];
        if (index == 0) {
          h3.innerHTML = "Professional Experience";
        }
        else if (index + 1 == Math.ceil(experience.length / 2)) {
          h3.setAttribute('style', "height: 30px");
        }
        innerDiv.append(h4, h5, p, ul);
        div.append(h3, innerDiv);
        experienceContainer.appendChild(div);
      })
    })
    .catch(error => {
      console.error('Error fetching data:', error);
    });
}

function fetchAndRenderTestimony() {
  fetch('/api/testimonial')
    .then(response => response.json())
    .then(testimony => {
      renderSwiperTestimony(testimony);
    })
    .catch(error => {
      console.error('Error fetching data:', error);
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
      p.innerHTML = `<i class="bx bxs-quote-alt-left quote-icon-left"></i>
        ${item['Message']}
        <i class="bx bxs-quote-alt-right quote-icon-right"></i>`;
      h3.innerHTML = item['Name'];
      if(item['Company']){
        h4.innerHTML = item['Designation'] + ' , ' + item['Company'];
      }
      else{
        h4.innerHTML = item['Designation'];
      }
      innerDiv.setAttribute('class', 'testimonial-item');
      innerDiv.setAttribute('data-aos', 'fade-up');
      innerDiv.append(p, h3, h4);
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
  const formData = {
    Name: document.getElementById('name').value,
    Email: document.getElementById('email').value,
    Company: document.getElementById('company').value,
    Designation: document.getElementById('designation').value,
    Message: document.getElementsByName('message')[0].value
  };
  apiUrl = '/api/' + msgType;
  fetch(apiUrl, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(formData)
  })
    .then(response => {
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      return response.json();
    })
    .then(data => {
      console.log('Message sent:', data);
      alert(data.Message);
      // Optionally, you can reset the form here
    })
    .catch(error => {
      console.error('Error sending message:', error);
      alert('Please fill the form properly and try again.');
    });
}

function handleCheckboxSelection() {
  const form = document.getElementsByClassName('contact-form');
  const checkboxes = form[0].querySelectorAll('input[type="checkbox"]');
  checkboxes.forEach(checkbox => {
    checkbox.addEventListener('change', () => {
      // Uncheck all other checkboxes when one is checked
      checkboxes.forEach(otherCheckbox => {
        if (otherCheckbox !== checkbox) {
          otherCheckbox.checked = false;
        }
      });
    });
  });
}

document.getElementsByClassName('contact-form')[0].addEventListener('submit', function(event) {
  event.preventDefault(); // Prevent default form submission
  var messageType;
  const checkboxes = document.querySelectorAll('input[type="checkbox"]');
  checkboxes.forEach(checkbox => {
    if (checkbox.checked) {
      messageType = checkbox.value;
    }
  });
  sendMessageOrContact(messageType);
});
